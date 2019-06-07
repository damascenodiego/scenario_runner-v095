import time
import tkinter as tk
from tkinter import font as tkfont
from ast import literal_eval


class DrivingSummary(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self.configure(background='#67BFFF')
        label = tk.Label(self, text="Driving summary", font=controller.title_font,bg='#67BFFF')
        label.pack(side="top", fill="x", pady=10)

        labelframe1 = tk.LabelFrame(self, text="Hope you enjoyed it",bg='#67BFFF')
        labelframe1.pack(fill="both", expand="yes")

        photo = tk.PhotoImage(file="leicester.gif")
        a1label = tk.Label(labelframe1,image = photo,bg='#67BFFF')
        a1label.image = photo
        a1label.pack()

        text_font = tkfont.Font(family='Helvetica', size=25, weight="bold", slant="italic")
        self.toplabel = tk.Label(labelframe1, text="Your score is {}\n\n"
                                              "Thank you for visiting and have a lovely day.\n\n".format(000)
                            , font=text_font, bg='#67BFFF')
        self.toplabel.pack()
        # self.toplabel.place(anchor="c", relx=.5, rely=.5)

        infomessage = tk.Label(labelframe1,text = "If you would like more information please visit: http://driverleics.github.io/", font=text_font, bg='#67BFFF')
        infomessage.pack()


        self.button1 = tk.Button(self, text="Back to start menu", command=lambda: controller.show_frame("StartPage"),bg='#FF9A2E')
        self.button1.focus()
        self.button1.pack()

        self.bind("<<"+self.__class__.__name__+">>", self._event_call)

    def _event_call(self, event):
        score = self.read_last_score()
        self.toplabel["text"] = "Your score is {}\n\n" \
                                "" \
                                "Thank you for visiting and have a lovely day.\n\n".format(score)

        self.button1.focus_set()
        print(self.__class__.__name__)
        print("event -> " + str(event))

    def read_last_score(self):
        fp = open("score.dict","r")
        last_line = ""
        while 1:
            line = fp.readline()
            if not line:
                break
            last_line = line
        score_dict = literal_eval(last_line)
        finalScore = 0
        if 'finalScore' in score_dict.keys():
            finalScore = score_dict['finalScore']
        return finalScore