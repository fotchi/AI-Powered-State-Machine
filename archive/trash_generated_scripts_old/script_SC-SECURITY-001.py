import json

try:
    with open('flync_4_security.json') as f:
        data = json.load(f)
except FileNotFoundError:
    print("Erreur : Le fichier 'flync_4_security.json' n'existe pas.")
    # Vous pouvez choisir de continuer à exécuter le script ou non
    sys.exit(1)  # Si vous souhaitez arrêter le script