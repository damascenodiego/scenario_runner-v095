import time
import os
import imageio
import tkinter as tk, threading

from tkinter import font as tkfont
from PIL import Image,ImageTk

class PopulateScenario(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self.configure(background='#67BFFF')
        labelframe1 = tk.LabelFrame(self,
                                    text="Populating test scenario with obstacles...\n",
                                    font=controller.title_font, bg='#67BFFF')
        labelframe1.pack(fill="both", expand="yes")
        labelframe1.place(anchor="c", relx=.5, rely=.5)


        dir_path = os.path.dirname(os.path.realpath(__file__))
        image_name = os.path.join(dir_path, "images", "populating.gif")
        image = Image.open(image_name)

        self._label = tk.Label(labelframe1)
        self._label.image = image
        self._label.pack()
        # self._label.place(anchor="c", relx=.5, rely=.5)

        text_font = tkfont.Font(family='Helvetica', size=32, slant="italic")
        bottomlabel = tk.Label(labelframe1, text="Follow the red line and drive safely!", font=text_font,bg='#67BFFF')
        bottomlabel.pack()
        # bottomlabel.grid(row=1)



        self.bind("<<"+self.__class__.__name__+">>", self._event_call)

    def stream(self):
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            video_name = os.path.join(dir_path, "images", "populating.gif")
            video = imageio.get_reader(video_name)
            wait_sleep = self._controller.timeout_SearchingRoute/len(video)
            for image in video.iter_data():
                frame_image = ImageTk.PhotoImage(Image.fromarray(image))
                self._label.config(image=frame_image)
                self._label.image = frame_image
                time.sleep(wait_sleep)
        except Exception as e:
            print(e)

        self._controller.show_frame("DrivingMode")

    def _event_call(self, event):
        print(self.__class__.__name__)
        # print("event -> "+str(event))
        self.focus()
        self.focus_set()
        self.focus_force()
        self._thread = threading.Thread(target=self.stream)
        self._thread.daemon = 1
        self._thread.start()

