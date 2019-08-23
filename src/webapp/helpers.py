import time
import sys
sys.path.append('./src')

from utils.chain import get_account_states
from utils.wallets import vending_machines, operators, manufacturers, suppliers, locations

# get account state

def get_parties_addresses():
    addresses = []
    for party in [operators, manufacturers, suppliers, locations]:
        addresses = [*addresses, *[item['address'] for item in party]]
    return addresses


def get_parties_states():
    return get_account_states(get_parties_addresses())


# def check_type(moniker: str):
#     '''
#     Check the type of a party
#     '''
#     for t in ['operator', 'manufacturer', 'supplier', 'location']:
#         if t in moniker:
#             return t
#         continue
#     raise ValueError("Oops, no match type is found")
# print(check_type("hh001"))


# get control dict
def party_types():
    types = {}
    for party in get_parties_states():
        moniker = party['moniker']
        types.update({'{}'.format(moniker): moniker})
    return types


PARTY_TYPES = party_types()

# # add user readable info to aggregate tx list
# def readable_aggregate_tx_lst():
#     lst = list_aggregate_tx()
#     for d in lst:
#         d.update(dict(
#             vm = get_account_moniker(d['vm_addr']),
#             operator = get_account_moniker(d['op_addr']),
#             manufacturer = get_account_moniker(d['ma_addr']),
#             supplier = get_account_moniker(d['su_addr']),
#             location = get_account_moniker(d['lo_addr']),
#         ))
#     return lst
