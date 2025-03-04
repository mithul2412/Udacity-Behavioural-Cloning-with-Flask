# -*- coding: utf-8 -*-
"""Udacity_adv_models

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13E2pnEWyh04PrjHAiskTEkslrdVK9XiM
"""

!git clone https://github.com/rslim087a/track

!ls track

!pip3 install imgaug

!pip install transformers

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import keras
from keras.models import Sequential
from keras.optimizers import Adam
from keras.layers import Convolution2D, MaxPooling2D, Dropout, Flatten, Dense
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from imgaug import augmenters as iaa
import cv2
import pandas as pd
import ntpath
import random

import tensorflow as tf
from tensorflow.keras.layers import Dense, Flatten, Input, Add, Multiply, Dropout
from tensorflow.keras.layers import LayerNormalization, Conv2D, Reshape, GlobalAveragePooling1D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.activations import gelu
from tensorflow.keras.losses import MeanSquaredError
from keras.layers import Input, Dense, Reshape, LayerNormalization, Flatten
from transformers import TFDistilBertModel, DistilBertConfig

datadir = 'track'
columns = ['center', 'left', 'right', 'steering', 'throttle', 'reverse', 'speed']
data = pd.read_csv(os.path.join(datadir, 'driving_log.csv'), names = columns)
pd.set_option('display.max_colwidth', -1)
data.head()

def path_leaf(path):
  head, tail = ntpath.split(path)
  return tail
data['center'] = data['center'].apply(path_leaf)
data['left'] = data['left'].apply(path_leaf)
data['right'] = data['right'].apply(path_leaf)
data.head()

num_bins = 25
samples_per_bin = 400
hist, bins = np.histogram(data['steering'], num_bins)
center = (bins[:-1]+ bins[1:]) * 0.5
plt.bar(center, hist, width=0.05)
plt.plot((np.min(data['steering']), np.max(data['steering'])), (samples_per_bin, samples_per_bin))

print('total data:', len(data))
remove_list = []
for j in range(num_bins):
  list_ = []
  for i in range(len(data['steering'])):
    if data['steering'][i] >= bins[j] and data['steering'][i] <= bins[j+1]:
      list_.append(i)
  list_ = shuffle(list_)
  list_ = list_[samples_per_bin:]
  remove_list.extend(list_)

print('removed:', len(remove_list))
data.drop(data.index[remove_list], inplace=True)
print('remaining:', len(data))

hist, _ = np.histogram(data['steering'], (num_bins))
plt.bar(center, hist, width=0.05)
plt.plot((np.min(data['steering']), np.max(data['steering'])), (samples_per_bin, samples_per_bin))

print(data.iloc[1])
def load_img_steering(datadir, df):
  image_path = []
  steering = []
  for i in range(len(data)):
    indexed_data = data.iloc[i]
    center, left, right = indexed_data[0], indexed_data[1], indexed_data[2]
    image_path.append(os.path.join(datadir, center.strip()))
    steering.append(float(indexed_data[3]))
    # left image append
    image_path.append(os.path.join(datadir,left.strip()))
    steering.append(float(indexed_data[3])+0.15)
    # right image append
    image_path.append(os.path.join(datadir,right.strip()))
    steering.append(float(indexed_data[3])-0.15)
  image_paths = np.asarray(image_path)
  steerings = np.asarray(steering)
  return image_paths, steerings

image_paths, steerings = load_img_steering(datadir + '/IMG', data)

# X_train, X_valid, y_train, y_valid = train_test_split(image_paths, steerings, test_size=0.2, random_state=6)
# print('Training Samples: {}\nValid Samples: {}'.format(len(X_train), len(X_valid)))

X_temp, X_test, y_temp, y_test = train_test_split(image_paths, steerings, test_size=0.2, random_state=6)
X_train, X_valid, y_train, y_valid = train_test_split(X_temp, y_temp, test_size=0.125, random_state=6) # 0.125 x 0.8 = 0.1
print('Training Samples: {}\nValidation Samples: {}\nTesting Samples: {}'.format(len(X_train), len(X_valid), len(X_test)))

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].hist(y_train, bins=num_bins, width=0.05, color='blue')
axes[0].set_title('Training set')
axes[1].hist(y_valid, bins=num_bins, width=0.05, color='red')
axes[1].set_title('Validation set')

