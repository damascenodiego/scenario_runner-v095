import tkinter as tk
from tkinter import font as tkfont

class ChooseTown(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.LabelFrame(self, text="List of scenarios", font=controller.title_font)
        label.pack(side="top", fill="both", padx=10, pady=10)

        frm = tk.Frame(label)
        frm.grid(row=0, column=0)
        self.scenario_selected = None
        scrollbar = tk.Scrollbar(frm, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._listNodes = tk.Listbox(frm, width=20, yscrollcommand=scrollbar.set, font=("Helvetica", 12))
        self._listNodes.bind('<<ListboxSelect>>', self._scenario_clicked)
        self._listNodes.pack(expand=True, fill=tk.Y)
        scrollbar.config(command=self._listNodes.yview)

        frm.pack(side=tk.LEFT, fill=tk.Y)

        for k, v in controller.map_of_scenarios.items():
            if self.scenario_selected is None:
                self.scenario_selected = v
            self._listNodes.insert(tk.END, v)

        photo = tk.PhotoImage(file="scenario2.png")
        self._scenicroute = tk.Label(label,image=photo, text="Description", compound=tk.TOP)
        self._scenicroute.image = photo
        self._scenicroute.pack(expand=True, fill=tk.BOTH)

    def _event_call(self, event):
        print(self.__class__.__name__)
        print("event -> " + str(event))

    def _scenario_clicked(self, event):
        widget = event.widget
        selection = widget.curselection()
        if len(selection) > 0:
            print("selection -> " + str(selection))
            picked = widget.get(selection[0])
            print("picked -> " + str(picked))
            self._scenicroute['text'] = picked
            img2 = tk.PhotoImage(file=picked+".png")
            self._scenicroute.configure(image=img2)
            self._scenicroute.image = img2

