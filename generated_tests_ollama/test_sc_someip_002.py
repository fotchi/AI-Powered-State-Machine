import pytest
from flync.model.flync_4_someip.deployment import SOMEIPServiceConsumer

@pytest.mark.parametrize(
    "deployment_type, service, major_version, instance_id, someip_sd_timings_profile, consumed_eventgroups",
    [
        (
            "SOMEIP_DEPLOYMENT_TYPE",
            65536,
            0,
            1,
            "someip_sd_timings_profile",
            None
        ),
        (
            "SOMEIP_DEPLOYMENT_TYPE",
            -1,
            0,
            1,
            "someip_sd_timings_profile",
            None
        )
    ]
)
def test_subscribe_to_non_existent_eventgroup(
    deployment_type, service, major_version, instance_id, someip_sd_timings_profile, consumed_eventgroups
):
    with pytest.raises(pydantic.ValidationError) as excinfo:
        SOMEIPServiceConsumer(
            deployment_type=deployment_type,
            service=service,
            major_version=major_version,
            instance_id=instance_id,
            someip_sd_timings_profile=someip_sd_timings_profile,
            consumed_eventgroups=consumed_eventgroups
        )

    assert "gt" in str(excinfo.value)