def zoom(image):
  zoom = iaa.Affine(scale=(1, 1.3))
  image = zoom.augment_image(image)
  return image

image = image_paths[random.randint(0, 1000)]
original_image = mpimg.imread(image)
zoomed_image = zoom(original_image)

fig, axs = plt.subplots(1, 2, figsize=(15, 10))
fig.tight_layout()

axs[0].imshow(original_image)
axs[0].set_title('Original Image')

axs[1].imshow(zoomed_image)
axs[1].set_title('Zoomed Image')

def pan(image):
  pan = iaa.Affine(translate_percent= {"x" : (-0.1, 0.1), "y": (-0.1, 0.1)})
  image = pan.augment_image(image)
  return image
image = image_paths[random.randint(0, 1000)]
original_image = mpimg.imread(image)
panned_image = pan(original_image)

fig, axs = plt.subplots(1, 2, figsize=(15, 10))
fig.tight_layout()

axs[0].imshow(original_image)
axs[0].set_title('Original Image')

axs[1].imshow(panned_image)
axs[1].set_title('Panned Image')

def img_random_brightness(image):
    brightness = iaa.Multiply((0.2, 1.2))
    image = brightness.augment_image(image)
    return image

image = image_paths[random.randint(0, 1000)]
original_image = mpimg.imread(image)
brightness_altered_image = img_random_brightness(original_image)

fig, axs = plt.subplots(1, 2, figsize=(15, 10))
fig.tight_layout()

axs[0].imshow(original_image)
axs[0].set_title('Original Image')

axs[1].imshow(brightness_altered_image)
axs[1].set_title('Brightness altered image ')

def img_random_flip(image, steering_angle):
    image = cv2.flip(image,1)
    steering_angle = -steering_angle
    return image, steering_angle
random_index = random.randint(0, 1000)
image = image_paths[random_index]
steering_angle = steerings[random_index]


original_image = mpimg.imread(image)
flipped_image, flipped_steering_angle = img_random_flip(original_image, steering_angle)

fig, axs = plt.subplots(1, 2, figsize=(15, 10))
fig.tight_layout()

axs[0].imshow(original_image)
axs[0].set_title('Original Image - ' + 'Steering Angle:' + str(steering_angle))

axs[1].imshow(flipped_image)
axs[1].set_title('Flipped Image - ' + 'Steering Angle:' + str(flipped_steering_angle))

def random_augment(image, steering_angle):
    image = mpimg.imread(image)
    if np.random.rand() < 0.5:
      image = pan(image)
    if np.random.rand() < 0.5:
      image = zoom(image)
    if np.random.rand() < 0.5:
      image = img_random_brightness(image)
    if np.random.rand() < 0.5:
      image, steering_angle = img_random_flip(image, steering_angle)

    return image, steering_angle

ncol = 2
nrow = 10

fig, axs = plt.subplots(nrow, ncol, figsize=(15, 50))
fig.tight_layout()

for i in range(10):
  randnum = random.randint(0, len(image_paths) - 1)
  random_image = image_paths[randnum]
  random_steering = steerings[randnum]

  original_image = mpimg.imread(random_image)
  augmented_image, steering = random_augment(random_image, random_steering)

  axs[i][0].imshow(original_image)
  axs[i][0].set_title("Original Image")

  axs[i][1].imshow(augmented_image)
  axs[i][1].set_title("Augmented Image")

def img_preprocess(img):
    img = img[60:135,:,:]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img,  (3, 3), 0)
    img = cv2.resize(img, (200, 66))
    img = img/255
    return img

image = image_paths[100]
original_image = mpimg.imread(image)
preprocessed_image = img_preprocess(original_image)

fig, axs = plt.subplots(1, 2, figsize=(15, 10))
fig.tight_layout()
axs[0].imshow(original_image)
axs[0].set_title('Original Image')
axs[1].imshow(preprocessed_image)
axs[1].set_title('Preprocessed Image')

