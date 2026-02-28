import json

def parse_json():
    # Open the JSON file
    with open("sample-data.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    # Print table header
    print("Interface Status")
    print("="*80)
    print(f"{'DN':50} {'Description':20} {'Speed':8} {'MTU':6}")
    print("-"*80)

    # Loop through each interface in JSON
    for item in data["imdata"]:
        attributes = item["l1PhysIf"]["attributes"]
        dn = attributes.get("dn", "")
        descr = attributes.get("descr", "")
        speed = attributes.get("speed", "")
        mtu = attributes.get("mtu", "")
        print(f"{dn:50} {descr:20} {speed:8} {mtu:6}")

# Make sure to use __name__ and __main__
if __name__ == "__main__":
    parse_json()