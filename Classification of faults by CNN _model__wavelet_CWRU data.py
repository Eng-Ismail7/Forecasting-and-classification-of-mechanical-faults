# -*- coding: utf-8 -*-
"""Copy of CNN CWRU wavelet.Model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14TgwQaGPHOwkaNdhjAFHDtQANf01agyF
"""

import tensorflow as tf
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras import layers
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt
import pandas as pd
import pywt
import seaborn as sns
import sklearn
from sklearn.model_selection import train_test_split

print("Tensorflow version: ", tf.__version__)
print("Numpy version: ", np.__version__)
print("Pandas version: ", pd.__version__)
print("Scikit-learn version: ", sklearn.__version__)



file = np.load('/content/drive/MyDrive/CWRU.zip') # Give path to downloaded file in your system
print(file.files)



data = file['CWRU files/signal_data']
labels = file['CWRU files/signal_data_labels']
print(data.shape, labels.shape)
plt.plot(data[0]);

data =data.reshape(-1,40,40)
print(data.shape)
plt.plot(data[0]);

data = data.reshape(-1, 1600)
print(data.shape)
plt.plot(data[0])

wavelet_data = np.repeat(np.nan, repeats = 280 * 10 * 40 * 40).reshape(-1, 40, 40)
for i in range(data.shape[0]):
    segment = data[i, :]
    coefs, _ = pywt.cwt(segment, np.arange(start = 1, stop = 3201, step = 40), "morl")
    wavelet_data[i, :, :] = tf.reshape(tf.image.resize(coefs.reshape((80, 1600, 1)), (40, 40)), (40, 40))
    if (i % 100) == 0 and (i != 0):
        print(f"{i} segments processed.")

np.savez('CWRU_LOAD_CNN_wavelet_data',data = wavelet_data , labels = labels)
#file =np.load('wavelet_data.npy')
#file.file

file = np.load('/content/CWRU_LOAD_CNN_wavelet_data.npz')
print(file.files)

data =file["data"]
labels = file["labels"]
print(data.shape, labels.shape)
plt.show(data[110])

print(data[0])
print(labels)
plt.plot(labels)

category_labels = np.unique(labels)
print(category_labels)

labels = pd.Categorical(labels, categories = category_labels).codes

train_data, test_data, train_labels, test_labels = train_test_split(data, labels, test_size = 1000, stratify = labels)

train_data = train_data.reshape(len(train_data),40,40,1)
test_data = test_data.reshape(len(test_data),40,40,1)
train_labels = to_categorical(train_labels)
test_labels = to_categorical(test_labels)
#shuffle data
index = np.random.permutation(len(train_labels))
(train_data, train_labels) = (train_data[index],train_labels[index])
print(train_data.shape,train_labels.shape,test_data.shape, test_labels.shape)



demo_model = Sequential([
    layers.Conv2D(32,9,activation= 'relu', input_shape = (40,40,1)),
    layers.MaxPool2D(2),
    layers.Conv2D(32,9,activation = 'relu'),
    layers.MaxPool2D(2),
    layers.Flatten(),
    layers.Dense(64,activation = 'relu'),
    layers.Dense(96, activation = 'relu'),
    layers.Dense(10, activation = 'softmax')
])
demo_model.summary()

def create_compiled_model():
    model = Sequential([
    layers.Conv2D(32,9,activation= 'relu', input_shape = (40,40,1)),
    layers.MaxPool2D(2),
    layers.Conv2D(32,9,activation = 'relu' ),
    layers.MaxPool2D(2),
    layers.Flatten(),
    layers.Dense(64,activation = 'relu'),
    layers.Dense(96, activation = 'relu'),
    layers.Dense(10, activation = 'softmax')
    ])
    model.compile(loss = 'categorical_crossentropy', optimizer = tf.keras.optimizers.Adam(learning_rate= 0.001), 
                  metrics= ['accuracy'])
    return model

res = np.empty(10)
res[:] = np.nan
for i in range(10):
    model = create_compiled_model()
    history = model.fit (train_data,train_labels,epochs=45, batch_size = 128, verbose = 0)    # Verbosity is set to zero
    res[i] = model.evaluate(test_data, test_labels, batch_size = 128, verbose = 0)[1]          # Verbosity is set to zero
    print('Loop iteration %d, Accuracy: %4.4f' % (i+1, res[i]))
    if res[i]>=np.max(res[:(i+1)]):
        best_model = model

print('Average accuracy:%4.4f'%(np.mean(res))) # After running the model 10 times
print("Best accuracy: %4.4f"%(np.max(res)))
print("Worst accuracy: %4.4f"%(np.min(res)))
print('Standard deviation: %4.4f' % (np.std(res)))

tf.keras.models.save_model(best_model, "CWRU_CNN_raw_time_domain_data.h5")

prediction = best_model.predict(test_data)
prediction_labels = list([])
for each_prediction in prediction:
    prediction_labels.append(list(each_prediction).index(max(each_prediction)))

from sklearn.metrics import confusion_matrix
true_labels = np.argmax(test_labels, axis = 1)
matrix = confusion_matrix(true_labels, prediction_labels)

import seaborn as sns
matrix = pd.DataFrame(matrix)
plt.figure()
sns.heatmap(matrix, annot= True, fmt = "d",
           xticklabels = category_labels,
           yticklabels = category_labels, cmap = "Blues", cbar = False)
plt.xticks(rotation = 90)
plt.show()