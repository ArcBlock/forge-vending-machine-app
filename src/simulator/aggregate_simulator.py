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
from utils import wallets
from utils.chain import config
from utils.chain import rpc


# set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simulator")


async def send(context):
    '''
    Get a ramdon element from each category, and current time to generate a bill for simulation.
    Send this bill on the chain through AggregateTx
    ------
    Args:
        context(dict): all necessary info (items, vending_machines, batch)

    Output:
        send aggregate tx on the chain
    '''

    # put random info together to generate a random bill

    item_unit = choice(context['items'])
    vm_unit = choice(context['vms'])

    op = vm_unit['operator']
    ma = vm_unit['manufacturer']
    su = item_unit['supplier']
    lo = vm_unit['location']

    # get current time
    curr_time = Timestamp()
    curr_time.GetCurrentTime()

    # get item's value
    value = utils.int_to_biguint(utils.to_unit(item_unit['value']))

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
        vm_unit['pk']), sk=utils.multibase_b64decode(vm_unit['sk']), address=vm_unit['address'])

    # creat tx
    itx = AggregateTx(sku=item_unit['sku'], value=value, time=curr_time, operator=op['address'],
                      manufacturer=ma['address'], supplier=su['address'], location=lo['address'])
    itx2 = utils.encode_to_any(type_url="fg:t:aggregate", data=itx)

    logger.info(
        f"batch {context['batch']} is sending tx... ---> value: {item_unit['value']}, from: {vm_unit['address']}, operator: {op['address']}, manufacturer: {ma['address']}, supplier: {su['address']}, location: {lo['address']}")
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
    Load data from yaml files, and call simulate()
    ------
    Args:
        batch(int): the number of coroutines

    Output:
        call simulate()
    '''
    await asyncio.gather(*(simulate(dict(items=wallets.item_units,
                                            vms=wallets.vm_units,
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
