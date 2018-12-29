# Image-Classification
using existing deep learning frameworks to classify images, deploy the service into Telegram Application

### Introduction
I will build an image classifier and then deploy the classifier as a chatbot on Telegram. Self-trained deep learning model is NOT required as the focus would be on socket programming and multi-threaded programming in Python.

You will build a system which offer image classification service via Telegram bot. A user in Telegram can either send an image or the URL of an image to the bot, and the bot will feed the image (download the image first if it is given a URL) into a deep learning model to generate image classification predictions, and then send back the result to the user.

### Implementation
1. bot.py: Continuously receiving user messages from Telegram. Whenever a message is received, if the message contains an image, or if the message’s text has an URL inside, get the binary data of the image, and send it via a TCP connection to the server. If the message does not contain an image or a URL to an image, nothing has to be done. Once classification results are received from the server, format the output and send the results back to the user
2. server.py: In the server.py script, you will need to implement a TCP server, in which there are two threads running (including the main thread). The main thread will be responsible for listening for incoming connections from clients. Once a client is connected, it should pass throught a queue the client socket to the second thread, which will communicate with the client.

Involved Model: Keras pre-trained ResNet50 model, running Tensorflow background
