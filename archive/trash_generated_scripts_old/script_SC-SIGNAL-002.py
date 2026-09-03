import json
import sys

# Récupération des données de la règle métier
rule_data = {
    "id": "SC-SIGNAL-002",
    "submodel": "flync_4_signal",
    "type": "Negative",
    "title": "CAN Frame DLC smaller than referenced PDU",
    "description": "A CANFrame declares DLC=4 but its referenced StandardPDU has an 8-byte payload.",
    "injected_fault": "size mismatch between Frame and PDU",
    "expected_result": "Validation fails with a size-mismatch error."
}

# Récupération du fichier JSON de la submodèle
try:
    with open('flync_4_signal.json') as f:
        submodel_data = json.load(f)
except FileNotFoundError:
    print("INATTENDU : aucune erreur levée")
    sys.exit(1)

# Vérification si la règle métier existe dans la submodèle
if 'CANFrame' in submodel_data and 'StandardPDU' in submodel_data['CANFrame']:
    can_frame = submodel_data['CANFrame']
    standard_pdu = submodel_data['StandardPDU']

    # Vérification de la taille du DLC et de la taille du PDU
    if can_frame['DLC'] < len(standard_pdu):
        print("Erreur : La taille du DLC est inférieure à celle du PDU")
    else:
        print("OK : La taille du DLC est supérieure ou égale à celle du PDU")

else:
    print("INATTENDU : aucune erreur levée")