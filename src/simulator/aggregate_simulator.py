import asyncio
import logging
import os
import time

from forge_connect import rpc, config
from forge_sdk import protos, utils
from google.protobuf.timestamp_pb2 import Timestamp
from load_yaml import load_yaml
from protos.aggregate_pb2 import AggregateTx
from random import choice
from sku_gen import sku_generator
from wallet_gen import wallet_generator

# set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simulator")

# generate lists of relevant info, supposing they have the same number of elements
def prepare(num):
    # declare wallets
    for party in ["vending_machine", "operator", "manufacturer", "supplier", "location"]:
        wallet_generator(party, num)

    # create sku
    sku_generator(num)
    time.sleep(10)
    
# loads wallets and items
def setup(curr_time):
    # load items
    items = load_yaml("sku")
    
    # load wallets
    vending_machines = load_yaml("vending_machine")
    operators = load_yaml("operator")
    manufacturers = load_yaml("manufacturer")
    suppliers = load_yaml("supplier")
    locations = load_yaml("location")

    # put random info together to generate a random bill
    item = choice(items)
    vm = choice(vending_machines)
    op = choice(operators)
    ma = choice(manufacturers)
    su = choice(suppliers)
    lo = choice(locations)

    value = utils.int_to_biguint(utils.to_unit(item['value']))


    # group a wallet object for vending_machine
    vm_wallet = protos.WalletInfo(pk=utils.multibase_b64decode(vm['pk']), sk= utils.multibase_b64decode(vm['sk']), address=vm['address'])
    print(vm_wallet)
    # creat tx
    itx =  AggregateTx(sku=item['sku'], value=value, time=curr_time, operator=op['address'], \
        manufacturer=ma['address'], supplier=su['address'], location=lo['address'])
    print(itx)
    
    itx2 = utils.encode_to_any(type_url="fg:t:aggregate", data=itx)

    logger.info("sending tx...")
    res = rpc.send_itx(tx=itx2, wallet=vm_wallet, nonce=0)

    time.sleep(3)
    logger.info(f"TX verify: {rpc.is_tx_ok(res.hash)}")



    



    
    

def main(curr_time):
    declare_wallets = os.environ.get("DECLARE_WALLETS")

    if declare_wallets == "yes":
        logger.info("first-time simulate, declaring wallets...")
        prepare(10)


    setup(curr_time)

if __name__ == "__main__":
    curr_time = Timestamp()
    curr_time.GetCurrentTime()
    main(curr_time)



#     # prepare accounts/wallets for simulation
#     def setup(self):
#         # create wallet if needed
#         # TODO
#         # if True: 
#         #     wallet_gen.wallet_generator("vending_machine", self.vm_num)
#         #     wallet_gen.wallet_generator("operator", self.op_num)
#         #     wallet_gen.wallet_generator("manufacturer", self.ma_num)
#         #     wallet_gen.wallet_generator("supplier", self.su_num)
#         #     wallet_gen.wallet_generator("location", self.lo_num)

#         # load yaml
#         self.vm_dict = wallet_gen.get_wallet_yaml("vending_machine")
#         self.op_dict = wallet_gen.get_wallet_yaml("operator")
#         self.ma_dict = wallet_gen.get_wallet_yaml("manufacturer")
#         self.su_dict = wallet_gen.get_wallet_yaml("supplier")
#         self.lo_dict = wallet_gen.get_wallet_yaml("location")



    

        

        
            




# # port = ForgeConn('127.0.0.1:27210')
# sim = AggregateSimulator(10, 5, 3, 5, 8)
# sim.setup()



#     # read from json / yaml - vm, location, .... wallet vm.json, location.json, ...
#     # declare wallets when a env defined, but load wallets everytime DECLARE_WALLETS=yes  python3 aggregate_sim.py
#     # def setup:

#     # get one random value for each group of wallets. (vm1, op1, lo1, ...)
#     # generate a tx after a random time
#     # def simulate:



# aysnc def simulate(batch):
#     while True:
#         tasks = [i for i in 1..batch asyncio.create_task(send_tx())]

#         print(f"started at {time.strftime('%X')}")

#         # Wait until both tasks are completed (should take
#         # around 2 seconds.)
#         for i in 1..batch:
#             await tasks[i]