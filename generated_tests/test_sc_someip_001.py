"""
Scénario SC-SOMEIP-001 (Positive)
Client subscribes to an offered Eventgroup

A SOMEIPServiceConsumer sends Subscribe after receiving a matching Offer via SD, for an Eventgroup declared on the provider.
"""
import pytest
# from flync.model.<module> import SOMEIPServiceConsumer  # TODO: ajuster le chemin exact


def test_sc_someip_001():
    someipserviceconsumer = SOMEIPServiceConsumer(
        # TODO: fournir une instance de type DeploymentTypes (non résolu automatiquement)
        deployment_type=None,
        # TODO: fournir une instance de type Annotated[int, Reference(source='_service_ref')] (non résolu automatiquement)
        service=None,
        # TODO: fournir une instance de type Annotated[int, Field(gt=0, lt=65535)] (non résolu automatiquement)
        instance_id=None,
        someip_sd_timings_profile="demo_someip_sd_timings_profile",
    )
    assert someipserviceconsumer is not None
