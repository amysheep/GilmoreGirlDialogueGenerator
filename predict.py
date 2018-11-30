#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 11:07:23 2018

@author: ayang
"""


from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM



# define model 


#def create_model():
#   model = Sequential()
#   model.add(LSTM(128, input_shape=(maxlen, len(chars))))
#   model.add(Dense(len(chars)))
#   model.add(Activation('softmax'))
#   return model



#from keras.models import save_model as save_keras_model
from keras.models import load_model
import json
import pandas as pd
import numpy as np
import sys
#save_keras_model(self.model, os.path.join(saving_staging_directory, 'model.hdf5'))
#model = create_model()
actor = input("Rory or Lorelai?")
if actor == 'Rory':
    model = load_model("weights.hdf5")
else: model = load_model("weights_lorelai.hdf5")






#from lstmmodel.sample import sample
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
        
rorysubset = [item for item in data if item['actor'] == 'RORY']
lorelaisubset = [item for item in data if item['actor'] == 'LORELAI']


rory = pd.DataFrame(rorysubset)
lorelai = pd.DataFrame(lorelaisubset)

roryline = rory.line

n_messages = len(roryline)
n_chars = len(' '.join(map(str, roryline)))



roryline = ' '.join(map(str, roryline)).lower()

chars = sorted(list(set(roryline)))
#print('Count of unique characters (i.e., features):', len(chars))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))


##### create pred_x
predtext= input('Give me 40 characters: ')
maxlen=len(predtext)
for diversity in [0.2, 0.5, 1.0, 1.2]:
            print('----- diversity:', diversity)

            generated = ''
            sentence = predtext
            generated += sentence
            print('----- Generating with seed: "' + sentence + '"')
            sys.stdout.write(generated)

            for i in range(400):
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