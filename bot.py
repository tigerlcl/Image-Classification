# a TCP client

import time
import socket
import telepot
import base64
import json
from threading import Thread
from telepot.loop import MessageLoop
from PIL import Image
from urllib import request
from queue import Queue
from io import BytesIO

def get_image(url):
    print('downloading image...')
    request.urlretrieve(url,'image.png')

def thread_2(queue):
    def image_encode(data):
        image = Image.open(data)
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        encoded_image = base64.b64encode(buffered.getvalue())
        return encoded_image

    while not queue.empty():
        image, chat_id = queue.get()
        encoded_image = image_encode(image).decode('utf-8')
        data = {'image' : encoded_image, 'chat_id': chat_id}
        data = json.dumps(data) +'##END##' # remark for end of transfer

        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((IPAddr, PORT))
        soc.sendall(data.encode('utf-8'))

        # received predictions from server
        print('collecting predictions from server...')
        parts = []
        while True:
            part = soc.recv(1024).decode('utf-8') #decode JSON data
            if '##END##' in part :
                parts.append(part[:-7]) # -7: the last 7 chars are '##END##'
                break
            parts.append(part)
        parts = json.loads("".join(parts))

        # send output into Queue_2
        queue_2.put((parts['predictions'], parts['chat_id']))
        Thread(target=thread_3, args=(queue_2,), daemon=True).start()
        soc.close()

def thread_3(queue):
    while not queue.empty():
        reply, chat_id = queue.get()
        print('get output from server...')
        messages = '' # store entire message to sent to user
        for item in reply:
            message = '{}. {} ({})'.format(item['top'],item['label'], item['proba'])
            messages = messages + message +'\n'
        bot.sendMessage(chat_id, messages)

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    # received URL for image
    if content_type == "text":
        content = msg["text"]
        get_image(content)
    elif content_type == 'photo':
        bot.download_file(msg['photo'][-1]['file_id'],'image.png')
    else:
        print('can\'t recognize, waiting for another input')

    queue_1.put(('image.png',chat_id))
    Thread(target=thread_2, args=(queue_1,), daemon=True).start()

if  __name__ == "__main__":
    queue_1 = Queue()
    queue_2 = Queue()
    # address and port are pre-defined
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    PORT = 50001

    # Provide your bot's token
    bot = telepot.Bot("Bot's Token")
    print('Initializing the bot...')
    MessageLoop(bot, handle).run_as_thread()

    while True:
        time.sleep(10)
