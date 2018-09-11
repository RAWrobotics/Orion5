import time
import os
import glob
import serial

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import orion5
from orion5.utils import update, signal_update
from orion5.utils.general import ComQuery

FIRMWARE_FOLDER = '../Orion5-private/Firmware'
FILENAME_FORMAT = 'Orion5_Firmware_{}_{}.bin'

if not os.path.isdir(FIRMWARE_FOLDER):
    FIRMWARE_FOLDER = '../Firmware'

class FirmwareUpdater(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.progress_var = DoubleVar()
        self.orion5_status = StringVar()
        self.main_status = StringVar()

        self.state = 0
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

        # Orion5 connection status
        self.orion5_label = ttk.Label(self.main_frame, textvariable=self.orion5_status, justify="center")
        self.orion5_label.grid(column=0, row=0, columnspan=6, padx=5, pady=5, sticky=(N, S))

        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, orient="horizontal", mode="determinate", length=400, variable=self.progress_var, maximum=100)
        self.progress.grid(column=0, row=3, columnspan=6, padx=5, pady=5)

        # Update Button
        self.start_button = ttk.Button(self.main_frame, text="Start", command=self.flash, state='disabled')
        self.start_button.grid(column=1, row=4, columnspan=4, padx=5, pady=5, sticky=(N, S))

        self.orion5_status.set("Unable to find Orion5...")
        self.main_status.set("No firmware file")

        self.wait_for_stuff()

    def wait_for_stuff(self):
        self.orion5_status.set("Looking for Orion5...")
        comport = ComQuery()
        if comport is not None:
            self.com_port = str(comport.device)
            self.orion5_status.set("Found Orion5 at " + self.com_port)
        else:
            self.com_port = None
            self.orion5_status.set("Unable to find Orion5...")

        try:
            files = glob.glob(os.path.join(FIRMWARE_FOLDER, FILENAME_FORMAT.format('*', '*')))
            max_version = max([int(x.split('_')[-2]) for x in files])
            self.file_path = os.path.join(FIRMWARE_FOLDER, FILENAME_FORMAT.format(max_version, '*'))
            self.main_status.set("Found " + os.path.basename(self.file_path))
        except ValueError as e:
            print(e)

        self.check_ready()
        self.after(500, self.wait_for_stuff)

    def check_ready(self):
        if self.com_port is not None and self.file_path != '':
            self.start_button.config(state="normal")
            self.main_status.set("Ready to update to " + os.path.basename(self.file_path))
            self.start_button.config(text="Update")
        else:
            self.start_button.config(state="disabled")

    def flash(self):
        if self.state == 0:
            # s = serial.Serial(port=self.com_port, baudrate=1000000, write_timeout=0, timeout=30)
            # signal_update(s, self.flashing_callback)
            o = orion5.Orion5(mode='standalone', serialName=self.com_port)
            o.setVariable('firmwareUpdate', 1)
            time.sleep(5)
            self.state = 1

        if self.state == 1:
            s = serial.Serial(port=self.com_port, baudrate=500000, write_timeout=0, timeout=30)
            update(s=s, filename=self.file_path, callback=self.flashing_callback, output=False)
            self.start_button.config(state="disabled")

    def flashing_callback(self, status, index, total):
        if total > 0:
            self.progress.config(maximum=total)
        self.progress_var.set(index)
        self.main_status.set(status)
        self.update()

    def on_closing(self):
        self.destroy()

app = FirmwareUpdater()
app.mainloop()
