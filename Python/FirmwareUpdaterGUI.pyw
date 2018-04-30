import time
import serial

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import orion5
from orion5.utils import update
from orion5.utils.general import ComQuery

class FirmwareUpdater(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.progress_var = DoubleVar()
        self.orion5_status = StringVar()
        self.firmware_status = StringVar()
        self.main_status = StringVar()

        self.state = 0
        self.orion = None
        self.com_port = None
        self.file_path = ""

        self.title("Orion5 - Firmware Updater")
        self.resizable(False, False)

        # Main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(column=0, row=0)
        self.main_frame.rowconfigure(2, minsize=40)

        # Main status
        self.main_label = ttk.Label(self.main_frame, textvariable=self.main_status, justify="center")
        self.main_label.grid(column=0, row=2, columnspan=6, padx=5, pady=5, sticky=(N, S))

        # Orion5 status
        self.orion5_label = ttk.Label(self.main_frame, textvariable=self.orion5_status, justify="left")
        self.orion5_label.grid(column=0, row=0, columnspan=5, padx=5, pady=5, sticky=W)

        self.refresh_button = ttk.Button(self.main_frame, text="Refresh", command=self.find_Orion5)
        self.refresh_button.grid(column=5, row=0, columnspan=1, padx=5, pady=5, sticky=E)

        # Firmware status
        self.firmware_label = ttk.Label(self.main_frame, textvariable=self.firmware_status, justify="left")
        self.firmware_label.grid(column=0, row=1, columnspan=5, padx=5, pady=5, sticky=W)

        self.browse_button = ttk.Button(self.main_frame, text="Browse", command=self.browse)
        self.browse_button.grid(column=5, row=1, columnspan=1, padx=5, pady=5, sticky=E)

        # Firmware updating bits
        self.progress = ttk.Progressbar(self.main_frame, orient="horizontal", mode="determinate", length=400, variable=self.progress_var, maximum=100)
        self.progress.grid(column=0, row=3, columnspan=6, padx=5, pady=5)

        self.start_button = ttk.Button(self.main_frame, text="Start", command=self.flash, state='disabled')
        self.start_button.grid(column=2, row=4, columnspan=3, padx=5, pady=5, sticky=(E, W))

        self.checkbox_status = StringVar()
        self.checkbox = ttk.Checkbutton(self.main_frame, text='Bootloader?', command=self.check, variable=self.checkbox_status, onvalue='1', offvalue='0')
        self.checkbox.grid(column=0, row=4, padx=5, pady=5)

        self.orion5_status.set("Refresh to connect to Orion5")
        self.firmware_status.set("Select a firmware file")
        self.main_status.set("Connect to Orion5 and select firmware file")

    def check(self):
        self.state = int(self.checkbox_status.get())
        self.check_ready()

    def find_Orion5(self):
        self.orion5_status.set("Looking for Orion5...")
        comport = ComQuery()
        if comport is not None:
            self.com_port = str(comport.device)
            self.orion5_status.set("Found Orion5 at " + self.com_port)
            if self.state == 0:
                self.orion = orion5.Orion5(self.com_port)
            self.check_ready()
        else:
            self.com_port = None
            self.orion5_status.set("Unable to find Orion5...")

    def browse(self):
        self.file_path = filedialog.askopenfilename(initialdir=".", title="Select Firmware File", filetypes=(("BIN files", "*.bin"),))
        if len(self.file_path) > 0:
            self.firmware_status.set(self.file_path.split('/')[-1])
            self.check_ready()

    def check_ready(self):
        if self.com_port is not None and self.file_path != '':
            self.start_button.config(state="normal")
            if self.state == 0:
                self.main_status.set("Ready to start")
                self.start_button.config(text="Start")
            elif self.state == 1:
                self.main_status.set("Ready to flash")
                self.start_button.config(text="Flash")
        else:
            self.start_button.config(state="disabled")

    def flash(self):
        if self.state == 0:
            self.progress_var.set(0)
            self.orion.setVariable('firmwareUpdate', 1)
            time.sleep(0.25)
            self.orion.setVariable('firmwareUpdate', 1)
            time.sleep(2)
            self.main_status.set('Power cycle Orion5')
            self.orion.exit()
            self.orion5_status.set('Click refresh to reconnect')
            self.com_port = None
            self.check_ready()
            self.state = 1
        elif self.state == 1:
            s = serial.Serial(port=self.com_port, baudrate=500000, write_timeout=0, timeout=30)
            update(s=s, filename=self.file_path, callback=self.flashing_callback, output=False)
            self.start_button.config(state="disabled")
            self.refresh_button.config(state="disabled")
            self.browse_button.config(state="disabled")

    def flashing_callback(self, status, index, total):
        self.progress.config(maximum=total)
        self.progress_var.set(index)
        self.main_status.set(status)
        self.update()

    def on_closing(self):
        try:
            self.orion.exit()
        except:
            pass
        self.destroy()

app = FirmwareUpdater()
app.mainloop()
