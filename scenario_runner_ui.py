import os
import random
import ntpath
import tkinter as tk
from tkinter import font as tkfont
import xml.etree.ElementTree as ET
import configparser


from utils.StartPage import StartPage
from utils.ExperimentInfo import ExperimentInfo
from utils.SearchingRoute import SearchingRoute
from utils.PopulateScenario import PopulateScenario
from utils.DrivingMode import DrivingMode
from utils.DrivingSummary import DrivingSummary
from utils.Scenario import Scenario


class ScenarioRunnerApp(tk.Tk):

    timeout_ExperimentInfo   = 1
    timeout_SearchingRoute   = 1
    timeout_PopulateScenario = 1
    timeout_DrivingMode      = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Carla Scenario Runner UI")

        self.title_font = tkfont.Font(family='Arial', size=20)

        self.map_of_scenarios = {}

        self.selected_scenario = None

        config = configparser.RawConfigParser()
        config.read('scenarios.conf')

        self.bash_path = config.get('DEFAULT', 'bash_path')

        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "scenarios.list"), "r") as f:
            counter = 0
            lines = f.read().splitlines()
            for line in lines:
                print(">>"+line)
                xml_fname = ntpath.basename(line)
                self.map_of_scenarios[xml_fname] = loadXml(line)
                counter += 1

        key = random.choice(list(self.map_of_scenarios.keys()))
        self.selected_scenario = self.map_of_scenarios[key]

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, ExperimentInfo, SearchingRoute, PopulateScenario, DrivingMode, DrivingSummary):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")
        self.geometry("1400x900")  # You want the size of the app to be 500x500
        self.resizable(0, 0)  # Don't allow resizing in the x or y direction

        self.bind("<<"+self.__class__.__name__+">>", self._event_call)

    def _event_call(self, event):
        print(event)

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        frame.update()
        # print(page_name)
        frame.event_generate("<<" + page_name + ">>")


def loadXml(xml_path):
    tree = ET.parse(xml_path)
    for scenario in tree.iter("scenario"):
        name = set_attrib(scenario, "name", "Scenario example")
        town = set_attrib(scenario, "town", "Town example")
        for node in scenario.iter("description"):
            goal        = set_attrib(node, "goal", "Follow the red line and have fun!")
            description = set_attrib(node, "description", "Follow the red line!")
            criteria    = set_attrib(node, "criteria", "Do not crash!")
            timeout     = int(set_attrib(node, "timeout", 60))
            a_scenario = Scenario(
                xml_file=xml_path,
                name=name,
                description=description,
                town=town,
                goal=goal,
                timeout=timeout,
                criteria=criteria,
                snapshot=name+".mp4"
            )
            return a_scenario


def set_attrib(node, key, default):
    """
    Parse XML key for a given node
    If key does not exist, use default value
    """
    return node.attrib[key] if key in node.attrib else default

if __name__ == "__main__":
    app = ScenarioRunnerApp()
    app.mainloop()

