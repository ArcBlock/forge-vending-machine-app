import os
import sys
sys.path.append('./src')
import yaml

from faker import Faker
from forge_sdk import utils

from utils.chain import rpc
from utils.conf import fixture_path, party



def create_wallet_dict(moniker: str, passphrase: str) -> dict:
    '''
    Create a wallet on the chain, and return its moniker, address, pk, and sk as dict
    ------
    Args:
        moniker(str): wallet's moniker
        passphrase(str): wallet's passphrase

    Output:
        return dict with info of moniker, address, pk, and sk
    '''

    # create a wallet
    new_wallet = rpc.create_wallet(moniker=moniker, passphrase=passphrase)

    return dict(
        moniker=moniker,
        address=new_wallet.wallet.address,
        pk=utils.multibase_b64encode(new_wallet.wallet.pk),
        sk=utils.multibase_b64encode(new_wallet.wallet.sk),
    )


# generate a certain number of wallet of certain type, and write the data in .yml
def wallet_generator(name: str, num: int):
    '''
    Generate a certain number of wallet of certain type, and write the data in yaml
    ------
    Args:
        name(str): the name of wallet
        num(int): the number of wallets wanted to create

    Output:
        create `fixtures/{}.yml`
    '''
  
    fake = Faker()
    data = []

    for i in range(num):
        # e.g. moniker = 'location001'
        moniker = name + str(i + 1).zfill(3)
        # e.g. passphrase = 'location0011234'
        passphrase = moniker[:2] + "1234"

        wallet_info = create_wallet_dict(moniker, passphrase)
       
       # add lat, lng for locations (for building scattergeo map)
        if name == 'location':
            (lat, lng, _, _, _,) = fake.local_latlng(country_code="US")
            wallet_info.update(dict(lat = str(lat), lng = str(lng)))
        # add a fake company for each party (for webapp display)
        if name in party:
            wallet_info.update(dict(company=fake.company()))
        # add an id number of each vending machine, e.g. 010 (for webapp display)
        elif name == 'vending_machine':
            wallet_info.update(dict(vm_id=str(i + 1).zfill(3)))
            
        data.append(wallet_info)

    with open('{}/{}.yml'.format(fixture_path, name), 'w') as outfile:
        yaml.dump(data, outfile, explicit_start=True)