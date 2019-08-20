import os

import yaml
from conf import fixture_path
from forge_connect import rpc
from forge_sdk import utils


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

    data = []

    for i in range(num):
        # e.g. moniker = 'location001'
        moniker = name + str(i + 1).zfill(3)
        # e.g. passphrase = 'location0011234'
        passphrase = moniker[:2] + "1234"

        data.append(create_wallet_dict(moniker, passphrase))

    with open('{}/{}.yml'.format(fixture_path, name), 'w') as outfile:
        yaml.dump(data, outfile, explicit_start=True)

# w = create_wallet_dict("nana", "abcd1234")
# print(w)
# wallet_generator("vending_machine", 4)
