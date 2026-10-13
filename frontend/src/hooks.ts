import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { getScenarios, getScripts, type Scenario, type GeneratedScript } from "./api";

// --- Cache partagé des données API (le State Manager) ---------------------

export function useScenarios(runId?: string) {
  return useQuery({
    queryKey: ["scenarios", runId ?? "all"],
    queryFn: () => getScenarios(runId),
  });
}

export function useScripts(runId?: string) {
  return useQuery({
    queryKey: ["scripts", runId ?? "all"],
    queryFn: () => getScripts(runId),
  });
}

// --- Sélection de scénario partagée entre écrans (remplace le
// localStorage lu/écrit à la main dans StateMachine/ScenarioDetails/
// ScenarioHistory) ----------------------------------------------------------

const SELECTED_SCENARIO_KEY = "flync_selected_scenario_id";
const listeners = new Set<() => void>();

export function useSelectedScenarioId(): [string | null, (id: string) => void] {
  const [id, setId] = useState<string | null>(() => window.localStorage.getItem(SELECTED_SCENARIO_KEY));

  useEffect(() => {
    const listener = () => setId(window.localStorage.getItem(SELECTED_SCENARIO_KEY));
    listeners.add(listener);
    return () => { listeners.delete(listener); };
  }, []);

  const select = (newId: string) => {
    window.localStorage.setItem(SELECTED_SCENARIO_KEY, newId);
    listeners.forEach((listener) => listener());
  };

  return [id, select];
}

/** Résout l'id sélectionné vers le vrai objet Scenario, avec fallback sur
 * le premier de la liste -- même logique que chaque écran réimplémentait
 * avant, centralisée ici. */
export function useSelectedScenario(): { scenario: Scenario | undefined; scenarios: Scenario[]; isLoading: boolean } {
  const { data: scenarios = [], isLoading } = useScenarios();
  const [selectedId] = useSelectedScenarioId();
  const scenario = scenarios.find((s) => s.id === selectedId) ?? scenarios[0];
  return { scenario, scenarios, isLoading };
}

// --- Correspondance script <-> scénario (même logique qu'avant, mais
// centralisée une seule fois au lieu d'être dupliquée dans 3 écrans) -------

// Bug corrigé : le filename est `script_<id en snake_case>_<type>.py` où
// <type> est "positive" ou "negative" SEUL -- jamais "neg_negative". Un id
// de scénario qui se termine lui-même par "-NEG" (ex: "SC-BUS-005-NEG")
// produit un filename du style "script_sc_bus_005_neg_negative.py" ;
// retirer "_neg_negative$" en un seul bloc effaçait aussi le "-NEG" propre
// à l'id du scénario, donc l'id reconstruit ne correspondait plus jamais
// à l'id réel pour ces scénarios-là. Ne retirer que le suffixe de type.
export function scenarioIdFromScriptId(scriptId: string): string {
  return scriptId
    .replace(/^script_/, "")
    .replace(/_negative$/, "")
    .replace(/_positive$/, "")
    .toUpperCase()
    .replace(/_/g, "-");
}

export function scriptStatusFor(scenarioId: string, scripts: GeneratedScript[]): "pending" | "success" | "failed" {
  const script = scripts.find((s) => scenarioIdFromScriptId(s.id) === scenarioId);
  if (!script || script.execution_success === null || script.execution_success === undefined) return "pending";
  return script.execution_success ? "success" : "failed";
}