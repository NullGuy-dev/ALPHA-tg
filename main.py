# import frameworks and libraries
import numpy as np
import re
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Input, Dense, Embedding, LSTM, Dropout, Bidirectional, GlobalMaxPooling1D
from tensorflow.keras.models import Sequential, load_model

def preproc_text(text): # method for text preproc'ing
    text = re.sub(r',', '', text)
    text = re.sub(r'\'', '', text)
    text = re.sub(r'\"', '', text)
    text = re.sub(r'\(', '', text)
    text = re.sub(r'\)', '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'“', '', text)
    text = re.sub(r'”', '', text)
    text = re.sub(r'’', '', text)
    text = re.sub(r'\.', '', text)
    text = re.sub(r';', '', text)
    text = re.sub(r':', '', text)
    text = re.sub(r'\-', '', text)
    return text

with open("dataset.txt", "r", encoding="utf8") as f:
    data = f.read().lower().splitlines() # get values from dataset-file

# preproc'ing our data
pre_final = ''
for l in data:
    l = preproc_text(l)
    pre_final += '\n'+l
final = pre_final.split('\n')

# creating tokenizer's class for nn
max_voc = 100000
tok = Tokenizer(num_words=max_voc)
tok.fit_on_texts(final)

w2id = tok.word_index
voc_size = len(w2id)+1

# convert data to sequences with tokenizer's class
in_seq = []
for l in final:
    ltok = tok.texts_to_sequences([l])[0]
    for i in range(1, len(ltok)):
        ngs = ltok[:i+1]
        in_seq.append(ngs)

# data's distribution for nn
max_seq_len = max(len(x) for x in in_seq)
in_seq = np.array(pad_sequences(in_seq, maxlen=max_seq_len, padding='pre'))
xs = in_seq[:, :-1]
labels = in_seq[:, -1]
ys = to_categorical(labels, num_classes=voc_size)

def train(epochs=50): # function for creating, training and saving or model
    # creating model
    model = Sequential([
        Embedding(voc_size, 124, input_length=max_seq_len-1),
        Dropout(0.2),
        LSTM(520, return_sequences=True),
        Bidirectional(LSTM(340, return_sequences=True)),
        GlobalMaxPooling1D(),
        Dense(1024, activation='relu'),
        Dense(voc_size, activation='softmax')
    ])

    model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy']) # preparation for training
    model.fit(xs, ys, epochs=epochs) # model's training
    model.save('alpha-tg.h5') # model's saving

def use(seed, no_words, model): # function for using model
    # model = load_model("alpha-tg.h5")
    for i in range(no_words): # preproc'ing data for working with nn
        ltok = tok.texts_to_sequences([seed])[0]
        ltok = pad_sequences([ltok], maxlen=max_seq_len-1, padding='pre')
        predicted = np.argmax(model.predict(ltok), axis=1)
        nw = ''
        for w, i in tok.word_index.items():
            if predicted == i:
                nw = w
                break
        seed += ' ' + nw
        print(seed) # show result