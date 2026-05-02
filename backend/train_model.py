# 1. IMPORTS
import numpy as np
import os
import tensorflow as tf
from sklearn.model_selection import train_test_split

# 2. LOAD DATA
DATA_DIR = "data"
X = []
y = []
classes = []

for idx, gesture_name in enumerate(sorted(os.listdir(DATA_DIR))):
    gesture_path = os.path.join(DATA_DIR, gesture_name)
    if not os.path.isdir(gesture_path):
        continue
    classes.append(gesture_name)
    for file in os.listdir(gesture_path):
        if file.endswith(".npy"):
            sequence = np.load(os.path.join(gesture_path, file))
            X.append(sequence)
            y.append(idx)

X = np.array(X)
y = np.array(y)

# 3. SPLIT DATA
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

print(f"Classes: {classes}")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples:  {len(X_test)}")

# 4. BUILD MODEL
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(30, 63)),
    tf.keras.layers.LSTM(128, return_sequences=True),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.LSTM(64, return_sequences=False),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dense(len(classes), activation="softmax"),
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# 5. PRINT SUMMARY
model.summary()
# 6. TRAIN
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=50,
    batch_size=32,
)

# 7. EVALUATE
test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"\nTest Accuracy: {test_acc * 100:.1f}%")

# 8. SAVE MODEL
model.save("gesture_model.h5")

import json
with open("classes.json", "w") as f:
    json.dump(classes, f)

print("Model saved as gesture_model.h5")
print("Classes saved as classes.json")