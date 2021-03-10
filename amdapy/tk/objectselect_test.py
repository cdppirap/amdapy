import tkinter as tk
from tkinter import ttk

#        tree=ttk.Treeview(self)
#        tree.column("#0", width=100, minwidth=100, stretch=tk.NO)
#
#        tree.heading("#0",text="Dataset", anchor=tk.W)
#        d1=tree.insert("",1,text="Dataset 1", values=())
#        #level2
#        tree.insert(d1, "end",  text="Variable1", values=())
#        tree.insert(d1,"end", text="Variable2", values=())
#        tree.pack(side=tk.TOP, fill=tk.X)

class TreeSelector(ttk.Treeview):
  def __init__(self, master, head):
    super().__init__(master)
    self.head=head
    self.column("#0")
    self.heading("#0", text=head, anchor=tk.W)
    a=self.insert("",1,text="Selection1", values=())
    self.insert(a, "end", text="var1", values=())
    self.insert(a, "end", text="var2", values=())
    self.pack(side=tk.TOP, fill=tk.X)
    self.bind("<ButtonRelease-1>",self.on_click)
  def on_click(self, ev):
    print("\tSelector {} select {}".format(self.head,ev))
    print(self.selection())
    
class ObjectSelector(ttk.Notebook):
  tab_names=["Dataset","Function","Plot"]
  def __init__(self, master):
    super().__init__(master)
    self.tabs=[]
    self.create_tabs(self.tab_names)
    self.pack(expand=1,fill="both")
  def create_tabs(self, tab_names):
    for tn in tab_names:
      #tab=ttk.Frame(self)
      tree=TreeSelector(self, head="{}".format(tn))#.grid(column=0, row=0, padx=30, pady=30)
      self.tabs.append(tree)
      self.add(tree, text=tn)


root=tk.Tk()
root.title("Test ObjectSelector widget")

objectselector=ObjectSelector(root)
root.mainloop()

