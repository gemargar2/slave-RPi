import zmq
import threading
from time import sleep
from window import Window_class

printMessages = False

class Slave_class:
    def __init__(self):
        self.p_in_sp = 0
        self.q_in_sp = 0
        self.p_ex_sp = 0
        self.q_ex_sp = 0
        self.temp = 0
        self.tsi = 0

def plotStuff(i, window_obj, slave_obj):
    x = i/10
    window_obj.plot_data(x, slave_obj)

def master_rx(slave_obj):
    # Zero MQ is the messaging protocol used to communicate with the slave devices.
    context_rx = zmq.Context()
    socket_rx = context_rx.socket(zmq.PULL)
    socket_rx.connect("ipc:///tmp/zmqpub")
    sleep(5)

    while True:
        message = socket_rx.recv_json()
        # print(message)
        if message['value_name'] == 'P_SP_master': slave_obj.p_in_sp = float(message['value'])
        elif message['value_name'] == 'Q_SP_master': slave_obj.q_in_sp = float(message['value'])
        elif message['value_name'] == 'P_ex_sp': slave_obj.p_ex_sp = float(message['value'])
        elif message['value_name'] == 'Q_in_sp': slave_obj.q_ex_sp = float(message['value'])
        # Upon receiving a new value re-calculate
        # emulator_obj.hv_meter()

def inverter_tx(slave_obj):
    # Zero MQ is the messaging protocol used to communicate with the slave devices.
    context_tx = zmq.Context()
    socket_tx = context_tx.socket(zmq.PUSH)
    socket_tx.bind("ipc:///tmp/zmqsub")
    sleep(5)
    
    while(True):
        # Tick
        sleep(0.1)
        message1 = { "destination": "Inverter", "value": str(slave_obj.p_in_sp), "value_name": "P_SP_slave" }
        message2 = { "destination": "Inverter", "value": str(slave_obj.q_in_sp), "value_name": "Q_SP_slave" }
        try:
            socket_tx.send_json(message1, zmq.NOBLOCK)
            socket_tx.send_json(message2, zmq.NOBLOCK)
            if printMessages: print("Success")
        except:
            if printMessages: print("Failed")

def main():
    # Create objects
    slave_obj = Slave_class()
    window_obj = Window_class()

    # Start parallel processes
    master_receive = threading.Thread(target=master_rx, args=(slave_obj,))
    master_receive.start()
    inverter_send = threading.Thread(target=inverter_tx, args=(slave_obj,))
    inverter_send.start()

    # Plot data
    i = 0
    while True:
        plotStuff(i, window_obj, slave_obj)
        i += 1

if __name__ == "__main__":
    main()
