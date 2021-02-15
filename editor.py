## Script used for editing Spase Resource files.
#
#  @file editor.py
#  @author Alexandre Schulz
#  @brief SPASE resource editor.

import os
import argparse

from amdapy.spase import NumericalData, Parameter, Contact
import amdapy.spase as spase

class Editor:
  """This is the base class used for editing SPASE XML resource files. This class is used as a base for 
  the construction of the NumericalDataEditor, ObservatoryEditor, InstrumentEditor classes.
  :class: amdapy.editor.Editor

  :param resource: the object that we wish to edit.
  :type resource: class amdapy.spase.SpaseResource
  :param ui: user input
  :type ui: amdapy.editor.Editor.UserInput
  :param done: flag indicating that editing is done, the main loop is broken
  :type done: boolean
  :param actions: list of editing actions.
  :type actions: list of amdapy.editor.Editor.EditAction
  :param buffer: debugging buffer.
  :type buffer: str
  """
  def __init__(self):
    """Constructor
    """
    self.resource=None
    self.ui=None
    self.done=False
    self.actions=[]
    self.buffer=None
  def start(self):
    """Start the editing loop.
    """
    while not self.editing_done():
      ## print editor content
      self.print_content()
      ## get user input
      self.user_input()
      ## act on user input
      self.apply_input()
  def print_content(self):
    """Print the current state of the editor.
    """
    os.system("clear")
    if not self.buffer is None:
      print("buffer content : {}".format(self.buffer))
    print("content : {}".format(self.resource))
    self.print_manual()
  def editing_done(self):
    """Check if editing is done.
    """
    return self.done
  def user_input(self):
    """Get user input.
    """
    self.ui=self.UserInput()
  def apply_input(self):
    """Apply editing actions.
    """
    for action in self.actions:
      if action.matches(self.ui):
        action.apply(self,self.ui)
        return
  def add_action(self, par, act, n_args=0, help=None):
    """Add action to editor.

    :param par: action keys.
    :type par: type of strings
    :param act: action to perform, should be a function taking as arguments the current editor and the user input.
    :type act: callable
    :param n_args: number of arguments for that action.
    :type n_args: int
    :param help: help string.
    :type help: string
    """
    self.actions.append(self.EditorAction(par,act,n_args,help))
  ## Editor.set_done
  #
  #  Set the editing done flag.
  #  @param self object pointer.
  #  @param v value.
  def set_done(self, v=True):
    self.done=v
  ## Editor.print_manual
  #
  #  Print action manual.
  #  @param self object pointer.
  def print_manual(self):
    print("Commands : ")
    for a in self.actions:
      print("\t{}".format(a))

  ## Editor.UserInput class documentation.
  #
  #  UserInput class definition.
  class UserInput:
    ## Editor.UserInput.__init__
    #
    #  Initialize the UserInput object.
    #  @param self object pointer.
    def __init__(self):
      ## User input data
      self.a=input("?>")
      self.a=self.a.split(" ")
    ## Editor.UserInput.__len__
    #
    #  Return UserInput length.
    #  @param self object pointer.
    #  @return int.
    def __len__(self):
      return len(self.a)
    ## Editor.UserInput.__getitem__
    #
    #  UserInput item getter.
    #  @param self object pointer.
    #  @param i int index.
    #  @return str.
    def __getitem__(self,i):
      return self.a[i]
    ## Editor.UserInput.__str__
    #
    #  UserInpur string representation.
    #  @param self object pointer.
    def __str__(self):
      return str(self.a)
    ## Editor.UserInput.__setitem__
    #
    #  UserInput item setter.
    #  @param self object pointer.
    #  @param i (int) index.
    #  @param v value.
    def __setitem__(self,i,v):
      self.a[i]=v

  ## Editor.EditorAction class documentation.
  #
  #  EditorAction class definition.
  class EditorAction:
    ## Editor.EditorAction.__init__
    #
    #  EditorAction initialization.
    #  @param self object pointer.
    #  @param par action keys.
    #  @param act func action function.
    #  @param help help string.
    #  @param n_args number of user supplied values.
    def __init__(self, par, act, n_args=0, help=None):
      ## Action keys.
      self.par=par
      ## Action function.
      self.act=act
      ## Number of user supplied values.
      self.n_args=n_args
      ## Help string.
      self.help=help
    ## Editor.EditorAction.key_count
    #
    #  count action keys.
    #  @param self object pointer.
    def key_count(self):
      if isinstance(self.par, str):
        return 1
      return len(self.par)
    ## Editor.EditorAction.matches
    #
    #  Check if user input matches the current action object.
    #  @param self object pointer.
    #  @param ui user input.
    #  @return bool.
    def matches(self, ui):
      # check that the number of user inputs matches to action definition
      if len(ui)!=self.key_count()+self.n_args:
        #print("arg len mismatch")
        #input()
        return False
      if isinstance(self.par, str):
        return self.par==ui[0]
      for i in range(len(self.par)):
        if not self.par[i]==ui[i]:
          return False
      return True
    ## Editor.EditorAction.apply
    #
    #  Apply action to content.
    #  @param self object pointer.
    #  @param editor_ptr editor object pointer.
    #  @param ui user input.
    def apply(self,editor_ptr, ui):
      self.act(editor_ptr, ui)
    ## Editor.EditorAction.__str__
    #
    #  EditorAction string representation.
    #  @param self object pointer.
    def __str__(self):
      if isinstance(self.par, str):
        a="- {}".format(self.par)
      else:
        a=" ".join(self.par)
        a="- {}".format(a)
      for i in range(self.n_args):
        a="{} <val>".format(a)
      if not self.help is None:
        a="{} : {}".format(a,self.help)
      return a

