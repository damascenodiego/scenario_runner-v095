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

        simage = Image.open("utils/images/car.png")
        sphoto = ImageTk.PhotoImage(simage)
        slabel = tk.Label(image=sphoto)
        slabel.image = sphoto
        self.button1 = tk.Button(self,
                                 image=sphoto,
                                 text="Start Scenario (\u21b5)",
                                 compound=tk.TOP,
                                 command=lambda: controller.show_frame("ExperimentInfo"),
                                 font=controller.title_font,bg='#FF9A2E')

        self.button1.focus()
        self.button1.pack()
        self.button1.place(anchor="c", relx=.5, rely=.5)

        self.curr_scenario = 0
        self.list_of_scenarios = list(self._controller.map_of_scenarios.keys())
        self.bind("<<"+self.__class__.__name__+">>", self._event_call)

    def start_experiment(self, event):
        self._controller.show_frame("ExperimentInfo")

    def _event_call(self, event):
        print(self.__class__.__name__)
        # print("event -> "+str(event))
        self._controller.csv_size = self._controller.file_len("score.csv")
        key = self.list_of_scenarios[self.curr_scenario % len(self.list_of_scenarios)]
        self.curr_scenario += 1
        # key = self.list_of_scenarios[self.curr_scenario %]
        # print(list(self._controller.map_of_scenarios.keys()))
        print("Selected scenario: {}".format(key))
        self._controller.selected_scenario = self._controller.map_of_scenarios[key]
        self.button1.focus()
        self.button1.focus_set()
        self.button1.focus_force()
