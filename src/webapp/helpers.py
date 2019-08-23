import time
import sys
sys.path.append('./src')

from utils.chain import get_account_states
from utils.wallets import vending_machines, operators, manufacturers, suppliers, locations


# get a list of dicts of parties' wallet info (address, pk, sk, and moniker)
PARTY_LIST = [operators, manufacturers, suppliers, locations]

def get_parties_addresses(lst: list):
    '''
    Grab the addresses of all parties,
    a helper function for get_parties_states
    ------
    Args:
        lst(list): list of dicts of parties's wallet info (address, pk, sk, and moniker)

    Output:
        addresses(list): list of parties' addresses
    '''

    addresses = []
    for party in lst:
        addresses = [*addresses, *[item['address'] for item in party]]
    return addresses


def get_parties_states(lst: list):
    '''
    Get the states of every party's wallets
    ------
    Args:
        lst(list): list of dicts of parties's wallet info (address, pk, sk, and moniker)

    Output:
        (list): a list of states of the given addresses, 
            where each state is a dict with a party's wallet info (balance, num_txs, address, and moniker)
    '''

    return get_account_states(get_parties_addresses(lst))


def party_types(lst: list):
    '''
    Get the type of each party, where type includes operator, manufacturer, supplier, and location,
    a helper function for building RadioItems and Dropdown.
    ------
    Args:
        lst(list): list of dicts of parties's wallet info (address, pk, sk, and moniker)

    Output:
        type(dict): a dict where key and value are wallet monikers
    '''
    
    types = {}
    for party in get_parties_states(lst):
        moniker = party['moniker']
        types.update({'{}'.format(moniker): moniker})
    return types


PARTY_TYPES = party_types(PARTY_LIST)
