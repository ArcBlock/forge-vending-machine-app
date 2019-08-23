import logging
import sys
sys.path.append('./src')

from forge_sdk import protos, utils
from utils.chain import rpc, get_current_txs_info


# set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_helpers")

