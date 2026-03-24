from expyry.utils import parse_date, save_entry

def add_custom():
    print("\n✏️   Custom Credential\n")
    name = input("Label (e.g. 'AWS Access Key'): ").strip()
    date_input = input("Expiry date (e.g. YYYY-MM-DD): ").strip()
    
    expires, error = parse_date(date_input)
    if not expires:
        print(f"\n❌  {error}\n")
        return

    save_entry(name, "custom", expires)
    print(f"\n✅  {name} — expires {expires}\n")
