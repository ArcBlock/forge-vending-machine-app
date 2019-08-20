import os
from random import randrange

import yaml
from conf import fixture_path


def sku_generator(num: int):
    '''
    Generate a list of dict on sku's info (name and value), and save as yaml
    ------
    Args:
        num(int): the number of sku wanted to generate

    Output:
        create `fixtures/sku.yml`
    '''

    data = []

    for i in range(num):
        # e.g. name = 'sku001'
        name = "sku" + str(i + 1).zfill(3)
        # e.g. value = a random number
        value = randrange(1, 6)  # generate random int from 1 to 5

        sku_data = dict(
            sku=name,
            value=value,
        )

        data.append(sku_data)

    with open(os.path.join(fixture_path, 'sku.yml'), 'w') as outfile:
        yaml.dump(data, outfile, explicit_start=True)