def batch_generator(image_paths, steering_ang, batch_size, istraining):

  while True:
    batch_img = []
    batch_steering = []

    for i in range(batch_size):
      random_index = random.randint(0, len(image_paths) - 1)

      if istraining:
        im, steering = random_augment(image_paths[random_index], steering_ang[random_index])

      else:
        im = mpimg.imread(image_paths[random_index])
        steering = steering_ang[random_index]

      im = img_preprocess(im)
      batch_img.append(im)
      batch_steering.append(steering)
    yield (np.asarray(batch_img), np.asarray(batch_steering))

x_train_gen, y_train_gen = next(batch_generator(X_train, y_train, 1, 1))
x_valid_gen, y_valid_gen = next(batch_generator(X_valid, y_valid, 1, 0))

fig, axs = plt.subplots(1, 2, figsize=(15, 10))
fig.tight_layout()

axs[0].imshow(x_train_gen[0])
axs[0].set_title('Training Image')

axs[1].imshow(x_valid_gen[0])
axs[1].set_title('Validation Image')

import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, GlobalAveragePooling2D, Reshape, Flatten, LSTM, TimeDistributed, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.applications import EfficientNetB3
from tensorflow_model_optimization.sparsity.keras import prune_low_magnitude
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials

def build_pruned_model(input_shape=(5, 66, 200, 3), num_capsule=10, dim_capsule=16, num_heads=4, key_dim=64, lstm_units=64):
    pruning_params = {
        'pruning_schedule': tf.keras.optimizers.schedules.PolynomialDecay(initial_sparsity=0.0,
                                                                          final_sparsity=0.5,
                                                                          begin_step=2000,
                                                                          end_step=10000)
    }

    inputs = Input(shape=input_shape)
    x = TimeDistributed(EfficientNetB3(weights='imagenet', include_top=False))(inputs)
    x = TimeDistributed(GlobalAveragePooling2D())(x)
    x = Reshape((-1, x.shape[2]*x.shape[3]*x.shape[4]))(x)  # Adjust based on the output of TimeDistributed GAP

    # LSTM Layer for Temporal Information
    x = LSTM(lstm_units)(x)

    # Rest of the model
    x = Flatten()(x)
    x = Dense(128, activation='elu')(x)
    x = Dropout(0.5)(x)
    x = Dense(50, activation='elu')(x)
    x = Dense(10, activation='elu')(x)
    predictions = Dense(1)(x)

    pruned_model = Model(inputs=inputs, outputs=predictions)
    pruned_model.compile(loss='mse', optimizer='adam')

    return prune_low_magnitude(pruned_model, **pruning_params)

# def vision_transformer_model(input_shape=(66, 200, 3), patch_size=16, num_patches=207, d_model=64, num_heads=4, mlp_dim=128, layers=4, num_classes=1):
#     inputs = Input(shape=input_shape)

#     # Split image into patches
#     patches = Reshape((num_patches, patch_size * patch_size * 3))(inputs)

#     # Embed patches
#     patch_embeddings = Dense(d_model)(patches)

#     # Add positional embeddings here if needed

#     # Transformer Encoder Layers
#     encoded_patches = patch_embeddings
#     for _ in range(layers):
#         # Layer normalization 1
#         x1 = LayerNormalization(epsilon=1e-6)(encoded_patches)

#         # Create a multi-head attention layer
#         attention_output = MultiHeadAttention(num_heads=num_heads, key_dim=d_model)(x1, x1)

#         # Skip connection
#         x2 = Add()([attention_output, encoded_patches])

#         # Layer normalization 2
#         x3 = LayerNormalization(epsilon=1e-6)(x2)

#         # MLP
#         x3 = Dense(mlp_dim, activation='relu')(x3)
#         x3 = Dense(d_model)(x3)

#         # Skip connection 2
#         encoded_patches = Add()([x3, x2])

#     # Take the first token for regression
#     representation = Flatten()(encoded_patches)
#     outputs = Dense(num_classes)(representation)

#     # Compile the model
#     model = Model(inputs=inputs, outputs=outputs)
#     optimizer = Adam(lr=1e-3)
#     model.compile(loss='mse', optimizer=optimizer)

#     return model

# def mlp(x, hidden_units, dropout_rate):
#     for units in hidden_units:
#         x = Dense(units, activation=gelu)(x)
#         x = Dropout(dropout_rate)(x)
#     return x

