import sys
sys.path.append('./src')
import yaml

from random import choice
from utils.conf import fixture_path
from utils.load_yaml import load_yaml

def build_vending_machine(vms: list, ops: list, mas: list, los: list):
    '''
    Assign a operator, a manufacturer and a location to each vending machine randomly
    ------ 
    Args:
        vms(list): a list of vending machines info loaded from `vending_machine.yml`
        ops(list): a list of operators info loaded from `operator.yml`
        mas(list): a list of manufacturers info loaded from `manufacturer.yml`
        los(list): a list of locations info loaded from `location.yml`

    Output:
        generate `fixtures/vending_machine_models.yml`
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
        

def build_sku(skus: list, sus: list):
    '''
    Assign a supplier to each sku randomly
    ------ 
    Args:
        skus(list): a list of skus info loaded from `skus.yml`
        sus(list): a list of suppliers info loaded from `supplier.yml`

    Output:
        generate `fixtures/sku_models.yml` 
    '''
    res = []
    for sku in skus:
        su=choice(sus)
        sku.update(dict(
            supplier=dict(moniker=su['moniker'], address=su['address'], company=su['address']),
        ))
        res.append(sku)
    
    with open('{}/sku_models.yml'.format(fixture_path), 'w') as outfile:
        yaml.dump(res, outfile, explicit_start=True)