## NumericalDataEditor class documentation.
#
#  NumericalData Editor class definition.
class NumericalDataEditor(Editor):
  ## NumericalDataEditor.__init__
  #
  #  NumericalDataEditor initialization.
  #  @param self object pointer.
  #  @param filename path to the resource file.
  #  @param repo_root (default : spase.DEFAULT_REPOSITORY_ROOT) root of the Spase repository.
  def __init__(self,filename,repo_root=spase.DEFAULT_REPOSITORY_ROOT):
    super(NumericalDataEditor,self).__init__()
    ## Editor resource, this is the object we want to edit.
    self.resource=NumericalData(filename)
    self.add_editor_actions()
  ## NumericalDataEditor.add_editor_actions
  #
  #  Add the right editing actions to current object.
  #  @param self object pointer.
  def add_editor_actions(self):
    self.add_action("quit", NumericalDataEditor.set_editing_done,help="quit editor" )
   
    self.add_action(("set","id"), NumericalDataEditor.set_resource_id, n_args=1, help="set the ResourceID")
    self.add_action(("set","description"),NumericalDataEditor.set_description, n_args=1,help="set Description")
    self.add_action(("set","repository"),NumericalDataEditor.set_repository, n_args=1,help="set SPASE repository root")
    self.add_action(("set","measurementtype"),NumericalDataEditor.set_measurement_type, n_args=1,help="set MeasurementType")
    self.add_action(("set","startdate"),NumericalDataEditor.set_start_date, n_args=1,help="set StartDate")
    self.add_action(("set","stopdate"),NumericalDataEditor.set_stop_date, n_args=1,help="set StopDate")
    self.add_action(("set","releasedate"),NumericalDataEditor.set_release_date, n_args=1,help="set ReleaseDate")
    self.add_action(("set","cadencemin"),NumericalDataEditor.set_cadence_min, n_args=1,help="set CadenceMin")
    self.add_action(("set","cadencemax"),NumericalDataEditor.set_cadence_max, n_args=1,help="set CadenceMax")
   
    self.add_action(("add","parameter"),NumericalDataEditor.add_parameter, n_args=2,help="add parameter element")
    self.add_action(("add","contact"),NumericalDataEditor.add_contact, n_args=2,help="add contact element")
   
    self.add_action(("rm","parameter"),NumericalDataEditor.remove_parameter, n_args=1, help="remove parameter element")
    self.add_action(("rm","contact"),NumericalDataEditor.remove_contact, n_args=1,help="remove contact element")
    self.add_action(("set","component","prefix"), NumericalDataEditor.set_component_prefix, n_args=2, help="set the parameters components prefix")
    self.add_action(("set","component","suffix"), NumericalDataEditor.set_component_suffix, n_args=2, help="set the parameters components suffix")
  ## NumericalDataEditor.set_editing_done (static)
  #
  #  Set the state of the editor to done.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def set_editing_done(editor, ui):
    editor.set_done(True)
  ## NumericalDataEditor.set_resource_id (static)
  #
  #  Set the resource id value.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def set_resource_id(editor, ui):
    editor.resource.set_resource_id(ui[2])
  ## NumericalDataEditor.set_description (static)
  #
  #  Set the description value.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def set_description(editor, ui):
    editor.resource.set_description(ui[2])
  ## NumericalDataEditor.set_repository (static)
  #
  #  Set the repository path.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def set_repository(editor, ui):
    editor.repository_root=ui[2]
  ## NumericalDataEditor.set_measurement_type(static)
  #
  #  Set the measurement type.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def set_measurement_type(editor, ui):
    editor.resource.set_measurement_type(ui[2])
  ## NumericalDataEditor.set_start_date(static)
  #
  #  Set the start date.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def set_start_date(editor, ui):
    editor.resource.set_start_date(ui[2])
  ## NumericalDataEditor.set_stop_date(static)
  #
  #  Set the stop date.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def set_stop_date(editor, ui):
    editor.resource.set_stop_date(ui[2])
  ## NumericalDataEditor.set_release_date(static)
  #
  #  Set the release date.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def set_release_date(editor, ui):
    editor.resource.set_release_date(ui[2])
  ## NumericalDataEditor.set_cadence_min(static)
  #
  #  Set the cadence min.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def set_cadence_min(editor, ui):
    editor.resource.set_cadence_min(ui[2])
  ## NumericalDataEditor.set_cadence_max(static)
  #
  #  Set the cadence max.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def set_cadence_max(editor, ui):
    editor.resource.set_cadence_max(ui[2])
  ## NumericalDataEditor.add_parameter(static)
  #
  #  Add parameter.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def add_parameter(editor, ui):
    p=Parameter.make_parameter_xmlel(name=ui[2], key=ui[3], size=1)
    editor.resource.add_parameter(p)
  ## NumericalDataEditor.add_contact(static)
  #
  #  Add contact.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def add_contact(editor, ui):
    c=Contact.make_contact_xmlel(ui[2],ui[3])
    editor.resource.add_contact(c)
  ## NumericalDataEditor.remove_parameter(static)
  #
  #  Remove parameter.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def remove_parameter(editor, ui):
    editor.resource.remove_parameter(int(ui[2])-1)
  ## NumericalDataEditor.remove_contact(static)
  #
  #  Remove contact.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def remove_contact(editor, ui):
    editor.resource.remove_contact(int(ui[2])-1)
  ## NumericalDataEditor.set_component_prefix
  #
  #  Set the component prefix for a certain parameter.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def set_component_prefix(editor, ui):
    # parameter index
    param_index=int(ui[3])-1
    param_prefix=ui[4]
    editor.resource.set_component_prefix(param_index, param_prefix)
  ## NumericalDataEditor.set_component_suffix
  #
  #  Set the component suffix
  #  @param self object pointer.
  #  @param editor editor pointer.
  #  @param ui user input.
  @staticmethod
  def set_component_suffix(editor, ui):
    param_id=int(ui[3])-1
    suffix=ui[4]
    editor.resource.set_component_suffix(param_id,suffix)
