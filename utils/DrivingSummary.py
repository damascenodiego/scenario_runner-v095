import sys
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

        photo = tk.PhotoImage(file="utils/images/snapshot_blank.png")
        self.snapshot = tk.Label(labelframe1, image=photo, bg='#67BFFF')
        self.snapshot.image = photo
        self.snapshot.pack()

        sq_sz = 15
        self.legend = tk.Canvas(labelframe1, width=390, height=18)
        self.legend.create_rectangle(0, 2, sq_sz, sq_sz + 2, fill="red", outline ='black')
        self.legend.create_text(3.5 * sq_sz - 5, sq_sz / 2, text="Collision")

        self.legend.create_rectangle(100, 2, 100 + sq_sz, sq_sz + 2, fill="blue", outline ='black')
        self.legend.create_text(100 + 3.5 * sq_sz + 4, sq_sz / 2, text="Wrong way")

        self.legend.create_rectangle(210, 2, 210 + sq_sz, sq_sz + 2, fill="yellow", outline ='black')
        self.legend.create_text(210 + 3.5 * sq_sz - 3, sq_sz / 2, text="Off track")

        self.legend.create_rectangle(300, 2, 300+sq_sz, sq_sz+2, fill="white",  outline = 'black')
        self.legend.create_text(300+3.5*sq_sz,sq_sz/2, text="Red light")
        self.legend.pack()

        text_font = tkfont.Font(family='Helvetica', size=25, weight="bold", slant="italic")
        self.toplabel = tk.Label(labelframe1, text="Thank you for visiting our stand and drive safe!\n"
                                                   "For more information, check our homepage:\n" \
                                                   "http://driverleics.github.io/"
                            , font=text_font, bg='#67BFFF')
        self.toplabel.pack()

        self.button1 = tk.Button(self, text="Back to start menu", command=lambda: controller.show_frame("StartPage"),bg='#FF9A2E')
        self.button1.focus()
        self.button1.pack()

        self.bind("<<"+self.__class__.__name__+">>", self._event_call)

    def _event_call(self, event):
        print(self.__class__.__name__)
        print("event -> "+str(event))
        csv_size = self._controller.file_len("score.csv")
        if csv_size == self._controller.csv_size:
            frame_image = tk.PhotoImage(file="utils/images/snapshot_blank.png")
            self.snapshot.config(image=frame_image)
            self.snapshot.image = frame_image
            self.legend.pack_forget()

            self.toplabel["text"] = "Thank you for visiting our stand and drive safe!\n" \
                                    "For more information, check our homepage:\n" \
                                    "http://driverleics.github.io/"
        else:
            self.toplabel.pack_forget()
            self.legend.pack()
            self.toplabel.pack()
            id_score = self.check_last_score()
            id    = id_score[0]
            score = id_score[1]
            self.toplabel["text"] = "\nYour ID is {}\nYour score is {}\n" \
                                    "Thank you for visiting our stand and drive safe!\n" \
                                    "For more information, check our homepage:\n" \
                                    "http://driverleics.github.io/".format(int(id),int(score))

            try:
                self._controller.printer.print(id,score)
            except Exception as e:
                print("Printer error: {}".format(e), file=sys.stderr)

            try:
                frame_image = tk.PhotoImage(file="snapshots/snapshot_{}.png".format(id))
                self.snapshot.config(image=frame_image)
                self.snapshot.image = frame_image
            except Exception as e:
                print(e)
                frame_image = tk.PhotoImage(file="utils/images/snapshot_blank.png")
                self.snapshot.config(image=frame_image)
                self.snapshot.image = frame_image

            self.button1.focus()
            self.button1.focus_set()
            self.button1.focus_force()

        self.toplabel.pack()
        # time.sleep(self._controller.timeout_DrivingSummary)

    def check_last_score(self):
        id = None
        finalScore = None
        try:
            with open("score.csv","r") as fp:
                scorereader = csv.DictReader(fp, delimiter=',')
                for row in scorereader:
                    print(row['finalScore'])
                    id = row['id']
                    finalScore = row['finalScore']
        except Exception as e:
            print(e)

        return [id, finalScore]