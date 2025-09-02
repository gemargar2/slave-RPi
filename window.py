import matplotlib.pyplot as plt
from collections import deque

xmax = 40 # seconds
smax = 400 # samples
time_interval = 0.1

class Window_class:

	def __init__(self):
		# --- init plot --------------
		self.fig = plt.figure(figsize=(8, 3.5))
		
		mngr = plt.get_current_fig_manager()
		mngr.window.geometry("+50+100")
		self.fig.suptitle('Slave 1 PPC')

		# create axis
		self.ax1 = self.fig.add_subplot(121)
		self.ax2 = self.fig.add_subplot(122)

		# Set titles of subplots
		self.ax1.set_title('Active Power Setpoints')
		self.ax2.set_title('Reactive Power Setpoints')

		# set label names
		self.ax1.set_xlabel("t")
		self.ax1.set_ylabel("(p.u)")
		self.ax2.set_xlabel("t")
		self.ax2.set_ylabel("(p.u)")

		# enable grid
		self.ax1.grid(True)
		self.ax2.grid(True)

		# set axis limits
		self.ax1.set_xlim(0, xmax)
		self.ax1.set_ylim(-0.1, 1.1)
		self.ax2.set_xlim(0, xmax)
		self.ax2.set_ylim(-0.4, 0.4)

		self.ln11, = self.ax1.plot([], [], "r-", label='master')
		self.ln12, = self.ax1.plot([], [], "b-", label='dev1')
		self.ln13, = self.ax1.plot([], [], "g-", label='dev2')
		self.ax1.legend(handles=[self.ln11, self.ln12, self.ln13])

		self.ln21, = self.ax2.plot([], [], "r-", label='master')
		self.ln22, = self.ax2.plot([], [], "b-", label='dev1')
		self.ln23, = self.ax2.plot([], [], "g-", label='dev2')
		self.ax2.legend(handles=[self.ln21, self.ln22, self.ln23])

		self.fig.tight_layout(pad=2.0)
		# self.fig.subplots_adjust(
		#     top=0.981,
		#     bottom=0.049,
		#     left=0.042,
		#     right=0.981,
		#     hspace=0.2,
		#     wspace=0.2
		# )

	# Index
	x_data = deque([], maxlen=smax)
	# Active power
	master_p_sp_data = deque([], maxlen=smax)
	dev1_p_sp_data = deque([], maxlen=smax)
	dev2_p_sp_data = deque([], maxlen=smax)
	# Reactive power
	master_q_sp_data = deque([], maxlen=smax)
	dev1_q_sp_data = deque([], maxlen=smax)
	dev2_q_sp_data = deque([], maxlen=smax)

	def plot_data(self, x, obj):
		# Index
		self.x_data.append(x)
		# Active power
		self.master_p_sp_data.append(obj.master_p_in_sp)
		self.dev1_p_sp_data.append(obj.dev_p_sp[0])
		self.dev2_p_sp_data.append(obj.dev_p_sp[1])
		# Reactive power
		self.master_q_sp_data.append(obj.master_q_in_sp)
		self.dev1_q_sp_data.append(obj.dev_q_sp[0])
		self.dev2_q_sp_data.append(obj.dev_q_sp[1])

		# Plot stuff 
		# Active power
		self.ln11.set_data(self.x_data, self.master_p_sp_data)
		self.ln12.set_data(self.x_data, self.dev1_p_sp_data)
		self.ln13.set_data(self.x_data, self.dev2_p_sp_data)
		# Active power
		self.ln21.set_data(self.x_data, self.master_q_sp_data)
		self.ln22.set_data(self.x_data, self.dev1_q_sp_data)
		self.ln23.set_data(self.x_data, self.dev2_q_sp_data)

		# Slide window
		if x>=xmax:
			# Active power
			self.ln11.axes.set_xlim(x-xmax, x)
			self.ln12.axes.set_xlim(x-xmax, x)
			self.ln13.axes.set_xlim(x-xmax, x)
			# Reactive power
			self.ln21.axes.set_xlim(x-xmax, x)
			self.ln22.axes.set_xlim(x-xmax, x)
			self.ln23.axes.set_xlim(x-xmax, x)
        
		# Emulate FuncAnimation
		plt.pause(time_interval) # 1/20Hz = 0.05 s (TG3, section 6.1.1, p.132)
