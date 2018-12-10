#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 11:07:23 2018

@author: ayang
"""

import argparse
import json
import sys

import keras.models
import numpy as np
import pandas as pd

DIVERSITY_SAMPLES = [0.2, 0.5, 1.0, 1.2]
SEED_LENGTH = 40
SEED_CHARSET = list('abcdefghijklmnopqrstuvwxyz')


def _setup_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--role', default='rory', help='Role (Rory or Lorelai)', required=True)
    parser.add_argument('--seed', default=None, help='Random seed')
    parser.add_argument('--diversity', nargs='+', default=DIVERSITY_SAMPLES, help='Diversity')
    parser.add_argument('--output-length', default=400, type=int, help='Output sentence length')

    return parser.parse_args()


def _generate_seed():
    chars = []
    for _ in range(40):
       chars.append(np.random.choice(SEED_CHARSET))
    return ''.join(chars)


def _sample(preds, temperature=1.0):
    """
    helper function to sample an index from a probability array
    """
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


def _load_model(role):
    model_file = "weights_{}.hdf5".format(role)
    return keras.models.load_model(model_file)


def _load_lines(role):
    data = []
    with open('./scrape/script.jl') as f:
        for line in f:
            data.append(json.loads(line))

    role_subset = [item for item in data if item['actor'].lower() == role]
    role_dataframe = pd.DataFrame(role_subset)

    role_line = ' '.join(map(str, role_dataframe.line)).lower()
    chars = sorted(list(set(role_line)))
    return chars


def _main():
    args = _setup_args()

    role = (args.role).lower()
    if role not in ['rory', 'lorelai']:
        raise ValueError('Expected Rory or Lorelai')
    model = _load_model(role)
    chars = _load_lines(role)
    char_indices = dict((c, i) for i, c in enumerate(chars))
    indices_char = dict((i, c) for i, c in enumerate(chars))

    seed = args.seed or _generate_seed()
    if len(seed) > SEED_LENGTH:
        seed = seed[0:SEED_LENGTH]
    elif len(seed) < SEED_LENGTH:
        raise ValueError('Seed needs to have {} characters.'.format(SEED_LENGTH))

    div = [float(value) for value in args.diversity]

    result = {
        'role': role,
        'seed': seed,
        'diversity': div,
        'result': {}
    }

    for diversity in div:
        generated = ''
        sentence = seed

        for i in range(args.output_length):
            x_pred = np.zeros((1, SEED_LENGTH, len(chars)))
            for t, char in enumerate(sentence):
                x_pred[0, t, char_indices[char]] = 1.

            preds = model.predict(x_pred, verbose=0)[0]
            next_index = _sample(preds, diversity)
            next_char = indices_char[next_index]

            generated += next_char
            sentence = sentence[1:] + next_char

        result['result'][diversity] = generated

    print(json.dumps(result))


if __name__ == '__main__':
    _main()
