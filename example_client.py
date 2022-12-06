from core.client import ClientManager
from core.utils.mixins import (
    post_connect,
    post_close
)
import time
import socket

if __name__ == '__main__':
    # import time
    time.sleep(1)
    client = ClientManager('asd')
    client.new_connection(1, (socket.gethostname(), 56213))
    client.send_message(1, 'qewqwefqwef')
    client.send_message(1, 'qewqwefqwef')
    print('slepping in 2')
    time.sleep(2)
    print('done sleep')
    client.send_message(1, 'qewqwefqwef')
    client.send_message(1, 'qewqwefqwef')
    time.sleep(1)
    client.send_message(1, 'qewqwefqwef')

    client.disconnect_all()
