''' Libraries '''
import os
import numpy as np
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_virtual_device_configuration(
            gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=1024)]
        )
    except RuntimeError as e:
        print(e)



''' Parameters '''
FILE_PATH = os.path.abspath(__file__)
DIR_PATH  = os.path.dirname(FILE_PATH)
RESIZE_HEIGHT = int(os.environ.get("RESIZE_HEIGHT"))
RESIZE_WIDTH  = int(os.environ.get("RESIZE_WIDTH"))
id_to_character = {
     0: 'b',
     1: '7',
     2: 'e',
     3: '*',
     4: 'g',
     5: '0',
     6: 'i',
     7: 'c',
     8: 'k',
     9: '9',
    10: '+',
    11: 'z',
    12: 'l',
    13: 'r',
    14: 'w',
    15: '=',
    16: '1',
    17: 'n',
    18: 'o',
    19: '3',
    20: 't',
    21: 'x',
    22: 'p',
    23: '5',
    24: '8',
    25: 'v',
    26: 'h',
    27: '-',
    28: 's',
    29: 'd',
    30: 'm',
    31: '4',
    32: 'j',
    33: 'u',
    34: 'q',
    35: 'f',
    36: 'a',
    37: '/',
    38: 'y',
    39: '6',
    40: '2',
}
class_num = len(id_to_character)



''' Functions '''
class Mish(tf.keras.layers.Layer):
    def forward(self, x):
        return x * tf.nn.softplus(x).tanh()


class Detector(tf.keras.layers.Layer):
    def __init__(self):
        super(Detector, self).__init__()
        self.denses = [ tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation=Mish()),
            tf.keras.layers.Dense(32, activation=Mish()),
            tf.keras.layers.Dense(16, activation=Mish()),
            tf.keras.layers.Dense( 8, activation=Mish()),
        ]) for _ in range(4) ]
        self.detect = tf.keras.layers.Dense(class_num, activation="softmax")

    def call(self, x):
        y = tf.concat([
            tf.expand_dims(self.detect(self.denses[i](x)), axis=1) for i in range(4)
        ], axis=1)
        return y


class Model():
    def __init__(self):
        if "val_loss.h5" not in os.listdir(DIR_PATH):
            print("\nWeights file (val_loss.h5) missed, download here:\n" + 
                "https://drive.google.com/file/d/1qdB1SECI-cwqbUQNbJ834EcRAX07i4Z5/view?usp=sharing\n")
            raise Exception
        else:
            self.model = tf.keras.Sequential([
                tf.keras.layers.Conv2D(  32, 3, strides=1, padding="same", activation=tf.nn.silu),
                tf.keras.layers.MaxPool2D(padding="same"),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.Conv2D(  64, 3, strides=1, padding="same", activation=tf.nn.silu),
                tf.keras.layers.MaxPool2D(padding="same"),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.Conv2D( 128, 3, strides=1, padding="same", activation=tf.nn.silu),
                tf.keras.layers.MaxPool2D(padding="same"),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.Conv2D( 256, 3, strides=1, padding="same", activation=tf.nn.silu),
                tf.keras.layers.MaxPool2D(padding="same"),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.Conv2D( 512, 3, strides=1, padding="same", activation=tf.nn.silu),
                tf.keras.layers.MaxPool2D(padding="same"),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.Conv2D(1024, 3, strides=1, padding="same", activation=tf.nn.silu),
                tf.keras.layers.MaxPool2D(padding="same"),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dropout(0.93),
                Detector(),
            ])
            self.model.build(input_shape=(None, RESIZE_HEIGHT, RESIZE_WIDTH, 1))
            weights_path = os.path.join(DIR_PATH, "val_loss.h5")
            self.model.load_weights(weights_path)

    def predict(self, img):
        img = np.array(img, dtype=np.float)
        img = np.expand_dims(img, axis=2)
        img = np.expand_dims(img, axis=0)
        prediction = np.argmax(self.model(img), axis=2)[0]
        prediction = [ id_to_character[char] for char in prediction ]
        return prediction


    
''' Script '''
model = Model()
model.predict(np.zeros((RESIZE_HEIGHT, RESIZE_WIDTH), dtype=np.float))