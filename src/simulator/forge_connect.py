from forge_sdk import ForgeConn

# set up forge connection

f = ForgeConn('127.0.0.1:27210')
rpc = f.rpc
config = f.config