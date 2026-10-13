from __future__ import annotations
import json
from phase2.src.flync_pipeline.etape4_developpeur.agent_developpeur  import nettoyer_balises_markdown, appeler_llm 

REFERENCE_EXAMPLE = '''from flync.model.flync_4_ecu.controller import EthernetInterface, EthernetInterfaceConfig, VirtualControllerInterface
from flync.model.flync_4_ecu.internal_topology import ECUPortToControllerInterface, InternalConnectionUnion, InternalTopology, SwitchPortToControllerInterface
from flync.model.flync_4_ecu.phy import MII, BASET1
from flync.model.flync_4_ecu.port import ECUPort
from flync.model.flync_4_ecu.sockets import IPv4AddressEndpoint
from flync.model.flync_4_ecu.switch import Switch, SwitchPort
from flync.model.flync_4_metadata.metadata import BaseVersion, ECUMetadata, EmbeddedMetadata, SystemMetadata
from flync.model.flync_4_topology.system_topology import FLYNCTopology, SystemTopology
from flync.model.flync_model import FLYNCModel
from flync.model.flync_4_ecu.ecu import ECU, Controller
import sys

system_version = BaseVersion(version_schema="semver", version="0.11.0")
system_metadata = SystemMetadata(
    author="System_Architect",
    compatible_flync_version=system_version,
    release=system_version,
    oem="OEM_example",
    platform="Arch1",
)

embedded_metadata = EmbeddedMetadata(
    type="embedded",
    author="test_team",
    compatible_flync_version=system_version,
    target_system="my_system",
)

ipv4_ecu1 = IPv4AddressEndpoint(address="192.0.2.1", ipv4netmask="255.255.255.0")
virtual_iface_ecu1 = VirtualControllerInterface(name="virtual", vlanid=55, addresses=[ipv4_ecu1])
ctrl_iface_ecu1 = EthernetInterfaceConfig(
    mac_address="00:00:5e:00:53:01",
    virtual_interfaces=[virtual_iface_ecu1],
    mii_config=MII(type="mii", speed=100, mode="mac"),
)
ethernet_iface_ecu1 = EthernetInterface(
    name="eth_iface1",
    interface_config=ctrl_iface_ecu1,
)

controller_ecu1 = Controller(
    name="controller_ecu1",
    controller_metadata=embedded_metadata,
    ethernet_interfaces=[ethernet_iface_ecu1],
)

# Le port du switch est en mode MII complementaire ("phy") a l'interface
# controller ("mac") a laquelle il est relie -- regle reelle verifiee par le
# validator de connexion topologique (modes identiques = erreur).
switch_port1 = SwitchPort(
    name="sw_port1",
    silicon_port_no=1,
    default_vlan_id=1,
    mii_config=MII(type="mii", speed=100, mode="phy"),
)
switch1 = Switch(name="switch1", ports=[switch_port1], vlans=[], meta=embedded_metadata)

port_ecu1 = ECUPort(
    name="port1",
    mdi_config=BASET1(mode="base_t1", speed=100, role="slave", autonegotiation=False),
    mii_config=MII(type="mii", speed=100, mode="phy"),
)

ecu_to_controller_cnx1 = ECUPortToControllerInterface(
    type="ecu_port_to_controller_interface",
    id="1",
    ecu_port="port1",
    controller_interface="eth_iface1",
)

switch_to_controller_cnx1 = SwitchPortToControllerInterface(
    type="switch_port_to_controller_interface",
    id="2",
    switch_port="sw_port1",
    controller_interface="eth_iface1",
)

internal_topology_ecu1 = InternalTopology(
    connections=[
        InternalConnectionUnion(root=ecu_to_controller_cnx1),
        InternalConnectionUnion(root=switch_to_controller_cnx1),
    ]
)

ecu_metadata = ECUMetadata(type="ecu", author="test_team", compatible_flync_version=system_version)

ecu1 = ECU(
    name="ecu1",
    ports=[port_ecu1],
    controllers=[controller_ecu1],
    topology=internal_topology_ecu1,
    ecu_metadata=ecu_metadata,
    switches=[switch1],
)

empty_topology = FLYNCTopology(system_topology=SystemTopology(connections=[]))

flync_model = FLYNCModel(
    ecus=[ecu1],
    topology=empty_topology,
    metadata=system_metadata,
)

print(flync_model.get_all_ecus())
print('OK : construction réussie comme attendu (scénario Positive).')
sys.exit(0)
'''

