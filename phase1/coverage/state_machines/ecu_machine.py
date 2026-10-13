"""
Transcription directe de la proposition de State Machine (voir doc
"FLYNC Test State Architecture") pour l'objet ECU -- Niveau 2 (états) +
Niveau 3 (coverage_tag pour le Test Mutation Engine).

Chaque état a :
- on_pass  : état suivant si la validation réussit
- on_fail  : état d'échec si elle échoue
- coverage_tag : identifiant utilisé par le matcher pour savoir si un
  scénario existant "couvre" ce cas -- absent = état purement structurel,
  pas un point de test (ex: le début/fin de la chaîne).
"""

ECU_MACHINE = {
    "id": "ECU_MACHINE",
    "phase1_module": "ecu",
    "states": {
        "CREATE_ECU": {
            "on_pass": "VALIDATE_ECU_FIELDS",
            "on_fail": "FAIL_ECU",
        },
        "VALIDATE_ECU_FIELDS": {
            "on_pass": "RESOLVE_ECU_REFS",
            "on_fail": "FAIL_REQUIRED",
            "coverage_tag": "ecu.fields",
        },
        "RESOLVE_ECU_REFS": {
            "on_pass": "DETERMINE_ECU_TYPE",
            "on_fail": "FAIL_REFERENCE",
            "coverage_tag": "ecu.refs",
        },
        "DETERMINE_ECU_TYPE": {
            "on_pass": "CREATE_DEPENDENCIES",
            "on_fail": "FAIL_FORMAT",
            "coverage_tag": "ecu.type",
        },
        "CREATE_DEPENDENCIES": {
            "on_pass": "ECU_READY",
            "on_fail": "FAIL_DEPENDENCY",
            "coverage_tag": "ecu.deps",
        },
    },
    "terminal_pass": "ECU_READY",
}