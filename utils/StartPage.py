import tkinter as tk
from PIL import Image, ImageTk
import random


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self.configure(background='#67BFFF')
        label = tk.Label(self, text="Welcome to CARLA ScenarioRunner v1.0", font=controller.title_font,bg='#67BFFF')
        label.pack(side="top", fill="x", pady=10)

        simage = Image.open("car.png")
        sphoto = ImageTk.PhotoImage(simage)
        slabel = tk.Label(image=sphoto)
        slabel.image = sphoto
        self.button1 = tk.Button(self, image=sphoto, text="Start Scenario (\u21b5)", compound=tk.TOP, command=lambda: controller.show_frame("ExperimentInfo"), font=controller.title_font,bg='#FF9A2E')

        self.button1.focus()
        self.button1.pack()
        self.button1.place(anchor="c", relx=.5, rely=.5)

        self.bind("<<"+self.__class__.__name__+">>", self._event_call)
        self.bind('<Return>', self.start_experiment)

    def start_experiment(self, event):
        self._controller.show_frame("ExperimentInfo")

    def _event_call(self, event):
        self.button1.focus_set()
        key = random.choice(list(self._controller.map_of_scenarios.keys()))
        self._controller.selected_scenario = self._controller.map_of_scenarios[key]
