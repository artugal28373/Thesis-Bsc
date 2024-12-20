# -*- coding: utf-8 -*-
"""test_on_new_data_ Final_GDD_Transfer_Learning_Final

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1X4RPnUGFq_NQj9_Rfb1Me78942mESM1g
"""

import os
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D

# Define constants
IMAGE_SIZE = 512
NUM_CLASSES = 8

from google.colab import drive
drive.mount('/content/drive')

# Function to load images and labels
def load_data(data_dir):
    images = []
    labels = []

    c = 0

    for label in os.listdir(data_dir):
        label_path = os.path.join(data_dir, label)
        for img_file in os.listdir(label_path):
            img_path = os.path.join(label_path, img_file)
            img = cv2.imread(img_path)
            img = cv2.resize(img, (IMAGE_SIZE, IMAGE_SIZE))
            images.append(img)
            labels.append(label)
            c += 1
            if c % 100 == 0:
              print(c)

    return np.array(images), np.array(labels)

# Preprocess the data
def preprocess_data(data, labels):
    # Normalize pixel values
    data = data.astype('float32') / 255.0

    # Encode labels into numeric form
    label_encoder = LabelEncoder()
    labels_encoded = label_encoder.fit_transform(labels)

    # Convert labels to one-hot encoding
    labels_encoded = to_categorical(labels_encoded, NUM_CLASSES)

    return data, labels_encoded

data_dir = "/content/drive/MyDrive/200_data(Guava)"

# Load and preprocess the dataset

data, labels = load_data(data_dir)
data, labels = preprocess_data(data, labels)

# Split the dataset into training, validation, and test sets
X_train, X_temp, y_train, y_temp = train_test_split(data, labels, test_size=0.2, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Load the MobileNetV2 model with pre-trained weights
base_model = MobileNetV2(input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3), weights='imagenet', include_top=False)

# Freeze the base model layers
base_model.trainable = False

# Create the model architecture
model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dense(128, activation='relu'),
    Dense(NUM_CLASSES, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=10, batch_size=32)

# Evaluate the model
test_loss, test_acc = model.evaluate(X_test, y_test)
print("Test Accuracy:", test_acc)

class_names = os.listdir(data_dir)
print(class_names)

import matplotlib.pyplot as plt

# Plot training and validation loss/accuracy
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Training and Validation Loss')
plt.legend()
plt.show()

plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.legend()
plt.show()

# Predict on test data
y_pred = np.argmax(model.predict(X_test), axis=-1)

# Create confusion matrix
cm = confusion_matrix(y_test.argmax(axis=1), y_pred, labels = range(8))


# Visualize confusion matrix (using libraries like seaborn)
import seaborn as sns

sns.heatmap(cm, annot=True, fmt='d')  # Adjust formatting as needed
plt.xticks(range(len(class_names)), class_names, rotation=45)  # Rotate for better readability
plt.yticks(range(len(class_names)), class_names, rotation=45)
plt.title('Confusion Matrix')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.tight_layout()
plt.show()

from sklearn.metrics import classification_report

# Generate classification report
print(classification_report(y_test.argmax(axis=1), y_pred, target_names=class_names))

# Predict on a few samples from the test set
num = 10
predicted_classes = np.argmax(model.predict(X_test[0:num]), axis=-1)

# Visualize the test images and their corresponding predictions (using libraries like matplotlib)
for i, (img, label, pred) in enumerate(zip(X_test[:num], y_test[:num], predicted_classes)):
  plt.imshow(img[..., ::-1])  # Convert BGR to RGB for display
  print(class_names[label.argmax(axis=-1)])
  print(class_names[pred])
  plt.axis('off')
  plt.show()

