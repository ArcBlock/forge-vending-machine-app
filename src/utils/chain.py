import json
import logging
import sys
from datetime import datetime

from forge_sdk import ForgeConn
from forge_sdk import protos
from forge_sdk import utils
from simulator.protos.aggregate_pb2 import AggregateTx
sys.path.append('./src')


# set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chain")


# set up forge connection
f = ForgeConn('127.0.0.1:27210')
rpc = f.rpc
config = f.config


def get_account_states(addresses: list):
    states = []
    for addr in addresses:
        state = rpc.get_single_account_state(addr)
        raw_data = state.data.value
        if raw_data == b'':
            data = dict(balance=0, num_txs=0)
        else:
            data = json.loads(state.data.value)
        data.update(address=state.address, moniker=state.moniker)
        states.append(data)
    return states


def get_wallet_moniker(address: str):
    return rpc.get_single_account_state(address).moniker


def get_current_txs_info(db_height: int):
    '''
    1. get current block height
    2. grab every [:ok & aggregate] tx info in dict from every block from last height to current height
    '''
    block_height = rpc.get_chain_info().info.block_height
    logger.debug(block_height)

    # get blocks info from (current db height + 1) to current block height
    args = {"from": db_height + 1, "to": block_height}
    cursor = None
    next_page = True
    res = []

    while next_page:
        logger.debug("a new page starts")
        page = rpc.get_blocks(height_filter=protos.RangeFilter(
            **args), empty_excluded=True, paging=protos.PageInput(cursor=cursor))
        next_page = page.page.next
        cursor = page.page.cursor
        blocks = page.blocks
        logger.debug(f"blocks are \n {blocks}")

        for i in range(len(blocks)):
            single_block_txs_hashes = blocks[i].txs_hashes
            logger.debug(blocks[i])
            logger.debug("hashes are ", single_block_txs_hashes)

            for hash in single_block_txs_hashes:
                t = rpc.get_single_tx_info(hash)
                if t.code == 0 and t.tx.itx.type_url == 'fg:t:aggregate':
                    itx = utils.parse_to_proto(t.tx.itx.value, AggregateTx)
                    value = utils.biguint_to_int(itx.value)
                    time = datetime.fromtimestamp(itx.time.seconds)
                    info = dict(
                        hash=hash,
                        vm_addr=getattr(t.tx, "from"),
                        sku=itx.sku,
                        price=value,
                        time=time,
                        op_addr=itx.operator,
                        ma_addr=itx.manufacturer,
                        su_addr=itx.supplier,
                        lo_addr=itx.location,
                    )
                    info.update(dict(
                        vm=get_wallet_moniker(info['vm_addr']),
                        op=get_wallet_moniker(info['op_addr']),
                        ma=get_wallet_moniker(info['ma_addr']),
                        su=get_wallet_moniker(info['su_addr']),
                        lo=get_wallet_moniker(info['lo_addr']),
                    ))
                    res.append(info)

    return res, block_height

# res, db_height = get_current_txs_info(0)
# print("res is \n", res)
# print("db_height is ", db_height)
