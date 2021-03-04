#!/usr/bin/python3

import math

from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename


class MyWindow(Tk):
    
    def __init__(self):
        Tk.__init__(self)
        self.createMenuBar()
        
        # Fill the content of the window

        self.geometry( "300x200" )
        self.title( "MyFirstMenu V1.0" )
    
    def createMenuBar(self):
        menuBar = Menu(self)
        
        menuFile = Menu(menuBar, tearoff=0)
        menuFile.add_command(label="New", command=self.doSomething)
        menuFile.add_command(label="Open", command=self.openFile)
        menuFile.add_command(label="Save", command=self.doSomething)
        menuFile.add_separator()
        menuFile.add_command(label="Exit", command=self.quit)
        menuBar.add_cascade( label="File", menu=menuFile)

        menuEdit = Menu(menuBar, tearoff=0)
        menuEdit.add_command(label="Undo", command=self.doSomething)
        menuEdit.add_separator()
        menuEdit.add_command(label="Copy", command=self.doSomething)
        menuEdit.add_command(label="Cut", command=self.doSomething)
        menuEdit.add_command(label="Paste", command=self.doSomething)
        menuBar.add_cascade( label="Edit", menu=menuEdit)

        menuHelp = Menu(menuBar, tearoff=0)
        menuHelp.add_command(label="About", command=self.doAbout)
        menuBar.add_cascade( label="Help", menu=menuHelp)

        self.config(menu = menuBar)        

    def openFile(self):
        file = askopenfilename(title="Choose the file to open", 
                filetypes=[("PNG image", ".png"), ("GIF image", ".gif"), ("All files", ".*")])
        print( file )
        
        
    def doSomething(self):
        print("Menu clicked")


    def doAbout(self):
        messagebox.showinfo("My title", "My message")


window = MyWindow()
window.mainloop()
