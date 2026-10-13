
from __future__ import annotations

import argparse
import ast
import concurrent.futures
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

from phase2.src.flync_pipeline.etape1_discovery.kb_pointers import FLYNC_KB, KBPointers


# ---------------------------------------------------------------------------
# Schema de sortie de l'agent (contrat inter-agents, cf. §4 du cahier des charges :
# "chaque echange entre agents doit etre un objet structure et valide")
# ---------------------------------------------------------------------------

_ENUM_BASE_NAMES = {"Enum", "IntEnum", "StrEnum", "Flag", "IntFlag"}


@dataclass
class FieldInfo:
    name: str
    type_str: str
    required: bool
    default_str: Optional[str] = None


@dataclass
class ValidatorInfo:
    method_name: str
    kind: str  # "field_validator" | "model_validator"
    targets: list[str] = field(default_factory=list)
    mode: Optional[str] = None


@dataclass
class ClassInfo:
    name: str
    bases: list[str]
    fields: list[FieldInfo]
    validators: list[ValidatorInfo]
    file: str
    module: str = ""  # ex: "flync_4_signal" -- necessaire pour generer un vrai import
    docstring: Optional[str] = None
    is_enum: bool = False
    enum_members: list[str] = field(default_factory=list)


@dataclass
class ModuleAnalysis:
    module_name: str
    key: Optional[str]
    public_api: list[str]
    classes: dict[str, ClassInfo]
    cross_module_imports: dict[str, list[str]]  # module source -> noms importes

    @property
    def n_classes(self) -> int:
        return len(self.classes)

    @property
    def n_validators(self) -> int:
        return sum(len(c.validators) for c in self.classes.values())

    @property
    def n_enums(self) -> int:
        return sum(1 for c in self.classes.values() if c.is_enum)


@dataclass
class KBAnalysisReport:
    modules: dict[str, ModuleAnalysis] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    @property
    def total_classes(self) -> int:
        return sum(m.n_classes for m in self.modules.values())

    @property
    def total_validators(self) -> int:
        return sum(m.n_validators for m in self.modules.values())

    def all_classes(self) -> list[ClassInfo]:
        """Aplati toutes les classes de tous les modules en une seule liste
        (equivalent de `KnowledgeBase.all_classes()` de l'ancien
        `module_analyzer.py`), consommee par `kb_retriever.py` et
        `scenario_verifier.py`."""
        result: list[ClassInfo] = []
        for m in self.modules.values():
            result.extend(m.classes.values())
        return result

    def build_class_lookup(self) -> dict[str, ClassInfo]:
        """Construit un dict nom-de-classe -> ClassInfo. En cas de collision
        de nom entre deux modules, le premier rencontre l'emporte et la
        collision est journalisee (utile pour `scenario_verifier.py`,
        matching EXACT/ALIAS)."""
        lookup: dict[str, ClassInfo] = {}
        for m in self.modules.values():
            for name, info in m.classes.items():
                if name not in lookup:
                    lookup[name] = info
                elif lookup[name].module != info.module:
                    print(
                        f"[agent-lecteur] Avertissement: collision de nom de "
                        f"classe '{name}' entre modules '{lookup[name].module}' "
                        f"et '{info.module}'."
                    )
        return lookup


# ---------------------------------------------------------------------------
# Fonctions d'extraction AST -- top-level (aucune ne depend de `self`),
# reutilisees a la fois par le worker parallele et par l'enveloppe d'instance.
# ---------------------------------------------------------------------------

def _unparse(node) -> Optional[str]:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return "<?>"


def _extract_fields(class_node: ast.ClassDef) -> list[FieldInfo]:
    fields = []
    for stmt in class_node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            name = stmt.target.id
            if name.startswith("_"):
                continue
            type_str = _unparse(stmt.annotation) or "Any"
            default_str = _unparse(stmt.value)
            required = True
            if stmt.value is not None:
                if isinstance(stmt.value, ast.Call) and getattr(stmt.value.func, "id", "") == "Field":
                    kw_names = {kw.arg for kw in stmt.value.keywords}
                    if "default" in kw_names or "default_factory" in kw_names:
                        required = False
                else:
                    required = False
            fields.append(FieldInfo(name, type_str, required, default_str))
    return fields


