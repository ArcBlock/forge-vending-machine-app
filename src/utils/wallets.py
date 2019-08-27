from .load_yaml import load_yaml

# load items
items = load_yaml("sku")

# load wallets
vending_machines = load_yaml("vending_machine")
operators = load_yaml("operator")
manufacturers = load_yaml("manufacturer")
suppliers = load_yaml("supplier")
locations = load_yaml("location")

# load units
item_units = load_yaml("sku_models")
vm_units = load_yaml("vending_machine_models")