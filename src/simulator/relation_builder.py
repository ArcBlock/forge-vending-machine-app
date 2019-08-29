import sys
sys.path.append('./src')
import yaml

from random import choice
# from utils import wallets
from utils.conf import fixture_path
from utils.load_yaml import load_yaml

def build_vending_machine(vms: list, ops: list, mas: list, los: list):
    '''
    assign a operator, a manufacturer and a location to each vending machine
    '''
    res = []
    for vm in vms:
        op=choice(ops)
        ma=choice(mas)
        lo=choice(los)

        vm.update(dict(
            operator = dict(moniker=op['moniker'], address=op['address'], company=op['company']),
            manufacturer = dict(moniker=ma['moniker'], address=ma['address'], company=ma['company']),
            location=dict(moniker=lo['moniker'], address=lo['address'], company=lo['company'], lat=lo['lat'], lng=lo['lng']),
        ))
        res.append(vm)
    
    with open('{}/vending_machine_models.yml'.format(fixture_path), 'w') as outfile:
        yaml.dump(res, outfile, explicit_start=True)
        
# build_vending_machine(wallets.vending_machines, wallets.manufacturers, wallets.locations)
# models = load_yaml("vending_machine_models")
# print(models[-1:])

def build_sku(skus: list, sus: list):
    '''
    assign a supplier to each sku
    '''
    res = []
    su=choice(sus)
    for sku in skus:
        sku.update(dict(
            supplier=dict(moniker=su['moniker'], address=su['address'], company=su['address']),
        ))
        res.append(sku)
    
    with open('{}/sku_models.yml'.format(fixture_path), 'w') as outfile:
        yaml.dump(res, outfile, explicit_start=True)

# build_sku(wallets.items, wallets.locations)
