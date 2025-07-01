import matplotlib.pyplot as plt
import matplotlib

xmax = 40 # seconds

class Window_class:

    def __init__(self):
        # --- init plot --------------
        self.fig = plt.figure(figsize=(9, 4))
        
        mngr = plt.get_current_fig_manager()
        mngr.window.geometry("+50+100")
        self.fig.suptitle('Slave PPC')

        # create axis
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)
        # self.ax3 = self.fig.add_subplot(223)
        # self.ax4 = self.fig.add_subplot(224)

        # Set titles of subplots
        self.ax1.set_title('Active Power')
        self.ax2.set_title('Reactive Power')
        # self.ax3.set_title('Temperature')
        # self.ax4.set_title('Irradiance')

        # set label names
        self.ax1.set_xlabel("t")
        self.ax1.set_ylabel("P (p.u)")
        self.ax2.set_xlabel("t")
        self.ax2.set_ylabel("Q (p.u)")
        # self.ax3.set_xlabel("t")
        # self.ax3.set_ylabel(str("T (\u2103)"))
        # self.ax4.set_xlabel("t")
        # self.ax4.set_ylabel(str("TSI (W/m\u00b2)"))  

        # enable grid
        self.ax1.grid(True)
        self.ax2.grid(True)
        # self.ax3.grid(True)
        # self.ax4.grid(True)

        # set axis limits
        self.ax1.set_xlim(0, xmax)
        self.ax1.set_ylim(-0.1, 1.1)
        self.ax2.set_xlim(0, xmax)
        self.ax2.set_ylim(-0.8, 0.8)
        # self.ax3.set_xlim(0, xmax)
        # self.ax3.set_ylim(30, 40)
        # self.ax4.set_xlim(0, xmax)
        # self.ax4.set_ylim(900, 1100)

        self.ln1, = self.ax1.plot([], [], "r-", label='p_in_sp')
        self.ln2, = self.ax2.plot([], [], "r-", label='q_in_sp')
        # self.ln3, = self.ax3.plot([], [], "r-", label="temp")
        # self.ln4, = self.ax4.plot([], [], "r-", label="tsi")

        self.fig.tight_layout(pad=2.0)
        # self.fig.subplots_adjust(
        #     top=0.981,
        #     bottom=0.049,
        #     left=0.042,
        #     right=0.981,
        #     hspace=0.2,
        #     wspace=0.2
        # )
    
    p_sp_data = []
    q_sp_data = []
    temp_data = []
    tsi_data = []
    x_data = []

    def plot_data(self, x, obj):
        self.x_data.append(x)
        # P-f plots
        self.p_sp_data.append(obj.p_in_sp)
        self.q_sp_data.append(obj.q_in_sp)
        # self.temp_data.append(obj.temp)
        # self.tsi_data.append(obj.tsi)

        # Plot stuff
        self.ln1.set_data(self.x_data, self.p_sp_data)
        self.ln2.set_data(self.x_data, self.q_sp_data)
        # self.ln3.set_data(self.x_data, self.temp_data)
        # self.ln4.set_data(self.x_data, self.tsi_data)

        # Slide window
        if x>=xmax:
            self.ln1.axes.set_xlim(x-xmax, x)
            self.ln2.axes.set_xlim(x-xmax, x)
            # self.ln3.axes.set_xlim(x-xmax, x)
            # self.ln4.axes.set_xlim(x-xmax, x)
        
        # Emulate FuncAnimation
        plt.pause(0.001) # 1/20Hz = 0.05 s (TG3, section 6.1.1, p.132)
