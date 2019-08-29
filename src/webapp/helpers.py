import pandas as pd
import time
import sys
sys.path.append('./src')

from db.db import sqlite_file, sql_connection
from utils.chain import get_account_states
from utils.wallets import vending_machines, operators, manufacturers, suppliers, locations, vm_units
from utils.wallets import parties_moniker_name


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
    for party in lst:
        for elem in party:
            types.update({'{}'.format(elem['moniker']): elem['company']}) 
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


def get_distinct_value(column: str): 
    '''
    Return distinct values of a column
    ------
    Args:
        column(str): column's header
        
    Output:
        (list): e.g. [('operator001',), ('operator002',), ('operator003',)]
    '''
    conn = sql_connection(sqlite_file)
    c = conn.cursor()
    c.execute("SELECT DISTINCT {} FROM transactions ORDER BY {}".format(column, column))
    return c.fetchall()


def get_value_prop(column: str):
    '''
    Return the number of values of a certain column
    ------
    Args:
        column(str): column's header

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

def get_value_prop_with_conditions(column: str, con_column:str, con_value):
    '''
    Return the number of values of a certain column with conditions
    ------
    Args:
        column(str): column's header
        con_column(str): conditional column's header
        con_value(any type): conditional column's value

    Output:
        res(dict): e.g. {'operator001': 47, 'operator002': 26, 'operator003': 26}
    '''
    conn = sql_connection(sqlite_file)
    c = conn.cursor()
    c.execute("SELECT DISTINCT {} FROM transactions WHERE {} = ? ORDER BY {}".format(column, con_column, column), (con_value,))
    unique_values = c.fetchall()
    res = {}
    for value in unique_values:
        c.execute("SELECT COUNT(*) FROM transactions WHERE {} = ?".format(column), value)
        res.update({'{}'.format(value[0]): c.fetchone()[0]})
    return res

# print(get_value_prop_with_conditions('item', 'vm_id', '017'))


'''
Other helper functions
'''
def moniker_name_converter(moniker: str): 
    '''
    Find the company name of a party by its moniker
    ------ 
    Args:
        moniker(str): party's wallet moniker

    Output:
        (str): party's company name 
    '''
    for elem in PARTY_TYPES:
        if elem == moniker: return PARTY_TYPES[elem]
            

def get_wallet_address(ptype: str, moniker: str):
    '''
    Get wallet's address by its moniker in an off-chain way
    ------ 
    Args:
        ptype(str): party's type (operator, manufacturer, supplier, or location)
        moniker(str): party's moniker 

    Output:
        (str): party's address
    '''
    if ptype == 'operator':
        for elem in operators:
            if elem['moniker'] == moniker: return elem['address']
    elif ptype == 'manufacturer':
        for elem in manufacturers:
            if elem['moniker'] == moniker: return elem['address']
    elif ptype == 'supplier':
        for elem in suppliers:
            if elem['moniker'] == moniker: return elem['address']
    elif ptype == 'location':
        for elem in locations:
            if elem['moniker'] == moniker: return elem['address']


# DataTable
def get_column(ptype: str):
    '''
    Return the related address column based on party type,
    work for DataTable in Tab2 
    ------ 
    Args: 
        ptype(str): party's type (operator, manufacturer, supplier, or location)
    Output: 
        (str): related address column's header
    '''
    if ptype == 'operator': return 'op_addr'
    elif ptype == 'manufacturer': return 'ma_addr'
    elif ptype == 'supplier': return 'su_addr'
    elif ptype == 'location': return 'lo_addr'


# Heatmap
def heatmap_helper():
    '''
    Return parameters for building the heatmap
    ------ 
    Args:
        None 

    Output:
        whole_op_list(list): a list of distinct operators' monikers
        whole_vm_list(list/matrix): a matrix of vm_ids of all vending machines in an order for heatmap visualization 
        whole_tx_list(list/matrix): a matrix of transaction amounts of all vending machines in an order for heatmap visualization 
    '''

    conn = sql_connection(sqlite_file)
    c = conn.cursor()

    c.execute("SELECT DISTINCT operator FROM transactions ORDER BY operator")
    distinct_ops = c.fetchall()
    whole_op_list = []
    whole_vm_list = []
    whole_tx_list = []
    for (op,) in distinct_ops:
        whole_op_list.append(moniker_name_converter(op))
        vm_list = []
        tx_list = []
        for unit in vm_units:
            if unit['operator']['moniker'] == op:
                vm = unit['moniker']
                vm_id = unit['vm_id']
                vm_list.append(vm_id)
                c.execute("SELECT COUNT(*) FROM transactions WHERE operator = ? AND vending_machine = ?", (op, vm))
                tx_list.append(c.fetchone()[0])
        whole_vm_list.append(vm_list)
        whole_tx_list.append(tx_list)

    return whole_op_list, whole_vm_list, whole_tx_list