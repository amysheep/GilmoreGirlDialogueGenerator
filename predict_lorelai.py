#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 11:07:23 2018

@author: ayang
"""



from keras.models import load_model
import json
import pandas as pd
import numpy as np
import sys

model = load_model("weights_lorelai.hdf5")


def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


data = []
with open('./scrape/script.jl') as f:
    for line in f:
        data.append(json.loads(line))
        
lorelaisubset = [item for item in data if item['actor'] == 'LORELAI']
lorelai = pd.DataFrame(lorelaisubset)
lorelailine = lorelai.line

n_messages = len(lorelailine)
n_chars = len(' '.join(map(str, lorelailine)))



lorelailine = ' '.join(map(str, lorelailine)).lower()

chars = sorted(list(set(lorelailine)))
#print('Count of unique characters (i.e., features):', len(chars))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))


##### create pred_x
predtext= input('Give me 40 characters: ')
predtext=predtext.lower()[0:39]
maxlen=len(predtext)
for diversity in [0.2, 0.5, 1.0, 1.2]:
            print('----- diversity:', diversity)

            generated = ''
            sentence = predtext
            generated += sentence
            print('----- Generating with seed: "' + sentence + '"')
            sys.stdout.write(generated)

            for i in range(200):
                x_pred = np.zeros((1, maxlen, len(chars)))
                for t, char in enumerate(sentence):
                    x_pred[0, t, char_indices[char]] = 1.

                preds = model.predict(x_pred, verbose=0)[0]
                next_index = sample(preds, diversity)
                next_char = indices_char[next_index]

                generated += next_char
                sentence = sentence[1:] + next_char

                sys.stdout.write(next_char)
                sys.stdout.flush()
            print()