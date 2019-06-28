import usb
import random
import sys
import tkinter as tk
from tkinter import font as tkfont
import xml.etree.ElementTree as ET
import configparser

from tkinter import messagebox

from utils.StartPage import StartPage
from utils.ExperimentInfo import ExperimentInfo
from utils.SearchingRoute import SearchingRoute
from utils.PopulateScenario import PopulateScenario
from utils.DrivingMode import DrivingMode
from utils.DrivingSummary import DrivingSummary
from utils.Scenario import Scenario
from utils.leicester_receipt import Terow_Printer


class ScenarioRunnerApp(tk.Tk):

    timeout_ExperimentInfo   = 10
    timeout_SearchingRoute   = 4
    timeout_PopulateScenario = 3
    timeout_DrivingMode      = 0
    timeout_DrivingSummary   = 15

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attributes("-zoomed", True)

        printer_is_ok = False
        self.printer = None

        while not printer_is_ok:
            try:
                self.printer = Terow_Printer()
                check_if_printer_is_ok(self.printer)
                printer_is_ok = True

            except Exception as e:
                ret = messagebox.askretrycancel("Printer error",
                                      "Wanna try again?\n\n"
                                      "Make sure the printer is\n"
                                      "on and connected to the USB!\n\n"                                      
                                      "Message:\n{}".format(e))
                print(ret)
                if not ret:
                    sys.exit(-1)

        self.title("Carla Scenario Runner UI")

        self.title_font = tkfont.Font(family='Arial', size=20)

        self.map_of_scenarios = {}

        self.selected_scenario = None

        config = configparser.RawConfigParser()
        config.read('scenarios.conf')

        self.bash_path = config.get('DEFAULT', 'bash_path')
        self.xml_path = config.get('DEFAULT', 'xml_path')

        self.csv_size = self.file_len("score.csv")


        self.map_of_scenarios = loadXml(self.xml_path)

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
        for F in (StartPage, ExperimentInfo, PopulateScenario, SearchingRoute, DrivingMode, DrivingSummary):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")
        self.geometry("1400x900")  # You want the size of the app to be 500x500
        # self.resizable(0, 0)  # Don't allow resizing in the x or y direction

        self.bind("<<"+self.__class__.__name__+">>", self._event_call)

    def _event_call(self, event):
        print(self.__class__.__name__)
        print("event -> "+str(event))


    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        frame.update()
        # print(page_name)
        frame.event_generate("<<" + page_name + ">>")


    def file_len(self, fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1


def check_if_printer_is_ok(printer):
    # This method has been created based on the
    # __init__() method from the escposprinter library
    if printer.p.device is None:
        raise Exception("Cable isn't plugged in")
    try:

        if printer.p.device.is_kernel_driver_active(0):
            try:
                printer.p.device.detach_kernel_driver(0)
            except usb.core.USBError as e:
                raise Exception("Could not detatch kernel driver: %s" % str(e))
            except Exception as e:
                raise Exception(str(e))

    except Exception as e:
        raise Exception(str(e))

    try:
        printer.p.device.set_configuration()
        printer.p.device.reset()
    except usb.core.USBError as e:
        raise Exception("Could not set configuration: %s" % str(e))


def loadXml(xml_path):
    scenarios = dict()
    tree = ET.parse(xml_path)
    for scenario in tree.iter("scenario"):
        name = set_attrib(scenario, "name", "Scenario example")
        town = set_attrib(scenario, "town", "Town example")
        type = set_attrib(scenario, "type", "Town type")
        goal = set_attrib(scenario, "goal", "Follow the red line and have fun!")
        description = set_attrib(scenario, "description", "Follow the red line!")
        criteria    = set_attrib(scenario, "criteria", "Do not crash!")
        timeout     = int(set_attrib(scenario, "timeout", 60))
        a_scenario = Scenario(
            xml_file=xml_path,
            name=name,
            description=description,
            town=town,
            type=type,
            goal=goal,
            timeout=timeout,
            criteria=criteria,
            snapshot=name+".mp4"
        )
        scenarios[name] = a_scenario
    return scenarios

def set_attrib(node, key, default):
    """
    Parse XML key for a given node
    If key does not exist, use default value
    """
    return node.attrib[key] if key in node.attrib else default

if __name__ == "__main__":
    app = ScenarioRunnerApp()
    app.mainloop()

