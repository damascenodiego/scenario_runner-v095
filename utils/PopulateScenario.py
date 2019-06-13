import time
import tkinter as tk
from tkinter import font as tkfont
from PIL import Image,ImageTk

class PopulateScenario(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self.configure(background='#67BFFF')
        # label = tk.Label(self, text="Populating Scenario...", font=controller.title_font,bg='#67BFFF')
        # label.pack(side="top", fill="x", pady=10)

        labelframe1 = tk.LabelFrame(self,
                                    text="Populating test scenario...\n",
                                    font=controller.title_font, bg='#67BFFF')

        cycleimage= Image.open("utils/images/cyclist.png")
        width = 128
        height = 128
        smallcyclephoto = cycleimage.resize((width,height),Image.ANTIALIAS)
        cyclephoto = ImageTk.PhotoImage(smallcyclephoto)
        slabel = tk.Label(image=cyclephoto)
        slabel.image = cyclephoto
        clabel = tk.Label(labelframe1,image=cyclephoto,bg='#67BFFF')
        clabel.grid(row=0,column=0, padx=2)

        pedeimage = Image.open("utils/images/pedestrian.png")
        width = 128
        height = 128
        smallpedephoto = pedeimage.resize((width,height),Image.ANTIALIAS)
        pedephoto = ImageTk.PhotoImage(smallpedephoto)
        olabel = tk.Label(image = pedephoto)
        olabel.image = pedephoto
        plabel = tk.Label(labelframe1,image=pedephoto,bg='#67BFFF')
        plabel.grid(row=0,column=1, padx=2)

        weatherimage = Image.open("utils/images/weather.png")
        width = 128
        height = 128
        smallweat = weatherimage.resize((width,height),Image.ANTIALIAS)
        weatphoto = ImageTk.PhotoImage(smallweat)
        qlabel = tk.Label(image= weatphoto)
        qlabel.image = weatphoto
        rlabel = tk.Label(labelframe1,image=weatphoto,bg='#67BFFF')
        rlabel.grid(row=0,column=2, padx=2)

        carimage = Image.open("utils/images/car.png")
        width = 128
        height = 128
        smallcar = carimage.resize((width, height), Image.ANTIALIAS)
        carphoto = ImageTk.PhotoImage(smallcar)
        tlabel = tk.Label(image=carphoto)
        tlabel.image = carphoto
        ulabel = tk.Label(labelframe1, image=carphoto,bg='#67BFFF')
        ulabel.grid(row=0,column=3)

        text_font = tkfont.Font(family='Helvetica', size=35, weight="bold", slant="italic")
        bottomlabel = tk.Label(labelframe1, text="Follow the red line and drive safely!", font=text_font,bg='#67BFFF')
        # bottomlabel.pack()
        bottomlabel.grid(row=1, columnspan=4)

        labelframe1.pack(fill="both", expand="yes")
        labelframe1.place(anchor="c", relx=.5, rely=.5)

        self.bind("<<"+self.__class__.__name__+">>", self._event_call)

    def _event_call(self, event):
        print(self.__class__.__name__)
        print("event -> " + str(event))
        time.sleep(self._controller.timeout_PopulateScenario)
        self._controller.show_frame("DrivingMode")
