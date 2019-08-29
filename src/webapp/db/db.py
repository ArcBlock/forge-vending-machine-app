import logging
import sqlite3
import sys
sys.path.append('./src')

from time import sleep
from utils.chain import get_current_txs_info
from utils.wallets import parties_moniker_name, VM_DICT, SKU_DICT
from sqlite3 import Error


# set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db")


sqlite_file = 'src/webapp/db/vending_machine.sqlite'


def sql_connection(sqlite_file: str):
    '''
    Connect to database 
    '''

    try:
        return sqlite3.connect(sqlite_file)
    except Error:
        print(Error)


def sql_table(c, conn):
    '''
    Create table called transactions
    '''

    c.execute("""CREATE TABLE IF NOT EXISTS transactions(
        hash text PRIMARY KEY,
        vending_machine text,
        vm_id text,
        vm_addr text,
        item text,
        item_id text,
        price integer,
        time numeric,
        operator text,
        op_com text,
        op_addr text,
        manufacturer text,
        ma_com text,
        ma_addr text,
        supplier text,
        su_com text,
        su_addr text,
        location text,
        lo_com text,
        lo_addr text,
        lo_lat text,
        lo_lng text)""")
    conn.commit()


def sql_insert(c, conn, entities):
    '''
    Insert data into the table
    '''

    c.execute(
        'INSERT OR IGNORE INTO transactions VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', entities)
    conn.commit()


def main():
    '''
    Main function,
    update the database periodically (every 10s)
    '''

    conn = sql_connection(sqlite_file)
    c = conn.cursor()

    sql_table(c, conn)
    db_height = 0

    # insert data
    while True:
        data, db_height = get_current_txs_info(db_height)        
        for d in data:
            vm_id = VM_DICT['{}'.format(d['vm'])]
            sku_id = SKU_DICT['{}'.format(d['sku'])]
            op_com = parties_moniker_name['operator']['{}'.format(d['op'])]
            ma_com = parties_moniker_name['manufacturer']['{}'.format(d['ma'])]
            su_com = parties_moniker_name['supplier']['{}'.format(d['su'])]
            lo_com = parties_moniker_name['location']['{}'.format(d['lo'])][0]
            lo_lat = parties_moniker_name['location']['{}'.format(d['lo'])][1]
            lo_lng = parties_moniker_name['location']['{}'.format(d['lo'])][2]
            entities = (d['hash'], d['vm'], vm_id, d['vm_addr'], d['sku'], sku_id, d['price'], d['time'], d['op'], op_com,
                        d['op_addr'], d['ma'], ma_com, d['ma_addr'], d['su'], su_com, d['su_addr'], d['lo'], lo_com, d['lo_addr'], lo_lat, lo_lng)
            logger.debug(entities)
            sql_insert(c, conn, entities)
        logger.info(f"db_height is {db_height}")
        sleep(3)



if __name__ == '__main__':
    main()
