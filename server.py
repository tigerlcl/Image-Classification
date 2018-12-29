# A TCP server

import sys
import socket
import base64
import json
import numpy as np
import tensorflow as tf
from queue import Queue
from threading import Thread
from concurrent.futures import ProcessPoolExecutor
from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions

def server_client(queue):
    # start receiving data from client
    while not queue.empty():
        client_socket, address = queue.get()
        print("Serving client on {}".format(address))
        parts = []
        while True:
            part = client_socket.recv(1024).decode("utf-8")
            if '##END##' in part :
                parts.append(part[:-7])
                break
            parts.append(part)
        parts = "".join(parts) # concate all parts

        #extract (load) JSON data
        encoded_image = json.loads(parts)['image']
        chat_id = json.loads(parts)['chat_id']
        print('chat_id of client:',chat_id)
        #decode image data
        image_data = base64.b64decode(encoded_image)
        with open('image.png', 'wb') as outfile:
            outfile.write(image_data)

        # Preprocess the image
        img_path = 'image.png'
        img = image.load_img(img_path, target_size=(224, 224, 3))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        # Feed the image into the neural network
        with graph.as_default():
            preds = model.predict(x)

        # Decode the prediction into labels and take the top 5 predicted labels
        decoded = decode_predictions(preds, top=5)[0]

        # Initialize a dict to store predictions
        data = {'predictions': [],'chat_id' : chat_id}
        for i, (label_id, label, proba) in enumerate(decoded):
            proba = '%.4f'% proba
            output = {'top':i+1, 'label':label, 'proba':str(proba)}
            data['predictions'].append(output)

        #encode msg in JSON, then return to client
        data = json.dumps(data)+'##END##'
        client_socket.sendall(data.encode('utf-8'))
        client_socket.close()

if __name__ == "__main__":
    # Initialize a ResNet50 model
    # Pre-trained weights will be downloaded automatically
    model = ResNet50(weights='imagenet')
    # tensorflow reference
    graph = tf.get_default_graph()
    # define port number for listening
    port = 50001
    # create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket object to a socket in PC
    server_socket.bind((socket.gethostname(),port))
    # listen for incoming connection from clients
    server_socket.listen(10)
    print('server is listening...')
    queue_3 = Queue()

    while True:
        client_socket, address = server_socket.accept()
        queue_3.put((client_socket, address))
        client_thread = Thread(target = server_client, args=(queue_3,))
        client_thread.daemon = True
        client_thread.start()
