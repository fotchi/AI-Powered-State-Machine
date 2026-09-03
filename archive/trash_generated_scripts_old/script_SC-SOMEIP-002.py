# Importation des bibliothèques nécessaires
import sys

# Définition de la fonction pour tester la règle métier
def test_SC_SOMEIP_002():
    # Récupération du service SOMEIP
    someip_service = get_someip_service()

    # Vérification si l'Eventgroup référencé existe bien dans le service
    eventgroup_id = "non_existent_eventgroup"
    if eventgroup_id not in someip_service.eventgroups:
        print("Validation failed: consumer references an undefined Eventgroup.")
        sys.exit(1)

# Exécution de la fonction pour tester la règle métier
test_SC_SOMEIP_002()