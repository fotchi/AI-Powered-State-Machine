import sys
from pathlib import Path
import yaml

def load_can_bus_config(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

can_bus_config = load_can_bus_config('communication/channels/can/config.yaml')
print("SUCCESS")
sys.exit(0)