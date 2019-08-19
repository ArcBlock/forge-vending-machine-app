from forge_sdk import ForgeConn
from forge_sdk import protos, utils
from google.protobuf.timestamp_pb2 import Timestamp
from protos.aggregate_pb2 import AggregateTx
from time import sleep
import logging

logger = logging.getLogger("test")

# connect to a forge port

f = ForgeConn('127.0.0.1:27210')
rpc = f.rpc
config = f.config
# print(config.file)

logger.info("creating values...")

# create wallets for relevant parties
vm = rpc.create_wallet(moniker='vending_machine', passphrase='vm1234')
ma = rpc.create_wallet(moniker='manufacturer', passphrase='ma1234')
op = rpc.create_wallet(moniker='operator', passphrase='op1234')
su = rpc.create_wallet(moniker='supplier', passphrase='su1234')
lo = rpc.create_wallet(moniker='location', passphrase='lo1234')

print("vending machine's wallet: ", vm)
print("manufacturer's wallet: ", ma)
print("operator's wallet: ", op)
print("supplier's wallet: ", su)
print("location's wallet: ", lo)

# create other necessary info
sku = "pepsi"
value = utils.int_to_biguint(utils.to_unit(2))
logger.debug("value is %s", value)


# check account balance
sleep(3)
time = Timestamp()
time.GetCurrentTime()
print("time is %s", time)

print(f"operator's balance is {rpc.get_account_balance(op.wallet.address)}")
print(f"manufacturer's balance is {rpc.get_account_balance(ma.wallet.address)}")
print(f"supplier's balance is {rpc.get_account_balance(su.wallet.address)}")
print(f"location's balance is {rpc.get_account_balance(lo.wallet.address)}")


logger.info("sending a tx...")
    
# send a tx
itx = AggregateTx(sku=sku, value=value, time=time, operator=op.wallet.address, \
    manufacturer=ma.wallet.address, supplier=su.wallet.address, location=lo.wallet.address)
itx2 = utils.encode_to_any(type_url="fg:t:aggregate", data=itx)
print("itx2 is ", itx2)
res = rpc.send_itx(tx=itx2, wallet=vm.wallet, token=vm.token, nonce=0)
print("res is ", res)


# check tx
sleep(3)
logger.info(f"TX verify: {rpc.is_tx_ok(res.hash)}")

print(f"operator's balance is {rpc.get_account_balance(op.wallet.address)}")
print(f"manufacturer's balance is {rpc.get_account_balance(ma.wallet.address)}")
print(f"supplier's balance is {rpc.get_account_balance(su.wallet.address)}")
print(f"location's balance is {rpc.get_account_balance(lo.wallet.address)}")
