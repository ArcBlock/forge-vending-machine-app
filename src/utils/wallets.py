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

SKU_DICT = {}
for sku in items:
    SKU_DICT.update({"{}".format(sku['sku']): sku['barcode']})


VM_DICT = {}
for vm in vending_machines:
    VM_DICT.update({"{}".format(vm['moniker']): vm['vm_id']})

OP_DICT = {}
for op in operators:
    OP_DICT.update({"{}".format(op['moniker']): op['company']})

MA_DICT = {}
for ma in manufacturers:
    MA_DICT.update({"{}".format(ma['moniker']): ma['company']})

SU_DICT = {}
for su in suppliers:
    SU_DICT.update({"{}".format(su['moniker']): su['company']})

LO_DICT = {}
for lo in locations:
    LO_DICT.update({"{}".format(lo['moniker']): [lo['company'], lo['lat'], lo['lng']]})

parties_moniker_name = dict(
    operator=OP_DICT, 
    manufacturer=MA_DICT,
    supplier=SU_DICT, 
    location=LO_DICT,
)