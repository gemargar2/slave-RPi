import threading
from time import sleep
from slave_class import *
from send_receive import *
from window import Window_class

plotFlag = True
printMessages = False
sampling_period = 0.1 # 100ms

# Slave loop
def slave_loop(slave_obj, window_obj):
	while True:
		recalc_contribution(slave_obj, window_obj)
		slave_obj.sample += 1
		slave_obj.x = slave_obj.sample*sampling_period
		sleep(sampling_period)

def main():
	with open('config.json', 'r') as openfile:
		config = json.load(openfile)

	# Create objects
	slave_obj = Slave_class(config)
	window_obj = Window_class()

	# Start parallel processes
	signals_receive = threading.Thread(target = signals_rx, args=(slave_obj, ))
	signals_receive.start()
	signals_send = threading.Thread(target = signals_tx, args=(slave_obj, ))
	signals_send.start()
	distribute = threading.Thread(target = slave_loop, args=(slave_obj, window_obj))
	distribute.start()

	# Plot data
	while True:
		if plotFlag: window_obj.plot_data(slave_obj)

if __name__ == "__main__":
	main()
