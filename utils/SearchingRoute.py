import tkinter as tk, threading
import imageio
from PIL import Image, ImageTk
import time
import os
import configparser

class SearchingRoute(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self.configure(background='#67BFFF')
        labelframe1 = tk.LabelFrame(self, text="Searching for interesting route...", font=controller.title_font,bg='#67BFFF')
        labelframe1.pack(fill="both", expand="yes")

        self._video_running = True

        self._label = tk.Label(labelframe1)
        self._label.pack()
        self._label.place(anchor="c", relx=.5, rely=.5)

        scenario = self._controller.selected_scenario

        self._description = tk.Label(self, text=scenario.description, font=controller.title_font, bg='#67BFFF')
        self._description.pack(side="top", fill="x", pady=10)

        self.bind("<<" + self.__class__.__name__ + ">>", self._event_call)

    def stream(self):
        scenario = self._controller.selected_scenario
        dir_path = os.path.dirname(os.path.realpath(__file__))
        video_name = os.path.join(dir_path, "videos", scenario.snapshot)
        video = imageio.get_reader(video_name)
        self._description['text'] = "Searching for an interesting route...\n"

        meta_data = video.get_meta_data()
        wait_sleep = 0.2/meta_data['fps']
        for image in video.iter_data():
            frame_image = ImageTk.PhotoImage(Image.fromarray(image))
            self._label.config(image=frame_image)
            self._label.image = frame_image
            time.sleep(wait_sleep)
        self._description['text'] = "Goal: {}\n" \
                                    "Time limit: {} seconds".format(
                                                scenario.goal,
                                                scenario.timeout,
                                                scenario.description
        )
        time.sleep(self._controller.timeout_SearchingRoute)
        self._controller.show_frame("PopulateScenario")

    def _event_call(self, event):
        print(self.__class__.__name__)
        print("event -> "+str(event))
        self._thread = threading.Thread(target=self.stream)
        self._thread.daemon = 1
        self._thread.start()