## InstrumentEditor class documentation.
#
#  InstrumentEditor class definition. This class is used for defining Instrument SPASE file editors.
class InstrumentEditor(Editor):
  ## InstrumentEditor.__init__
  #
  #  Editor initialization.
  #  @param self object pointer.
  #  @param filename file we want to edit.
  #  @param repo_root (default: spase.DEFAULT_REPOSITORY_ROOT) root of the Spase repository.
  def __init__(self, filename, repo_root=spase.DEFAULT_REPOSITORY_ROOT):
    super(InstrumentEditor,self).__init__()
    self.resource=Instrument(filename)
    self.add_editor_actions()
  ## InstrumentEditor.add_editor_actions
  #
  #  Add actions needed for editing an Instrument file.
  #  @param self object pointer.
  def add_editor_actions(self):
    pass

## Parse arguments.
#
## Parse the command line arguments.
def parse_args():
  parser=argparse.ArgumentParser()
  parser.add_argument("-n","--numericaldata",help="edit a NumericalData file", type=str, default="")
  parser.add_argument("-i","--instrument",help="edit an Instrument file", type=str, default="")
  parser.add_argument("-o","--observatory", help="edit an Observatory file", type=str, default="")
  parser.add_argument("-r","--repository", help="set the SPASE repository path", type=str, default=spase.DEFAULT_REPOSITORY_ROOT)
  return parser.parse_args()

if __name__=="__main__":
  args=parse_args()
  editor=None
  print(type(args.numericaldata))
  if len(args.numericaldata):
    if not os.path.exists(args.numericaldata):
      print("Error : file {} does not exist.".format(args.numericaldata))
      exit()
    editor=NumericalDataEditor(filename=args.numericaldata)
  
  ## if we want to edit an Instrument file.
  if len(args.instrument):
    if not os.path.exists(args.instrument):
      print("Error : Instrument file {} does not exist".format(args.instrument))
      exit()
    editor=InstrumentEditor(args.instrument)
  
  ## if we want to edit an Observatory file.
  if len(args.observatory):
    if not os.path.exists(args.observatory):
      print("Error : Observatory file {} does not exist".format(args.observatory))
      exit()
    editor=ObservatoryEditor(args.observatory)
  if not editor is None:
    editor.start()
