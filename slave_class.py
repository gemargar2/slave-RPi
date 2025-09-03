from numpy import zeros

printMessages = False

class Slave_class:
	def __init__(self, config):
		# Store config data locally
		self.configdata = config
		self.slave_id = int(self.configdata["device"]["ID"])
		self.S_nom = int(self.configdata["device"]["nominal_power"])
		self.devices = self.configdata["device"]["devices"]
		self.number = len(self.devices) # number of inverters
		# Inverters
		self.installed = [] # nominal power of inverters
		self.device_id = [] # ids are not used anymore
		# Contribution percentages
		self.pi_per = zeros(self.number) # percentage of contribution to the injected active power
		self.qi_per = zeros(self.number) # percentage of contribution to the injected reactive power
		self.qa_per = zeros(self.number) # percentage of contribution to the absorbed reactive power
		# Inverter signals
		self.dev_pac = zeros(self.number) # P actual
		self.dev_qac = zeros(self.number) # Q actual
		self.dev_pmax = zeros(self.number) # Pmax available
		self.dev_qmax = zeros(self.number) # Qmax available
		self.dev_qmin = zeros(self.number) # Qmin available
		self.dev_status = zeros(self.number) # Operation statusl
		self.dev_connx = zeros(self.number) # Connection status
		# Setpoints
		self.dev_p_sp = zeros(self.number) # per unit
		self.dev_q_sp = zeros(self.number) # per unit
		# Summary
		self.total_pac = 0 # MW
		self.total_qac = 0 # MVAR
		self.total_pmax = 0 # MW
		self.total_qmax = 0 # MVAR
		self.total_qmin = 0 # MVAR
		self.ippm_switch = 1 # 0=Open / 1=Closed
		self.status_ippm = 1 # 0=OFF / 1=ON
		# Master setpoints
		self.master_p_in_sp = 0
		self.master_q_in_sp = 0
		self.connect_to_devices()

	def connect_to_devices(self):
		p_sum = 0
		index = 0
		for i in self.devices:
			self.device_id.append(int(self.devices[i]["ID"]))
			self.installed.append(int(self.devices[i]["nominal_power"]))
			self.pi_per[index] = float(self.devices[i]["nominal_power"])/self.S_nom
			self.qi_per[index] = float(self.devices[i]["nominal_power"])/self.S_nom
			self.qa_per[index] = float(self.devices[i]["nominal_power"])/self.S_nom
			p_sum += int(self.devices[i]["nominal_power"])
			index += 1

		print(self.device_id)
		print(self.installed)
		print(self.pi_per)

		if p_sum != self.S_nom:
			print("Error! Sum of inverter's nominal power ratings does not match Slave's nominal power")
		else:
			print("P_sum ok")



