"""Train the TIGMINO chatbot (same steps as chatigmino.ipynb) and copy it to the backend.

Usage, from the repository root:
    python deep-learning/train_chatbot.py
"""
import json
import pickle
import shutil
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

HERE = Path(__file__).resolve().parent
BACKEND = HERE.parent / "server-side" / "chatbot_api" / "model_info"

VOCAB_SIZE, EMBEDDING_DIM, MAX_LEN, EPOCHS = 1000, 16, 20, 300

tf.keras.utils.set_random_seed(42)
data = json.loads((HERE / "Data" / "intents.json").read_text(encoding="utf-8"))
sentences = [p for intent in data["intents"] for p in intent["patterns"]]
tags = [intent["tag"] for intent in data["intents"] for _ in intent["patterns"]]

label_encoder = LabelEncoder().fit(tags)
labels = label_encoder.transform(tags)

tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token="<OOV>")
tokenizer.fit_on_texts(sentences)
padded = pad_sequences(tokenizer.texts_to_sequences(sentences), truncating="post", maxlen=MAX_LEN)

model = Sequential([
    Embedding(VOCAB_SIZE, EMBEDDING_DIM),
    GlobalAveragePooling1D(),
    Dense(16, activation="relu"),
    Dense(16, activation="relu"),
    Dense(len(label_encoder.classes_), activation="softmax"),
])
model.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
history = model.fit(padded, np.array(labels), epochs=EPOCHS, verbose=0)
print(f"{len(sentences)} patterns, {len(label_encoder.classes_)} intents, "
      f"training accuracy {history.history['accuracy'][-1]:.2f}")

model.save(HERE / "chat_model.h5")
with open(HERE / "tokenizer.pickle", "wb") as f:
    pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)
with open(HERE / "label_encoder.pickle", "wb") as f:
    pickle.dump(label_encoder, f, protocol=pickle.HIGHEST_PROTOCOL)

for name in ("chat_model.h5", "tokenizer.pickle", "label_encoder.pickle"):
    shutil.copy2(HERE / name, BACKEND / name)
shutil.copy2(HERE / "Data" / "intents.json", BACKEND / "intents.json")
print(f"Model, tokenizer, label encoder and intents copied to {BACKEND}")
