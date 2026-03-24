import os
from pathlib import Path
from expyry.config import BASHRC_COMMENT, BASHRC_LINE

def detect_shell_profile() -> str | None:
    """
    Detect which shell the user is running and return
    the appropriate profile file path.
    """
    shell = os.environ.get("SHELL", "")
    
    if "zsh" in shell:
        return str(Path.home() / ".zshrc")
    elif "bash" in shell:
        # prefer .bashrc, fall back to .bash_profile on Mac
        bashrc = Path.home() / ".bashrc"
        bash_profile = Path.home() / ".bash_profile"
        if bashrc.exists():
            return str(bashrc)
        elif bash_profile.exists():
            return str(bash_profile)
        else:
            return str(bashrc)  # create .bashrc if neither exists
    elif "fish" in shell:
        return str(Path.home() / ".config/fish/config.fish")
    else:
        return None

def enable_notification() -> dict:
    """
    Append expyry check --quiet to the user's shell profile.
    Asks permission first, never does it silently.
    """
    profile_path = detect_shell_profile()

    if not profile_path:
        return {
            "success": False,
            "error": "Could not detect shell. Add this line manually to your shell profile:",
            "manual": BASHRC_LINE
        }

    # already added, don't duplicate
    if is_already_added(profile_path):
        return {
            "success": True,
            "already_exists": True,
            "profile": profile_path
        }

    try:
        with open(profile_path, "a") as f:
            f.write(f"\n{BASHRC_COMMENT}\n{BASHRC_LINE}\n")
        return {
            "success": True,
            "already_exists": False,
            "profile": profile_path
        }
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied writing to {profile_path}. Add this line manually:",
            "manual": BASHRC_LINE
        }

def disable_notification() -> dict:
    profile_path = detect_shell_profile()

    if not profile_path:
        return {
            "success": False,
            "error": "Could not detect shell profile:"
        }

    try:
        with open(profile_path, "r") as f:
            lines = f.readlines()

        # filter out both the comment and the command line
        updated_lines = [
            line for line in lines
            if BASHRC_COMMENT not in line
            and BASHRC_LINE not in line
        ]

        if len(updated_lines) == len(lines):
            return {"success": False, "already_removed": True}

        with open(profile_path, "w") as f:
            f.writelines(updated_lines)

        return {"success": True, "profile": profile_path}

    except PermissionError:
        return {"success": False, "error": f"Permission denied writing to {profile_path}"}

def enable_shell_notification():
    """
    Interactive wizard step for shell notification enabling.
    """
    print("\n🔔  Shell Startup Notifications\n")
    print("Expyry can silently check your stored credential validity every time")
    print("you open a terminal and warn you if something is expiring.\n")

    profile_path = detect_shell_profile()

    if profile_path:
        print(f"Detected shell profile: {profile_path}")
    else:
        print("⚠️  Could not detect your shell profile automatically.")

    choice = input("\nEnable startup notifications? (recommended) [Y/n]: ").strip().lower()
    
    if choice in ("","y","yes"):
        result = enable_notification()

        if result.get("already_exists"):
            print(f"✅  Already set up in {result['profile']}")

        elif result["success"]:
            print(f"✅  Added to {result['profile']}")
            print("    Open a new terminal to activate.\n")

        else:
            print(f"\n⚠️  {result['error']}")
            if "manual" in result:
                print(f"\n    Add this line to your shell profile manually:")
                print(f"    {result['manual']}\n")

    else:
        print("\n⏭️   Skipped.\n")

def disable_shell_notification():
    print("\n🔕  Disabling shell notifications\n")

    result = disable_notification()

    if result.get("already_removed"):
        print("⚠️   Expyry notification not found in shell profile.")
        print("    Nothing to remove.\n")

    elif result["success"]:
        print(f"✅  Removed from {result['profile']}")
        print("    Open a new terminal to take effect.\n")

    else:
        print(f"\n❌  {result['error']}\n")

def is_already_added(profile_path: str) -> bool:
    try:
        with open(profile_path, "r") as f:
            return BASHRC_LINE in f.read()
    except FileNotFoundError:
        return False
