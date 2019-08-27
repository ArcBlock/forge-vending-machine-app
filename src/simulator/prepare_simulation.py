import time
import sys
sys.path.append('./src')

from relation_builder import build_vending_machine, build_sku
from sku_gen import sku_generator
from utils.load_yaml import load_yaml
from wallet_gen import wallet_generator

def create_wallet(context):
    '''
    Create skus and wallets
    for wallets:
        Declare a certain number of wallets on the chain for each party (vending_machine, operator, manufacturer, supplier, and location),
        and save key info of wallets (address, pk, sk, and moniker) as lists of dict in corresponding yaml files (fixtures/{}.yml).
    for sku:
        Group each sku's name and a random price as a dict,
        and put these dicts in a list and save it in fixtures/sku.yml
    ------
    Args:
        context(dict): specify the number of wallets to create for each party, 
            example {'sku': 15, 'vending_machine':25, 'operator':3, 'manufacturer':5, 'supplier': 10, 'location':20} 
    
    Output:
        1. generate a set of skus
        2. declare sets of wallets on the chain
        3. generate yaml files in `fixtures/.`
    '''

    # generate sku
    sku_generator(context['sku'])
    
    # generate party wallets
    for party in ['vending_machine', 'operator', 'manufacturer', 'supplier', 'location']:
        wallet_generator(party, context[party])


def build_relation(sku, vm, op, ma, su, lo):
    '''
    Create relationship for each vending machine and each sku
    ------
    Args:
        sku(list): list of sku loaded from `sku.yml`
        vm(list): list of vending machines loaded from `vending_machine.yml`
        op(list): list of operators loaded from `operator.yml`
        ma(list): list of manufacturers loaded from `manufacturer.yml`
        su(list): list of suppliers loaded from `supplier.yml`
        lo(list): list of locations loaded from `locations.yml`

    Output:
        generate `fixtures/sku_model.yml` and `fixtures/vending_machine_models.yml`
    '''
    build_vending_machine(vm, op, ma, lo)
    build_sku(sku, su)


def main():
    '''
    Prepare necessary data (of wallets and sku) for simulation
    ------
    Args:
        context(dict): specify the number of wallets to create for each party, 
            example {'sku': 15, 'vending_machine':25, 'operator':3, 'manufacturer':5, 'supplier': 10, 'location':20} 
    
    Output:
        1. declare a set of wallets on the chain chain
        2. generate yaml files in `fixtures/.`
    '''
    # set up number
    context = dict(
        sku=15, 
        vending_machine=25, 
        operator=3,
        manufacturer=5,
        supplier=10,
        location=20,
    )

    # declare wallets and sku
    create_wallet(context)

    items = load_yaml("sku")
    vending_machines = load_yaml("vending_machine")
    operators = load_yaml("operator")
    manufacturers = load_yaml("manufacturer")
    suppliers = load_yaml("supplier")
    locations = load_yaml("location")

    build_relation(items, vending_machines, operators, manufacturers, suppliers, locations)

if __name__ == "__main__":
    main()