# SCÉNARIO À IMPLÉMENTER
{
  "id": "SC-SIGNAL-001",
  "submodel": "flync_4_signal",
  "type": "Positive",
  "title": "Valid CAN Frame with matching PDU size",
  "description": "A CANFrame declares a DLC of 8 bytes and references a StandardPDU whose payload is also 8 bytes.",
  "injected_fault": null,
  "expected_result": "Model validation succeeds with no errors."
}

# RETOUR DE LA TENTATIVE PRÉCÉDENTE
try:
    # Code pour tester le scénario
except Exception as e:
    print(f"Erreur : {e}")