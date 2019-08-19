import os
import yaml

from forge_connect import rpc
from forge_sdk import utils

from conf import fixture_path

# create a wallet on the chain, and return its moniker, address, pk, and sk as dict
def create_wallet_dict(moniker, passphrase):
    # create a wallet
    assert(isinstance(moniker, str) and isinstance(passphrase, str))
    new_wallet = rpc.create_wallet(moniker=moniker, passphrase=passphrase)

    return dict(
        moniker = moniker,
        address = new_wallet.wallet.address,
        pk = utils.multibase_b64encode(new_wallet.wallet.pk),
        sk = utils.multibase_b64encode(new_wallet.wallet.sk),
    )


# generate a certain number of wallet of certain type, and write the data in .yml
def wallet_generator(name, num):
    assert(isinstance(name, str) and isinstance(num, int))

    data = []

    for i in range(num):
        # e.g. moniker = 'location001'
        moniker = name + str(i + 1).zfill(3)
        # e.g. passphrase = 'location0011234'
        passphrase = moniker[:2] + "1234"

        data.append(create_wallet_dict(moniker, passphrase))

    with open('{}/{}.yml'.format(fixture_path, name), 'w') as outfile:
        yaml.dump(data, outfile, explicit_start=True)

# create_wallet_dict("nana", "abcd1234")
wallet_generator("vending_machine", 4)