_REGLES = """RÈGLES STRICTES :
1. Utilise EXACTEMENT les chemins d'import réels donnés ci-dessous. N'invente aucun chemin de module.
2. Utilise EXACTEMENT les champs et contraintes donnés (types, Field(ge=..., le=...), champs hérités inclus). N'invente aucun champ qui n'existe pas.
3. Utilise les valeurs EXACTES du scénario quand elles sont fournies (VLAN ID, adresse IP, MAC, noms...). Ne les remplace jamais par des valeurs génériques si le scénario les précise.
4. Structure le script en sections commentées ("# --- Nom de la section ---"), dans l'ordre logique de construction, exactement comme l'exemple de référence.
5. Zéro placeholder, zéro TODO, zéro "...". Si une donnée manque, utilise la valeur par défaut la plus raisonnable du champ concerné et ajoute un commentaire d'une ligne expliquant l'hypothèse.
6. Retourne UNIQUEMENT le code Python, sans balises markdown (pas de ```python, pas de ```).

7. COMPORTEMENT SELON LE TYPE DE SCÉNARIO (obligatoire, `import sys` en tête) :
   - Positive : construis directement, SANS try/except. Termine par
     `print(flync_model)` puis `sys.exit(0)`. Si une erreur réelle survient,
     laisse-la remonter telle quelle (ne l'attrape pas) -- son code de sortie
     non nul est le signal correct d'un problème à corriger.
   - Negative : injecte RÉELLEMENT la valeur fautive décrite par le scénario
     (injected_fault / description) sur le bon champ, à l'intérieur d'un
     `try/except Exception as exc` enveloppant la construction complète.
     Si une exception est levée : `print(f'OK : {type(exc).__name__}: {exc}')`
     puis `sys.exit(0)` (comportement attendu, prouvé). Si AUCUNE exception
     n'est levée : `print('INATTENDU : aucune erreur levée pour ce scénario')`
     puis `sys.exit(1)` (signale que la règle métier n'est peut-être pas
     implémentée dans le code actuel -- à remonter, pas à masquer).
   - Boundary : deux constructions successives -- une à la valeur limite
     exacte (doit réussir, `sys.exit(0)` si les deux comportements sont
     corrects), une juste au-delà (doit échouer, capturée en try/except).
     Si l'un des deux ne se comporte pas comme attendu : `sys.exit(1)`."""


def construire_prompt_construction(scenario: dict, class_context: str, feedback: str | None = None) -> str:
    scenario_json = json.dumps(scenario, ensure_ascii=False, indent=2)

    feedback_block = ""
    if feedback:
        feedback_block = (
            "\n--- RETOUR DE LA TENTATIVE PRÉCÉDENTE ---\n"
            f"{feedback}\n"
            "Corrige le script en conséquence. Si le retour précédent montre "
            "`sys.exit(1)` avec 'INATTENDU : aucune erreur levée', ce n'est PAS "
            "forcément un bug du script -- ça peut signifier que la règle "
            "métier n'existe pas dans le code réel. Dans ce cas, garde le "
            "script tel quel plutôt que d'inventer une contrainte qui n'existe pas.\n"
        )

    return f"""Tu es un générateur de scripts Python pour le framework FLYNC.

À partir du scénario et des définitions de classes ci-dessous, génère un script
Python COMPLET et DIRECTEMENT EXÉCUTABLE qui construit le modèle FLYNC correspondant
en INSTANCIANT DIRECTEMENT les objets. Ce n'est PAS un test : pas de pytest, pas
d'assertions, pas de pytest.raises -- uniquement `sys.exit(0)`/`sys.exit(1)`
pour signaler le résultat réel de l'exécution (voir règle 7).

{_REGLES}

--- EXEMPLE DE RÉFÉRENCE (style exact à reproduire sur le scénario donné plus bas) ---
{REFERENCE_EXAMPLE}

--- DÉFINITIONS DE CLASSES DISPONIBLES (imports, champs, contraintes) ---
{class_context}

--- SCÉNARIO À IMPLÉMENTER ---
{scenario_json}
{feedback_block}"""


def _squelette_mock(scenario: dict) -> str:
    """Mode mock : ne dépend d'aucun LLM. Utile pour tester le graphe et la
    persistance des scripts sans attendre une inference Ollama."""
    scenario_id = scenario.get("id", "scenario_inconnu")
    return (
        "import sys\n"
        f"print('mock : {scenario_id} -- prouve le flux (LLM absent), pas le contenu')\n"
        "sys.exit(0)\n"
    )


def generer_script_construction(
    scenario: dict,
    class_context: str,
    mode: str,
    feedback: str | None = None,
) -> str:
    if mode == "mock":
        return _squelette_mock(scenario)

    prompt = construire_prompt_construction(scenario, class_context, feedback)
    reponse = appeler_llm(prompt)
    return nettoyer_balises_markdown(reponse)


if __name__ == "__main__":
    scenario_exemple = {
        "id": "SC_DEMO_001",
        "type": "Positive",
        "description": "ECU avec un contrôleur Ethernet et un switch, VLAN 55",
    }
    class_context_exemple = (
        "VirtualControllerInterface (from flync.model.flync_4_ecu.controller import VirtualControllerInterface)\n"
        "  - name: str\n  - vlanid: int (Field(ge=0, le=4094))\n  - addresses: list[IPv4AddressEndpoint]"
    )

    prompt = construire_prompt_construction(scenario_exemple, class_context_exemple)
    print(f"Prompt généré : {len(prompt)} caractères")

    script_mock = generer_script_construction(scenario_exemple, class_context_exemple, mode="mock")
    compile(script_mock, "<mock>", "exec")
    print("Script mock : syntaxe OK")