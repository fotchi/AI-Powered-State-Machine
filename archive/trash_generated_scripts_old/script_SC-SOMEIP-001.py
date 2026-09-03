# SC-SOMEIP-001 : Client subscribes to an offered Eventgroup

import sys

def test_SC_SOMEIP_001():
    # Récupération des types de données nécessaires pour le scénario
    SOMEIPSDDeployment = "flync_4_someip.SOMEIPSDDeployment"
    SOMEIPServiceDeployment = "flync_4_someip.SOMEIPServiceDeployment"
    SOMEIPEventgroupMulticastConfig = "flync_4_someip.SOMEIPEventgroupMulticastConfig"

    # Vérification de la présence des types de données nécessaires
    if not hasattr(sys.modules['flync_4_someip'], 'SOMEIPSDDeployment'):
        print("INATTENDU : SOMEIPSDDeployment n'existe pas dans le code réel")
        sys.exit(1)
    elif not hasattr(sys.modules['flync_4_someip'], 'SOMEIPServiceDeployment'):
        print("INATTENDU : SOMEIPServiceDeployment n'existe pas dans le code réel")
        sys.exit(1)
    elif not hasattr(sys.modules['flync_4_someip'], 'SOMEIPEventgroupMulticastConfig'):
        print("INATTENDU : SOMEIPEventgroupMulticastConfig n'existe pas dans le code réel")
        sys.exit(1)

test_SC_SOMEIP_001()