def _extract_enum_members(class_node: ast.ClassDef) -> list[str]:
    """Membres d'un Enum : assignations simples (pas AnnAssign) au
    premier niveau du corps de la classe, ex. `UINT16 = "uint16"`."""
    members = []
    for stmt in class_node.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
            target = stmt.targets[0]
            if isinstance(target, ast.Name) and not target.id.startswith("_"):
                members.append(target.id)
    return members


def _extract_validators(class_node: ast.ClassDef) -> list[ValidatorInfo]:
    validators = []
    for stmt in class_node.body:
        if not isinstance(stmt, ast.FunctionDef):
            continue
        for dec in stmt.decorator_list:
            dec_call = dec if isinstance(dec, ast.Call) else None
            dec_name = None
            if isinstance(dec, ast.Name):
                dec_name = dec.id
            elif isinstance(dec, ast.Attribute):
                dec_name = dec.attr
            elif dec_call is not None:
                dec_name = getattr(dec_call.func, "id", None) or getattr(dec_call.func, "attr", None)

            if dec_name == "field_validator":
                targets = [a.value for a in (dec_call.args if dec_call else []) if isinstance(a, ast.Constant)]
                validators.append(ValidatorInfo(stmt.name, "field_validator", targets))
            elif dec_name == "model_validator":
                mode = None
                if dec_call is not None:
                    for kw in dec_call.keywords:
                        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                            mode = str(kw.value.value)
                validators.append(ValidatorInfo(stmt.name, "model_validator", mode=mode))
    return validators


def _extract_bases(class_node: ast.ClassDef) -> list[str]:
    bases = []
    for b in class_node.bases:
        if isinstance(b, ast.Name):
            bases.append(b.id)
        elif isinstance(b, ast.Attribute):
            bases.append(b.attr)
    return bases


def _is_enum(class_name: str, bases: list[str]) -> bool:
    if any(b in _ENUM_BASE_NAMES for b in bases):
        return True
    # repli heuristique : herite d'une base intermediaire non resolue
    # (ex: `class SignalDataType(MyIntEnum)`) mais le nom de la base
    # se termine quand meme par un mot-cle Enum connu.
    if any(b.endswith(tuple(_ENUM_BASE_NAMES)) for b in bases):
        return True
    return False


# ---------------------------------------------------------------------------
# Worker top-level picklable -- unite de travail du pool de processus.
# Ne depend d'AUCUN etat d'instance : uniquement des parametres recus.
# ---------------------------------------------------------------------------

def _analyze_one_module_worker(module_dir: str, module_name: str) -> ModuleAnalysis:
    """
    Analyse UN module, independamment de tout autre module analyse dans le
    meme run. Fonction pure et picklable, soumise au pool de processus (ou
    de threads en repli) par `AgentLecteurAnalyste.run`.

    :param module_dir: chemin absolu du dossier du module (str, picklable).
    :param module_name: nom logique du module (ex: "flync_4_someip").
    :return: ModuleAnalysis complet pour ce module.
    :raises FileNotFoundError: si le dossier du module n'existe pas.
    """
    module_path = Path(module_dir)
    if not module_path.is_dir():
        raise FileNotFoundError(f"Module introuvable: {module_path}")

    classes: dict[str, ClassInfo] = {}
    cross_imports: dict[str, list[str]] = {}
    key: Optional[str] = None
    public_api: list[str] = []

    for py_file in sorted(module_path.glob("*.py")):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and "flync.model.flync_4_" in node.module:
                if module_name not in node.module:
                    names = [a.name for a in node.names]
                    cross_imports.setdefault(node.module, [])
                    for n in names:
                        if n not in cross_imports[node.module]:
                            cross_imports[node.module].append(n)

            if py_file.name == "__init__.py" and isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == "KEY" and isinstance(node.value, ast.Constant):
                        key = str(node.value.value)
                    if isinstance(t, ast.Name) and t.id == "__all__" and isinstance(node.value, (ast.List, ast.Tuple)):
                        public_api = [e.value for e in node.value.elts if isinstance(e, ast.Constant)]

            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node)
                bases = _extract_bases(node)
                is_enum = _is_enum(node.name, bases)
                classes[node.name] = ClassInfo(
                    name=node.name,
                    bases=bases,
                    fields=[] if is_enum else _extract_fields(node),
                    validators=_extract_validators(node),
                    file=py_file.name,
                    module=module_name,
                    docstring=(doc.strip().split("\n")[0] if doc else None),
                    is_enum=is_enum,
                    enum_members=_extract_enum_members(node) if is_enum else [],
                )

    return ModuleAnalysis(
        module_name=module_name,
        key=key,
        public_api=public_api,
        classes=classes,
        cross_module_imports=cross_imports,
    )


