import time
import csv
import tkinter as tk
from tkinter import font as tkfont

class DrivingSummary(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self._parent = parent
        self._controller = controller
        self.configure(background='#67BFFF')
        label = tk.Label(self,
                         # text="Driving summary",
                         font=controller.title_font,bg='#67BFFF')
        label.pack(side="top", fill="x", pady=10)

        labelframe1 = tk.LabelFrame(self, text="Hope you enjoyed it",bg='#67BFFF')
        labelframe1.pack(fill="both", expand="yes")

        photo = tk.PhotoImage(file="utils/images/leicester.gif")
        a1label = tk.Label(labelframe1,image = photo,bg='#67BFFF')
        a1label.image = photo
        a1label.pack()

        text_font = tkfont.Font(family='Helvetica', size=25, weight="bold", slant="italic")
        self.toplabel = tk.Label(labelframe1, text="\nThank you for visiting and drive safe!\n"
                            , font=text_font, bg='#67BFFF')
        self.toplabel.pack()
        # self.toplabel.place(anchor="c", relx=.5, rely=.5)

        infomessage = tk.Label(labelframe1,text = "If you would like more information please visit:\n"
                                                  "http://driverleics.github.io/", font=text_font, bg='#67BFFF')
        infomessage.pack()


        self.button1 = tk.Button(self, text="Back to start menu", command=lambda: controller.show_frame("StartPage"),bg='#FF9A2E')
        self.button1.focus()
        self.button1.pack()

        self.bind("<<"+self.__class__.__name__+">>", self._event_call)

    def _event_call(self, event):
        print(self.__class__.__name__)
        print("event -> "+str(event))
        csv_size = self._controller.file_len("score.csv")
        if csv_size == self._controller.csv_size:
            self.toplabel["text"] = "\nThank you for visiting and drive safe!\n"
        else:
            score = self.check_last_score()
            self.toplabel["text"] = "\nYour score is {}\n"\
                                    "\nThank you for visiting and drive safe!\n".format(int(score))
            self.button1.focus()
            self.button1.focus_set()
            self.button1.focus_force()

        self.toplabel.pack()
        # time.sleep(self._controller.timeout_DrivingSummary)

    def check_last_score(self):
        finalScore = None
        try:
            with open("score.csv","r") as fp:
                scorereader = csv.DictReader(fp, delimiter=',')
                for row in scorereader:
                    print(row['finalScore'])
                    finalScore = row['finalScore']
        except Exception as e:
            print(e)

        return finalScore