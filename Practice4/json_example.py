import json

with open("sample-data.json") as f:
    data = json.load(f)


interfaces = data["imdata"]

print("Interface Status")
print("="*79)
print("{:<50} {:<20} {:<7} {:<7}".format("DN", "Description", "Speed", "MTU"))
print("-"*50, "-"*20, "-"*7, "-"*7)

for item in interfaces:
    attributes = item["l1PhysIf"]["attributes"]
    dn = attributes.get("dn", "")
    descr = attributes.get("descr", "")
    speed = attributes.get("speed", "")
    mtu = attributes.get("mtu", "")
    print("{:<50} {:<20} {:<7} {:<7}".format(dn, descr, speed, mtu))

