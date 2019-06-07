import subprocess
import sys
import tkinter as tk, threading
from tkinter import font as tkfont
import time

class DrivingMode(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self.configure(background='#67BFFF')
        # label = tk.Label(self, text="Driving Mode", font=controller.title_font,bg='#67BFFF')
        # label.pack(side="top", fill="x", pady=10)

        labelframe1 = tk.LabelFrame(self, text="Driving Mode", bg='#67BFFF')
        labelframe1.pack(fill="both", expand="yes")
        labelframe1.place(anchor="c", relx=.5, rely=.5)

        text_font = tkfont.Font(family='Helvetica', size=25, weight="bold", slant="italic")
        top_label = tk.Label(labelframe1, text="The simulation will begin soon...", font=text_font,bg='#67BFFF')
        top_label.pack()

        self._parameters = [self._controller.bash_path]

        self.bind("<<"+self.__class__.__name__+">>", self._event_call)

    def run(self):
        command = self._parameters
        print(command)
        subprocess.run(command, stdout=sys.stdout, stderr=subprocess.PIPE)
        time.sleep(self._controller.timeout_DrivingMode)
        self._controller.show_frame("DrivingSummary")

    def _event_call(self, event):
        print(self.__class__.__name__)
        print("event -> "+str(event))
        self._thread = threading.Thread(target=self.run)
        self._thread.daemon = 1
        self._thread.start()