# class Patches(tf.keras.layers.Layer):
#     def __init__(self, patch_size):
#         super(Patches, self).__init__()
#         self.patch_size = patch_size

#     def call(self, images):
#         batch_size = tf.shape(images)[0]
#         patches = tf.image.extract_patches(
#             images=images,
#             sizes=[1, self.patch_size, self.patch_size, 1],
#             strides=[1, self.patch_size, self.patch_size, 1],
#             rates=[1, 1, 1, 1],
#             padding='VALID',
#         )
#         patch_dims = patches.shape[-1]
#         patches = tf.reshape(patches, [batch_size, -1, patch_dims])
#         return patches

# def create_vit_classifier():
#     input_shape = (66, 200, 3)
#     patch_size = 16  # Size of the patches to be extract from the input images
#     num_patches = (input_shape[0] // patch_size) * (input_shape[1] // patch_size)
#     projection_dim = 64
#     num_heads = 4
#     transformer_units = [
#         projection_dim * 2,
#         projection_dim,
#     ]  # Size of the transformer layers
#     transformer_layers = 8
#     mlp_head_units = [2048, 1024]  # Size of the dense layers of the final classifier
#     dropout_rate = 0.1

#     inputs = Input(shape=input_shape)
#     # Create patches.
#     patches = Patches(patch_size)(inputs)
#     # Encode patches.
#     encoded_patches = Dense(projection_dim)(patches)

#     # Create multiple layers of the Transformer block.
#     for _ in range(transformer_layers):
#         # Layer normalization 1.
#         x1 = LayerNormalization(epsilon=1e-6)(encoded_patches)
#         # Create a multi-head attention layer.
#         attention_output = tf.keras.layers.MultiHeadAttention(
#             num_heads=num_heads, key_dim=projection_dim, dropout=dropout_rate
#         )(x1, x1)
#         # Skip connection 1.
#         x2 = Add()([attention_output, encoded_patches])
#         # Layer normalization 2.
#         x2 = LayerNormalization(epsilon=1e-6)(x2)
#         # MLP.
#         x3 = mlp(x2, hidden_units=transformer_units, dropout_rate=dropout_rate)
#         # Skip connection 2.
#         encoded_patches = Add()([x3, x2])

#     # Create a [batch_size, projection_dim] tensor.
#     representation = LayerNormalization(epsilon=1e-6)(encoded_patches)
#     representation = Flatten()(representation)
#     representation = Dropout(dropout_rate)(representation)
#     # Add MLP.
#     features = mlp(representation, hidden_units=mlp_head_units, dropout_rate=dropout_rate)
#     # Regression head.
#     outputs = Dense(1)(features)

#     # Create the Keras model.
#     model = Model(inputs=inputs, outputs=outputs)
#     return model

# # Create the Vision Transformer model.
# vit_model = create_vit_classifier()

# # Compile the model.
# optimizer = Adam(learning_rate=1e-4)
# vit_model.compile(optimizer=optimizer, loss=MeanSquaredError())

# # Display the model architecture.
# vit_model.summary()

class DynamicRoutingCapsuleLayer(layers.Layer):
    def __init__(self, num_capsule, dim_capsule, routings=3, **kwargs):
        super(DynamicRoutingCapsuleLayer, self).__init__(**kwargs)
        self.num_capsule = num_capsule
        self.dim_capsule = dim_capsule
        self.routings = routings

    def build(self, input_shape):
        self.kernel = self.add_weight(shape=(input_shape[1], input_shape[-1], self.num_capsule * self.dim_capsule),
                                      initializer='glorot_uniform', name='capsule_kernel')

    def call(self, inputs):
        # Define batch_size based on the shape of the inputs
        batch_size = tf.shape(inputs)[0]

        inputs_expand = K.expand_dims(inputs, 2)
        inputs_tiled = K.tile(inputs_expand, [1, 1, self.num_capsule, 1])
        inputs_hat = tf.linalg.einsum('ijkl,jlm->ijkm', inputs_tiled, self.kernel)

        b = tf.zeros([batch_size, inputs.shape[1], self.num_capsule])
        for i in range(self.routings):
            c = tf.nn.softmax(b, axis=-1)
            outputs = squash(tf.einsum('ijkl,ijk->ijl', inputs_hat, c))
            if i < self.routings - 1:
                b = b + tf.einsum('ijkl,ijl->ijk', inputs_hat, outputs)
        return outputs

