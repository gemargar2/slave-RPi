import threading
from slave_class import *
from send_receive import *
from window import Window_class

printMessages = False

def plotStuff(i, window_obj, slave_obj):
	x = i/10
	window_obj.plot_data(x, slave_obj)

def main():
	with open('config.json', 'r') as openfile:
		config = json.load(openfile)

	# Create objects
	slave_obj = Slave_class(config)
	window_obj = Window_class()

	# Start parallel processes
	signals_receive = threading.Thread(target = signals_rx, args=(slave_obj, window_obj))
	signals_receive.start()
	signals_send = threading.Thread(target = signals_tx, args=(slave_obj,))
	signals_send.start()

	# Plot data
	i = 0
	while True:
		plotStuff(i, window_obj, slave_obj)
		i += 1

if __name__ == "__main__":
	main()
