import asyncio
import logging
import os
import signal
import sys
sys.path.append('./src')
import time
from random import choice
from random import randrange

from forge_sdk import protos
from forge_sdk import utils
from google.protobuf.timestamp_pb2 import Timestamp
from protos.aggregate_pb2 import AggregateTx
from sku_gen import sku_generator
from utils import wallets
from utils.chain import config
from utils.chain import rpc
from wallet_gen import wallet_generator



# set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simulator")


def prepare(num):
    '''
    Prepare necessary data (of wallets and sku) for simulation;
    for wallets:
        Declare a certain number of wallets on the chain for each party (vending_machine, operator, manufacturer, supplier, and location),
        and save key info of wallets (address, pk, sk, and moniker) as lists of dict in corresponding yaml files (fixtures/{}.yml).
    for sku:
        Group each sku's name and a random price as a dict,
        and put these dicts in a list and save it in fixtures/sku.yml
    ------
    Args:
        num(int): the number of elements for each category

    Output:
        1. declare sets of wallets on the chain
        2. generate yaml files in `fixtures/.`
    '''

    # declare wallets
    for party in ["vending_machine", "operator", "manufacturer", "supplier", "location"]:
        wallet_generator(party, num)

    # create sku
    sku_generator(num)
    time.sleep(10)


async def send(context):
    '''
    Get a ramdon element from each category, and current time to generate a bill for simulation.
    Send this bill on the chain through AggregateTx
    ------
    Args:
        context(dict): all necessary info (items, vending_machines, operators, manufacturers, suppliers, locations, batch)

    Output:
        send aggregate tx on the chain
    '''

    # put random info together to generate a random bill
    item = choice(context['items'])
    vm = choice(context['vending_machines'])
    op = choice(context['operators'])
    ma = choice(context['manufacturers'])
    su = choice(context['suppliers'])
    lo = choice(context['locations'])

    # get current time
    curr_time = Timestamp()
    curr_time.GetCurrentTime()

    # get item's value
    value = utils.int_to_biguint(utils.to_unit(item['value']))

    logger.debug("before tx...")
    logger.debug(
        f"{op['moniker']}'s balance is {rpc.get_account_balance(op['address'])}")
    logger.debug(
        f"{ma['moniker']}'s balance is {rpc.get_account_balance(ma['address'])}")
    logger.debug(
        f"{su['moniker']}'s balance is {rpc.get_account_balance(su['address'])}")
    logger.debug(
        f"{lo['moniker']}'s balance is {rpc.get_account_balance(lo['address'])}")

    # group a wallet object for vending_machine
    vm_wallet = protos.WalletInfo(pk=utils.multibase_b64decode(
        vm['pk']), sk=utils.multibase_b64decode(vm['sk']), address=vm['address'])

    # creat tx
    itx = AggregateTx(sku=item['sku'], value=value, time=curr_time, operator=op['address'],
                      manufacturer=ma['address'], supplier=su['address'], location=lo['address'])
    itx2 = utils.encode_to_any(type_url="fg:t:aggregate", data=itx)

    logger.info(
        f"batch {context['batch']} is sending tx... ---> value: {item['value']}, from: {vm['address']}, operator: {op['address']}, manufacturer: {ma['address']}, supplier: {su['address']}, location: {lo['address']}")
    res = rpc.send_itx(tx=itx2, wallet=vm_wallet, nonce=0)

    await asyncio.sleep(5)
    logger.info(f"verify tx: {rpc.is_tx_ok(res.hash)}")

    logger.debug(
        f"{op['moniker']}'s balance is {rpc.get_account_balance(op['address'])}")
    logger.debug(
        f"{ma['moniker']}'s balance is {rpc.get_account_balance(ma['address'])}")
    logger.debug(
        f"{su['moniker']}'s balance is {rpc.get_account_balance(su['address'])}")
    logger.debug(
        f"{lo['moniker']}'s balance is {rpc.get_account_balance(lo['address'])}")


async def simulate(context):
    '''
    Keep sending tx
    ------
    Args:
        context(dict): all necessary info (items, vending_machines, operators, manufacturers, suppliers, locations, batch)

    Output:
        call send()
    '''

    batch = context['batch']
    round = 1
    while True:
        logger.info(f"batch {batch}, round {round} starts...")
        await send(context)
        round += 1
        logger.info(f"batch {batch} is sleeping...")
        # sleep for a random period (1-10s)
        await asyncio.sleep(randrange(1, 11))


async def main(batch):
    '''
    Main function for simulator, running with Python Coroutines.
    Declare new wallets if there is an env var "DECLARE_WALLETS"=yes, load data from yaml files, and call simulate()
    ------
    Args:
        batch(int): the number of coroutines

    Output:
        call simulate()
    '''
    declare_wallets = os.environ.get("DECLARE_WALLETS")

    if declare_wallets == "yes":
        logger.info("first-time simulate, declaring wallets...")
        prepare(10)
    else:
        await asyncio.gather(*(simulate(dict(items=wallets.items,
                                             vending_machines=wallets.vending_machines,
                                             operators=wallets.operators,
                                             manufacturers=wallets.manufacturers,
                                             suppliers=wallets.suppliers,
                                             locations=wallets.locations,
                                             batch=n,
                                             )) for n in range(batch)))
    # await send()


def signal_handler(sig, frame):
    '''
    Capture SIGINT in Python
    '''

    print('You pressed Ctrl+C!')
    time.sleep(2)
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(main(3))