def squash(vectors, axis=-1):
    s_squared_norm = K.sum(K.square(vectors), axis, keepdims=True)
    scale = s_squared_norm / (1 + s_squared_norm) / K.sqrt(s_squared_norm + K.epsilon())
    return scale * vectors

class SimpleCapsuleLayer(layers.Layer):
    def __init__(self, num_capsule, dim_capsule, **kwargs):
        super(SimpleCapsuleLayer, self).__init__(**kwargs)
        self.num_capsule = num_capsule
        self.dim_capsule = dim_capsule

    def build(self, input_shape):
        self.capsule_kernel = self.add_weight(shape=(input_shape[-1], self.num_capsule * self.dim_capsule),
                                              initializer='glorot_uniform', name='capsule_kernel')

    def call(self, inputs):
        caps_raw = K.dot(inputs, self.capsule_kernel)
        caps_raw = K.reshape(caps_raw, (-1, self.num_capsule, self.dim_capsule))
        return tf.sqrt(tf.reduce_sum(tf.square(caps_raw), axis=-1, keepdims=False) + K.epsilon())

from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Multiply, Dropout, Input

def simple_attention_block(inputs):
    """ A simple self-attention mechanism """
    x = Dense(64, activation='relu')(inputs)
    attention = Dense(1, activation='sigmoid')(x)
    multiplied = Multiply()([inputs, attention])
    return multiplied

def advanced_self_attention(x, num_heads, key_dim):
    # Advanced Self-Attention Mechanism
    attention_output = tf.keras.layers.MultiHeadAttention(num_heads=num_heads, key_dim=key_dim)(x, x)
    x = tf.keras.layers.Add()([attention_output, x])  # Skip Connection
    x = tf.keras.layers.LayerNormalization(epsilon=1e-6)(x)
    return x

# def build_enhanced_model(input_shape=(300, 300, 3)):
#     # EfficientNet Base
#     base_model = EfficientNetB3(weights='imagenet', include_top=False, input_shape=input_shape)
#     x = base_model.output
#     x = GlobalAveragePooling2D()(x)

#     # Attention Mechanism
#     x = simple_attention_block(x)

#     # Simple Capsule-Like Layer
#     x = SimpleCapsuleLayer(num_capsule=10, dim_capsule=16)(x)

#     # Dense Layers for Regression
#     x = Flatten()(x)
#     x = Dense(128, activation='elu')(x)
#     x = Dropout(0.5)(x)
#     x = Dense(50, activation='elu')(x)
#     x = Dense(10, activation='elu')(x)
#     predictions = Dense(1)(x)  # Output layer for steering angle

#     model = Model(inputs=base_model.input, outputs=predictions)
#     model.compile(loss='mse', optimizer=Adam(lr=1e-3))
#     return model

# model = build_enhanced_model()

def build_advanced_model(input_shape=(66, 200, 3), num_capsule=10, dim_capsule=16, num_heads=4, key_dim=64):
    inputs = tf.keras.Input(shape=input_shape)

    # Adjust EfficientNetB3 to accept the specified input shape
    base_model = EfficientNetB3(weights='imagenet', include_top=False, input_tensor=inputs)
    x = base_model.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)

    # Reshape for the attention and capsule layers
    x = tf.keras.layers.Reshape((1, -1))(x)  # Adjust based on the output of GlobalAveragePooling2D

    # Advanced Self-Attention Mechanism
    x = advanced_self_attention(x, num_heads, key_dim)
    x = DynamicRoutingCapsuleLayer(num_capsule=num_capsule, dim_capsule=dim_capsule)(x)
    # Flatten and final dense layers for prediction
    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(128, activation='elu')(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    x = tf.keras.layers.Dense(50, activation='elu')(x)
    x = tf.keras.layers.Dense(10, activation='elu')(x)
    predictions = tf.keras.layers.Dense(1)(x)

    model = Model(inputs=inputs, outputs=predictions)
    model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(lr=1e-3))
    return model

model = build_advanced_model()

# model = build_advanced_model()



