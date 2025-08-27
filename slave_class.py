from numpy import zeros

printMessages = False

class Slave_class:
	def __init__(self, config):
		# Store config data locally
		self.configdata = config
		self.slave_id = int(self.configdata["device"]["ID"])
		self.P_nominal = int(self.configdata["device"]["nominal_power"])
		self.devices = self.configdata["device"]["devices"]
		self.number = len(self.devices) # number of inverters
		# Inverters
		self.installed = [] # nominal power of inverters
		self.contribution = [] # percentage of contribution to the final power output
		self.device_id = []
		self.device_state = zeros(self.number)
		self.device_p = zeros(self.number)
		self.device_q = zeros(self.number)
		self.dev_p_sp = zeros(self.number)
		self.dev_q_sp = zeros(self.number)
		# Summary
		self.slave_p = 0
		self.slave_q = 0
		self.p_avail = 0
		# Master setpoints
		self.master_p_in_sp = 0
		self.master_q_in_sp = 0
		self.connect_to_devices()

	def connect_to_devices(self):
		p_avail = 0
		for i in self.devices:
			self.device_id.append(int(self.devices[i]["ID"]))
			self.installed.append(int(self.devices[i]["nominal_power"]))
			self.contribution.append(float(self.devices[i]["nominal_power"])/self.P_nominal)
			p_avail += int(self.devices[i]["nominal_power"])

		print(self.device_id)
		print(self.installed)
		print(self.contribution)

		if p_avail != self.P_nominal:
			print("Error! Sum of inverter's nominal power ratings does not match Slave's nominal power")
		else:
			print("P_avail ok")

	def recalc_contribution(self, window_obj):
		# Recalculate available power yield
		index = 0
		new_p_avail = 0
		for i in self.devices:
			self.contribution[index] = 0.0
			if self.device_state[index] == 0:
				new_p_avail += int(self.devices[i]["nominal_power"])
			index += 1

		# Calculate new contribution
		index = 0
		for i in self.devices:
			if self.device_state[index] == 0:
				self.contribution[index] = float(self.devices[i]["nominal_power"])/new_p_avail
			index += 1
		
		self.p_avail = new_p_avail
		total_production = round(self.device_p[0] + self.device_p[1], 2)
		total_setpoint = round(self.master_p_in_sp * self.P_nominal, 2)

		if self.device_state[0] == 0: dev1_state = "ON"
		else: dev1_state = "OFF"
		if self.device_state[1] == 0: dev2_state = "ON"
		else: dev1_state = "OFF"

		slave1_str = f'Slave 1 P={total_production} / S={total_setpoint} / A={self.p_avail} / I={self.P_nominal}'
		dev1_str = f'dev1 ({dev1_state}) S={round(self.dev_p_sp[0]*self.P_nominal, 2)} / I={self.installed[0]}'
		dev2_str = f'dev2 ({dev2_state}) S={round(self.dev_p_sp[1]*self.P_nominal, 2)} / I={self.installed[1]}'
		window_obj.fig.suptitle(f'{slave1_str} \n {dev1_str} \n {dev2_str}')





