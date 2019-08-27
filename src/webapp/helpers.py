import pandas as pd
import time
import sys
sys.path.append('./src')

from db.db import sqlite_file, sql_connection
from utils.chain import get_account_states
from utils.wallets import vending_machines, operators, manufacturers, suppliers, locations, vm_units


'''
The following functions are grabbing the data on the chain
'''

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

'''
The following functions are grabbing the data from the db
'''

def query_rows(column, value):
    '''
    Query all rows in the table by a certain column,
    turn the result into DataFrame
    ------
    Args: 
        column(str): the name of the column to query
        value(str): query by this value

    Output:
        query_result(df)
    '''
    conn = sql_connection(sqlite_file)
    return pd.read_sql_query('SELECT * FROM transactions WHERE {} = (?)'.format(column), conn, params=(value,))

# res = query_rows('operator', 'operator002')
# print(res.shape)
# for i in res:
#     print(i)

def get_value_prop(column: str):
    '''
    Return the number of values of a certain column
    ------
    Args:
        column(str): column

    Output:
        res(dict): e.g. {'operator001': 47, 'operator002': 26, 'operator003': 26}
    '''
    conn = sql_connection(sqlite_file)
    c = conn.cursor()
    c.execute("SELECT DISTINCT {} FROM transactions ORDER BY {}".format(column, column))
    unique_values = c.fetchall()
    res = {}
    for value in unique_values:
        c.execute("SELECT COUNT(*) FROM transactions WHERE {} = ?".format(column), value)
        res.update({'{}'.format(value[0]): c.fetchone()[0]})
    return res

# print(get_value_prop('operator'))


'''
Other helper functions
'''
def heatmap_helper():
    '''
    return matrix, e.g. [[1, 2, 3, 4,], [2, 3, 4, 5]]

    x-axis: 'operator's vending machines'
    y-axis: 'each operator'
    z-axis: 'number of tx'
    '''

    conn = sql_connection(sqlite_file)
    c = conn.cursor()

    c.execute("SELECT DISTINCT operator FROM transactions ORDER BY operator")
    distinct_ops = c.fetchall()
    whole_op_list = []
    whole_vm_list = []
    whole_tx_list = []
    for (op,) in distinct_ops:
        whole_op_list.append(op)
        vm_list = []
        tx_list = []
        for unit in vm_units:
            if unit['operator']['moniker'] == op:
                vm = unit['moniker']
                vm_list.append(vm)
                c.execute("SELECT COUNT(*) FROM transactions WHERE operator = ? AND vending_machine = ?", (op, vm))
                tx_list.append(c.fetchone()[0])
        whole_vm_list.append(vm_list)
        whole_tx_list.append(tx_list)

    return whole_op_list, whole_vm_list, whole_tx_list

# print(heatmap_helper())