# ---------------------------------------------------------------------------
# L'Agent lui-meme
# ---------------------------------------------------------------------------

class AgentLecteurAnalyste:
    """Agent autonome : connexion KB -> decouverte de modules -> analyse
    parallele independante de chacun -> rapport structure. Aucune etape ne
    necessite d'intervention externe module par module."""

    def __init__(self, pointers: KBPointers = FLYNC_KB, repo_cache_dir: Optional[str] = None):
        self.pointers = pointers
        self.repo_dir = Path(repo_cache_dir or pointers.local_cache_dir)

    # -- connexion KB ---------------------------------------------------

    def _local_phase1_data_root(self) -> Optional[Path]:
        """phase1/data/flync_source (model/, telecharge par
        phase1/graph_builder/download_source.py via GITHUB_TOKEN) +
        phase1/data/flync_core (core/, meme mecanisme). Si le Scenario
        Agent a deja telecharge les deux, on evite un clone git complet
        et redondant : simple copie de fichiers locaux. Retourne None
        (et laisse _sync_repo() se rabattre sur git) si l'un des deux
        est absent ou vide -- ex: le Scenario Agent n'a encore jamais
        tourne en pipeline complet sur cette machine."""
        repo_root = Path(__file__).resolve().parents[4]
        flync_source = repo_root / "phase1" / "data" / "flync_source"
        flync_core = repo_root / "phase1" / "data" / "flync_core"
        if not flync_source.is_dir() or not any(flync_source.iterdir()):
            return None
        if not (flync_core / "core").is_dir():
            return None
        return repo_root

    def _build_repo_dir_from_phase1_data(self, repo_root: Path) -> None:
        """Assemble self.repo_dir/src/flync/{model,core} a partir des
        donnees deja telechargees par le Scenario Agent -- copie de
        fichiers locale, aucun appel reseau.

        flync/__init__.py et flync/model/__init__.py sont laisses vides :
        chaque script genere importe directement depuis un sous-module
        (ex: `from flync.model.flync_4_bus.can_bus import CANBus`), jamais
        via le package flync/flync.model lui-meme -- leur contenu reel
        (qui re-exporte des domaines et flync_model.FLYNCModel, jamais
        telecharges par le Scenario Agent) n'est donc jamais execute.
        Seul core/ doit avoir son VRAI contenu : chaque classe du model
        importe reellement depuis flync.core.* (validators, base models,
        datatypes) a l'execution.

        self.repo_dir est un cache PARTAGE (~/.flync_kb_cache par defaut) --
        si deux runs se chevauchent (deux generations lancees a quelques
        secondes d'ecart, ou ce module rebati pendant qu'un run precedent
        est encore en train d'executer un script), l'ancienne version
        copiait fichier par fichier DIRECTEMENT dans flync_root : un import
        concurrent pouvait alors tomber en plein milieu de la copie et voir
        un flync/core/ partiellement écrit (d'ou des `ImportError: cannot
        import name 'core' from 'flync'` ou `'flync.core' is not a
        package` vus en usage reel). On construit maintenant l'arbre
        complet dans un dossier temporaire ISOLE, puis on ne fait qu'UN
        SEUL rename() pour le faire apparaitre -- un lecteur concurrent
        voit soit l'ancien flync_root complet, soit le nouveau complet,
        jamais un etat intermediaire."""
        flync_source = repo_root / "phase1" / "data" / "flync_source"
        flync_core = repo_root / "phase1" / "data" / "flync_core"
        flync_root = self.repo_dir / "src" / "flync"

        tmp_dir = Path(tempfile.mkdtemp(prefix=".flync_build_", dir=str(self.repo_dir.parent)))
        try:
            tmp_flync = tmp_dir / "flync"
            tmp_model = tmp_flync / "model"
            tmp_model.mkdir(parents=True, exist_ok=True)
            (tmp_flync / "__init__.py").touch()
            (tmp_model / "__init__.py").touch()
            for domain_dir in flync_source.iterdir():
                if domain_dir.is_dir() and domain_dir.name.startswith("flync_4_"):
                    shutil.copytree(domain_dir, tmp_model / domain_dir.name)
            shutil.copytree(flync_core / "core", tmp_flync / "core")

            flync_root.parent.mkdir(parents=True, exist_ok=True)
            old_flync = None
            if flync_root.exists():
                # Rename the old tree aside first (still fully valid, just
                # under a different name) rather than deleting it before
                # the new one is in place -- there is then never a moment
                # where "flync" doesn't exist at all for a concurrent import.
                old_flync = tmp_dir / "flync_previous"
                os.rename(str(flync_root), str(old_flync))
            os.rename(str(tmp_flync), str(flync_root))
            if old_flync is not None:
                shutil.rmtree(old_flync, ignore_errors=True)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def _sync_repo(self) -> None:
        model_root = self.repo_dir / self.pointers.model_root_path

        phase1_data_root = self._local_phase1_data_root()
        if phase1_data_root is not None:
            print("[agent-lecteur] Donnees deja telechargees par le Scenario Agent "
                  "trouvees localement -> assemblage sans clone git.")
            self._build_repo_dir_from_phase1_data(phase1_data_root)
            return

        print("[agent-lecteur] Donnees locales du Scenario Agent introuvables/incompletes "
              "-> repli sur le clonage git complet.")
        is_broken_clone = (self.repo_dir / ".git").exists() and not model_root.is_dir()

        if is_broken_clone:
            print(f"[agent-lecteur] Clone incomplet detecte dans {self.repo_dir} -> nettoyage et re-clonage.")
            shutil.rmtree(self.repo_dir, ignore_errors=True)

        if not (self.repo_dir / ".git").exists():
            print(f"[agent-lecteur] Clonage de {self.pointers.repo_url} ...")
            clone_result = subprocess.run(
                ["git", "-c", "core.longpaths=true", "clone", "--depth", "1",
                 "--branch", self.pointers.branch, self.pointers.repo_url, str(self.repo_dir)],
                capture_output=True, text=True,
            )
            if clone_result.returncode != 0:
                raise RuntimeError(
                    f"Echec du clonage de {self.pointers.repo_url} (code {clone_result.returncode}).\n"
                    f"Sortie git : {clone_result.stderr.strip()}\n"
                    f"Si l'erreur mentionne un chemin trop long : active le support des chemins longs "
                    f"avec 'git config --system core.longpaths true' (admin), ou clone dans un dossier "
                    f"plus court (ex: 'C:\\flync_kb_cache') plutot que sous un dossier OneDrive imbrique."
                )
        else:
            print("[agent-lecteur] Depot deja present -> synchronisation ...")
            result = subprocess.run(
                ["git", "-C", str(self.repo_dir), "pull", "origin", self.pointers.branch, "--ff-only"],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                print(f"[agent-lecteur] Avertissement: pull echoue ({result.stderr.strip()}) "
                      f"-> on continue avec le contenu local existant.")

        if not model_root.is_dir():
            raise RuntimeError(
                f"Echec de synchronisation KB : {model_root} n'existe pas apres clone/pull.\n"
                f"Verifier l'acces reseau a {self.pointers.repo_url} et la branche '{self.pointers.branch}'.\n"
                f"Cause frequente sous Windows : chemin de destination trop long "
                f"(ex: sous un dossier OneDrive imbrique) depassant MAX_PATH (260 car.) -- "
                f"essayer 'git config --system core.longpaths true', ou utiliser un "
                f"repo_cache_dir plus court (ex: tempfile.gettempdir())."
            )

    def _discover_modules(self) -> list[str]:
        model_root = self.repo_dir / self.pointers.model_root_path
        modules = [
            entry.name for entry in sorted(model_root.iterdir())
            if entry.is_dir() and (entry / "__init__.py").exists()
        ]
        print(f"[agent-lecteur] {len(modules)} module(s) decouvert(s): {modules}")
        return modules

    # -- analyse independante d'un module (enveloppe d'instance, compatibilite) --

    def analyze_one_module(self, module_name: str) -> ModuleAnalysis:
        """Analyse UN module. Enveloppe fine autour du worker top-level,
        conservee pour compatibilite avec du code appelant existant qui
        invoquerait `agent.analyze_one_module(name)` directement (hors pool
        de processus)."""
        module_dir = self.repo_dir / self.pointers.model_root_path / module_name
        return _analyze_one_module_worker(str(module_dir), module_name)

    # -- execution parallele ---------------------------------------------

    def _run_parallel(
        self,
        modules: list[str],
        model_root: Path,
        max_workers: int,
        executor_cls,
    ) -> dict[str, Union[ModuleAnalysis, Exception]]:
        results: dict[str, Union[ModuleAnalysis, Exception]] = {}
        with executor_cls(max_workers=max_workers) as executor:
            future_to_module = {
                executor.submit(_analyze_one_module_worker, str(model_root / m), m): m
                for m in modules
            }
            for future in concurrent.futures.as_completed(future_to_module):
                module_name = future_to_module[future]
                print(f"[agent-lecteur] Analyse terminee -> {module_name}")
                try:
                    results[module_name] = future.result()
                except Exception as exc:
                    results[module_name] = exc
        return results

    # -- point d'entree public de l'agent --------------------------------

    def run(
        self,
        target_modules: Optional[list[str]] = None,
        max_workers: Optional[int] = None,
    ) -> KBAnalysisReport:
        """
        Execute l'agent de bout en bout. Si target_modules est None,
        analyse TOUS les modules decouverts dynamiquement (comportement
        par defaut, requis par le cahier des charges).

        L'analyse de chaque module est parallelisee via
        `ProcessPoolExecutor` (un processus par module). En cas d'echec du
        pool de processus (sandboxing, environnement sans fork/spawn
        disponible), repli automatique sur `ThreadPoolExecutor` afin de
        garantir la completion du run.

        :param target_modules: sous-ensemble de modules a analyser, ou None
            pour analyser tous les modules decouverts.
        :param max_workers: nombre de workers paralleles ; par defaut,
            min(nombre de modules, nombre de coeurs CPU disponibles).
        """
        self._sync_repo()
        modules = target_modules or self._discover_modules()
        model_root = self.repo_dir / self.pointers.model_root_path

        effective_workers = max_workers or min(len(modules), (os.cpu_count() or 4))
        effective_workers = max(1, effective_workers)

        print(f"[agent-lecteur] Analyse parallele de {len(modules)} module(s) "
              f"avec {effective_workers} worker(s)...")

        try:
            raw_results = self._run_parallel(
                modules, model_root, effective_workers, concurrent.futures.ProcessPoolExecutor
            )
        except (OSError, PermissionError, RuntimeError) as exc:
            print(f"[agent-lecteur] ProcessPoolExecutor indisponible ({exc}), "
                  f"repli sur ThreadPoolExecutor.")
            raw_results = self._run_parallel(
                modules, model_root, effective_workers, concurrent.futures.ThreadPoolExecutor
            )

        report = KBAnalysisReport()
        for module_name, outcome in raw_results.items():
            if isinstance(outcome, Exception):
                print(f"[agent-lecteur]   ERREUR ({module_name}): {outcome}")
                report.errors[module_name] = str(outcome)
            else:
                report.modules[module_name] = outcome

        return report

    # -- serialisation des resultats --------------------------------------

    def write_reports(self, report: KBAnalysisReport, output_dir: str = "./agent_lecteur_out") -> Path:
        out = Path(output_dir)
        out.mkdir(exist_ok=True)

        index_lines = [
            "# Agent Lecteur/Analyste — rapport d'analyse indépendante",
            "",
            f"{len(report.modules)}/{len(report.modules) + len(report.errors)} module(s) analysé(s) avec succès.",
            "",
            "| Module | Classes | dont Enum | Validators | API publique |",
            "|---|---|---|---|---|",
        ]

        for name, m in sorted(report.modules.items()):
            module_dir = out / name
            module_dir.mkdir(exist_ok=True)
            (module_dir / "ANALYSE.md").write_text(self._render_module_report(m), encoding="utf-8")
            api = ", ".join(f"`{a}`" for a in m.public_api) if m.public_api else "-"
            index_lines.append(f"| `{name}` | {m.n_classes} | {m.n_enums} | {m.n_validators} | {api} |")

        for name, err in report.errors.items():
            index_lines.append(f"| `{name}` | ❌ {err} | - | - | - |")

        index_lines += [
            "",
            f"**Total : {report.total_classes} classes, {report.total_validators} validators.**",
        ]

        (out / "INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")
        return out

    @staticmethod
    def _render_module_report(m: ModuleAnalysis) -> str:
        lines = [f"# `{m.module_name}` — analyse indépendante", "", f"`KEY` = `{m.key}` | API publique = `{m.public_api}`", ""]
        for name, info in m.classes.items():
            bases = f" (hérite de: {', '.join(info.bases)})" if info.bases else ""
            kind = " — **Enum**" if info.is_enum else ""
            lines.append(f"### `{name}`{bases}{kind}")
            if info.docstring:
                lines.append(f"> {info.docstring}")
            if info.is_enum:
                lines.append(f"- membres : {', '.join(info.enum_members) or '(aucun détecté)'}")
            for f_ in info.fields:
                req = "obligatoire" if f_.required else f"optionnel (défaut: {f_.default_str})"
                lines.append(f"- `{f_.name}: {f_.type_str}` — {req}")
            for v in info.validators:
                lines.append(f"- validator `{v.method_name}` ({v.kind}, cible: {v.targets or v.mode})")
            lines.append("")
        if m.cross_module_imports:
            lines.append("### Dépendances croisées")
            for mod, names in m.cross_module_imports.items():
                lines.append(f"- `{mod}` -> {', '.join(names)}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Exécution autonome — l'agent tourne seul, aucune intervention manuelle
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Agent Lecteur/Analyste GitHub (autonome, parallèle).")
    parser.add_argument("--modules", nargs="*", default=None,
                         help="Sous-ensemble de modules à analyser. Omis = TOUS les modules découverts dynamiquement.")
    parser.add_argument("--output-dir", default="./agent_lecteur_out")
    parser.add_argument("--max-workers", type=int, default=None,
                         help="Nombre de processus paralleles. Par defaut: min(nb_modules, nb_coeurs_cpu).")
    args = parser.parse_args()

    agent = AgentLecteurAnalyste()
    report = agent.run(target_modules=args.modules, max_workers=args.max_workers)
    out = agent.write_reports(report, args.output_dir)

    print(f"\n[agent-lecteur] Terminé. {len(report.modules)} module(s) analysé(s), "
          f"{report.total_classes} classes, {report.total_validators} validators.")
    print(f"[agent-lecteur] Rapports -> {out}")
    return 0 if not report.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())