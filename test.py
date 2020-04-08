import pandas as pd
import numpy as np
import json
from collections import Counter

# load data
data = pd.read_csv('all_products.csv')

#separate resions
items_france = data[data['region']=='fr']
items_states = data[data['region']=='us']

# find products quantity
n_items_france = len(items_france)
n_items_states = len(items_states)

# check currency
currency_fr = all(items_france['currency'] == 'EUR')
currency_us = all(items_states['currency'] == 'USD')

#find intersections
n_intersections = len(pd.Series(np.intersect1d(items_france['sku'],items_states['sku'])))
sku_set = pd.unique(data['sku'])
intersection_percent = str(round((n_intersections/len(sku_set)) * 100)) + '%'

#find value percentage

def value_percentage(category):
    list_size = data[category].tolist()
    list_string = ','.join(list_size)
    new_list_size = list_string.split(',')
    c = Counter(new_list_size)
    return [(i, round(c[i] / len(list_size) * 100.0, 2)) for i, count in c.most_common()]

size_percentage = value_percentage('size')
color_percentage = value_percentage('color')

# find percentage of available variants

france_variants = round(items_france['availability'].value_counts(normalize=True) * 100, 2).to_dict()
us_variants = round(items_states['availability'].value_counts(normalize=True) * 100, 2).to_dict()

test_results = {'N_items_France': n_items_france,
        'N_items_US': n_items_states,
        'France_currency_correct': currency_fr,
        'US_currency_correct': currency_us,
        'Intersections': intersection_percent,
        'Percent of sizes': size_percentage,
        'Percent of color': color_percentage,
        'Percentage of available variants in France': france_variants,
        'Percentage of available variants in US': us_variants}

with open('test.json', 'w') as t:
    json.dump(test_results, t)
