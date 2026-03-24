from datetime import datetime, date
from expyry.config import load_config, save_config, CONFIG_PATH

MAX_YEAR = 2100

def parse_date(date_str: str) -> [str | None, str | None]:
    """
    Try to parse whatever date format the user throws at us.
    Always returns YYYY-MM-DD or None if it fails.
    """
    formats = [
        "%Y-%m-%d",      # 2026-05-01
        "%Y/%m/%d",      # 2026/05/01
        "%d/%m/%Y",      # 01/05/2026
        "%m/%d/%Y",      # 05/01/2026
        "%b %d %Y",      # May 01 2026
        "%B %d %Y",      # May 01 2026
        "%d %b %Y",      # 01 May 2026
        "%d %B %Y",      # 01 May 2026
        "%b %d, %Y",     # May 1, 2026
        "%B %d, %Y",     # May 1, 2026
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)

            if parsed.year > MAX_YEAR:
                return None, f"Year {parsed.year} seems too far in the future."
            
            if parsed.date() < date.today():
                return None, "That date is already in the past. Enter a future date."

            return parsed.strftime("%Y-%m-%d"), None

        except ValueError:
            continue

    return None, f"Couldn't parse '{date_str}'. Try: YYYY-MM-DD"

def save_entry(name, service_type, expires, extra={}):
    config = load_config()
    entry = {
        "name": name,
        "type": service_type,
        "expires": expires,
        "never_expires": expires is None,
        **extra
    }

    # merge any extra fields like domain for SSL
    for key, value in extra.items():
        entry[key] = value

    # remove existing entry with same name if present
    updated_services = []
    for s in config["services"]:
        if s["name"] != name:
            updated_services.append(s)
    
    updated_services.append(entry)
    config["services"] = updated_services
    save_config(config)
    print(f"💾  Saved to {CONFIG_PATH}\n")
