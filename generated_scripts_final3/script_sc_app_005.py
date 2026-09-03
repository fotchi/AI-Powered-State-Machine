import sys
from flync.model.flync_4_app.application import ServiceProviderReference

def main():
    try:
        service_provider_reference = ServiceProviderReference(
            type='provider',
            service_name='consumer',
            instance_id=123,
            major_version=1
        )
        print("SUCCESS")
        sys.exit(0)
    except Exception as exc:
        print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()