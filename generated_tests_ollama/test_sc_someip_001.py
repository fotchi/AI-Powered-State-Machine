import pytest
from flync.model.flync_4_someip.deployment import SOMEIPServiceConsumer

@pytest.fixture
def someip_service_consumer():
    return SOMEIPServiceConsumer(
        deployment_type="SOMEIP",
        service=12345,
        major_version=1,
        instance_id=54321,
        someip_sd_timings_profile="some_ip_timings_profile"
    )

def test_someip_service_consumer(someip_service_consumer):
    assert isinstance(someip_service_consumer, SOMEIPServiceConsumer)
    assert someip_service_consumer.deployment_type == "SOMEIP"
    assert someip_service_consumer.service == 12345
    assert someip_service_consumer.major_version == 1
    assert someip_service_consumer.instance_id == 54321
    assert someip_service_consumer.someip_sd_timings_profile == "some_ip_timings_profile"

def test_someip_service_consumer_consumed_eventgroups(someip_service_consumer):
    someip_service_consumer.consumed_eventgroups = ["eventgroup1", "eventgroup2"]
    assert someip_service_consumer.consumed_eventgroups == ["eventgroup1", "eventgroup2"]

def test_someip_service_consumer_invalid_deployment_type():
    with pytest.raises(pydantic.ValidationError):
        SOMEIPServiceConsumer(deployment_type="invalid")

def test_someip_service_consumer_invalid_service():
    with pytest.raises(pydantic.ValidationError):
        SOMEIPServiceConsumer(service=0)

def test_someip_service_consumer_invalid_major_version():
    with pytest.raises(pydantic.ValidationError):
        SOMEIPServiceConsumer(major_version=-1)

def test_someip_service_consumer_invalid_instance_id():
    with pytest.raises(pydantic.ValidationError):
        SOMEIPServiceConsumer(instance_id=65536)

def test_someip_service_consumer_invalid_someip_sd_timings_profile():
    with pytest.raises(pydantic.ValidationError):
        SOMEIPServiceConsumer(someip_sd_timings_profile="")

def test_someip_service_consumer_consumed_eventgroups_none():
    someip_service_consumer = SOMEIPServiceConsumer(
        deployment_type="SOMEIP",
        service=12345,
        major_version=1,
        instance_id=54321,
        someip_sd_timings_profile="some_ip_timings_profile"
    )
    assert someip_service_consumer.consumed_eventgroups is None