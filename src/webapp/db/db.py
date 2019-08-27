import logging
import sqlite3
import sys
sys.path.append('./src')

from time import sleep
from utils.chain import get_current_txs_info
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
        vm_addr text,
        item text,
        price integer,
        time numeric,
        operator text,
        op_addr text,
        manufacturer text,
        ma_addr text,
        supplier text,
        su_addr text,
        location text,
        lo_addr text)""")
    conn.commit()


def sql_insert(c, conn, entities):
    '''
    Insert data into the table
    '''

    c.execute(
        'INSERT OR IGNORE INTO transactions VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', entities)
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
            entities = (d['hash'], d['vm'], d['vm_addr'], d['sku'], d['price'], d['time'], d['op'],
                        d['op_addr'], d['ma'], d['ma_addr'], d['su'], d['su_addr'], d['lo'], d['lo_addr'])
            logger.debug(entities)
            sql_insert(c, conn, entities)
        logger.info(f"db_height is {db_height}")
        sleep(3)



if __name__ == '__main__':
    main()
