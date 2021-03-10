import tkinter as tk
from tkinter import *
import tkinter.ttk as ttk

class Application(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.create_menubar()
        self.create_widgets()
        self.create_dataset_tree()
    def create_widgets(self):
        self.hi_there=tk.Button(self)
        self.hi_there["text"]="Hello World\n(click me)"
        self.hi_there["command"]=self.say_hi
        self.hi_there.pack(side="top")
    def say_hi(self):
        print("hi there, everyone")
    def create_menubar(self):
        menuBar=tk.Menu(self)
        menuFile=tk.Menu(menuBar, tearoff=0)
        menuFile.add_command(label="New", command=self.new_session)
        menuFile.add_command(label="Open", command=self.open_session)
        menuFile.add_separator()
        menuFile.add_command(label="Quit", command=self.quit)
        menuBar.add_cascade(label="File", menu=menuFile)
        self.config(menu = menuBar)
    def create_dataset_tree(self):
        tree=ttk.Treeview(self)
        tree.column("#0", width=100, minwidth=100, stretch=tk.NO)

        tree.heading("#0",text="Dataset", anchor=tk.W)
        d1=tree.insert("",1,text="Dataset 1", values=())
        #level2
        tree.insert(d1, "end",  text="Variable1", values=())
        tree.insert(d1,"end", text="Variable2", values=())
        tree.pack(side=tk.TOP, fill=tk.X)
    def new_session(self):
        print("Creating new session")
    def open_session(self):
        print("Open session")
    def quit(self):
        print("Quitting")
        exit()
app=Application()
app.mainloop()