history = model.fit(batch_generator(X_train, y_train, batch_size=100, istraining=True),
                    steps_per_epoch=300,
                    epochs=10,
                    validation_data=batch_generator(X_valid, y_valid, batch_size=100, istraining=False),
                    validation_steps=200,
                    verbose=1,
                    shuffle=1)

# Epoch 1/10
# 300/300 [==============================] - 153s 511ms/step - loss: 0.0114 - val_loss: 0.0224
# Epoch 2/10
# 300/300 [==============================] - 146s 488ms/step - loss: 0.0114 - val_loss: 0.0256
# Epoch 3/10
# 300/300 [==============================] - 145s 485ms/step - loss: 0.0116 - val_loss: 0.0162
# Epoch 4/10
# 300/300 [==============================] - 140s 469ms/step - loss: 0.0108 - val_loss: 0.0184
# Epoch 5/10
# 300/300 [==============================] - 140s 466ms/step - loss: 0.0123 - val_loss: 0.0204
# Epoch 6/10
# 300/300 [==============================] - 143s 479ms/step - loss: 0.0108 - val_loss: 0.0231
# Epoch 7/10
# 300/300 [==============================] - 140s 466ms/step - loss: 0.0089 - val_loss: 0.0175
# Epoch 8/10
# 300/300 [==============================] - 126s 420ms/step - loss: 0.0093 - val_loss: 0.0194
# Epoch 9/10
# 300/300 [==============================] - 132s 442ms/step - loss: 0.0091 - val_loss: 0.0172
# Epoch 10/10
# 300/300 [==============================] - 151s 503ms/step - loss: 0.0140 - val_loss: 0.0271



def nvidia_model():
  model = Sequential()
  model.add(Convolution2D(24, kernel_size=(5,5), strides=(2, 2), input_shape=(66, 200, 3), activation='elu'))
  model.add(Convolution2D(36, kernel_size=(5,5), strides=(2, 2), activation='elu'))
  model.add(Convolution2D(48, kernel_size=(5,5), strides=(2, 2), activation='elu'))
  model.add(Convolution2D(64, kernel_size=(3,3), activation='elu'))

  model.add(Convolution2D(64, kernel_size=(3,3), activation='elu'))

  model.add(Flatten())

  model.add(Dense(100, activation = 'elu'))

  model.add(Dense(50, activation = 'elu'))

  model.add(Dense(10, activation = 'elu'))

  model.add(Dense(1))

  optimizer = Adam(lr=1e-3)
  model.compile(loss='mse', optimizer=optimizer)
  return model

from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Input, Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

def resnet_model():
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(66, 200, 3))
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(100, activation='elu')(x)
    x = Dense(50, activation='elu')(x)
    x = Dense(10, activation='elu')(x)
    predictions = Dense(1)(x)

    model = Model(inputs=base_model.input, outputs=predictions)
    model.compile(loss='mse', optimizer=Adam(lr=1e-3))
    return model

model = resnet_model()
print(model.summary())

history = model.fit(batch_generator(X_train, y_train, 100, 1),
                              # steps_per_epoch=300,
                              epochs=10,
                              validation_data=batch_generator(X_valid, y_valid, 100, 0),
                              # validation_steps=200,
                              verbose=1,
                              shuffle=1)

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.legend(['training', 'validation'])
plt.title('Loss')
plt.xlabel('Epoch')

model.save('model(1).h5')

model.save('/content/drive/My Drive/model(1).h5')

# from google.colab import files
# files.download('model.h5')

from keras.models import load_model
model = load_model('model(1).h5')

# Evaluation on Test Data
test_generator = batch_generator(X_test, y_test, 100, 0)
test_steps = len(X_test) // 100

# Calculating the metrics
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

y_true = []
y_pred = []

for i in range(test_steps):
    x_batch, y_batch = next(test_generator)
    predictions = model.predict(x_batch)

    y_true.extend(y_batch)
    y_pred.extend(predictions.reshape(-1))

mse = mean_squared_error(y_true, y_pred)
mae = mean_absolute_error(y_true, y_pred)
r2 = r2_score(y_true, y_pred)

print(f'Mean Squared Error: {mse}')
print(f'Mean Absolute Error: {mae}')
print(f'R^2 Score: {r2}')