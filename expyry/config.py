from pathlib import Path
import yaml

CONFIG_PATH = Path.home() / ".expyry" / "config.yaml"
BASHRC_COMMENT = "# Expyry — credential expiry checker"
BASHRC_LINE = "expyry list --quiet"

def load_config():
    if not CONFIG_PATH.exists():
        return {"services": []}
    try:
        with open(CONFIG_PATH) as f:
            data = yaml.safe_load(f)
        # safe_load returns None for empty files
        if data is None:
            return {"services": []}
        
        # make sure it has the right structure
        if "services" not in data:
            return {"services": []}
                
        return data
    
    except yaml.YAMLError:
        print(f"\n⚠️  Config file is corrupted: {CONFIG_PATH}")
        print("    Your saved credentials could not be loaded.")
        print("    Fix the file manually or delete it and start fresh.\n")
        return {"services": []}

    except PermissionError:
        print(f"\n❌  Cannot read config file: {CONFIG_PATH}")
        print("    Check file permissions.\n")
        return {"services": []}

def save_config(config):
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    except PermissionError:
        print(f"\n❌  Cannot write to config file: {CONFIG_PATH}")
        print("    Check file permissions.\n")
    except OSError as e:
        print(f"\n❌  Failed to save config: {e}\n")

