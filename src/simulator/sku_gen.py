import os
import random
import sys
sys.path.append('./src')
from random import randrange

import yaml
from faker import Faker

from utils.conf import fixture_path, item_names



def sku_generator(num: int):
    '''
    Generate a list of dict on sku's info (name and value), and save as yaml
    ------
    Args:
        num(int): the number of sku wanted to generate

    Output:
        create `fixtures/sku.yml`
    '''

    fake = Faker()
    data = []

    for i in range(num):
        # e.g. name = 'sku001'
        # name = "sku" + str(i + 1).zfill(3)
        # e.g. value = a random number
        value = randrange(1, 6)  # generate random int from 1 to 5

        sku_data = dict(
            sku=random.choice(item_names),
            value=value,
            barcode=str(fake.ean13()),
        )

        data.append(sku_data)

    with open(os.path.join(fixture_path, 'sku.yml'), 'w') as outfile:
        yaml.dump(data, outfile, explicit_start=True)
