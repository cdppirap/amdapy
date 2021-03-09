"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:brief: A simple editor for editing SPASE resource files.

Simple command line tool for editing SPASE XML resource files. Allows to perform simple checks such
that all variable in a NumericalData file are uniquely named and that the corresponding Parameter
file exists and is well defined.

Can be called like a script for editing specific files. Mostly used for managing the AMDA database
resource files.

"""
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
  def set_done(self, v=True):
    """Set the editing state to a given value. Default sets the flag to True.

    :param v: value to give to the editing state.
    :type v: bool, optional
    """
    self.done=v
  def print_manual(self):
    """Print the usage manual for the editor. Prints a description of all the commands.
    """
    print("Commands : ")
    for a in self.actions:
      print("\t{}".format(a))

  class UserInput:
    """Base class for representing the user inputs.
    """
    def __init__(self):
      """Object constructor
      """
      ## User input data
      self.a=input("?>")
      self.a=self.a.split(" ")
    def __len__(self):
      """Get length of the user input.

      :return: length of the user input string.
      :rtype: int
      """
      return len(self.a)
    def __getitem__(self,i):
      """Item getter.

      :param i: item index
      :type i: int
      :return: item at position i
      :rtype: str
      """
      return self.a[i]
    def __str__(self):
      """Current object string representation.
      
      :return: object string representation.
      :rtype: str
      """
      return str(self.a)
    def __setitem__(self,i,v):
      """Item setter

      :param i: item position
      :type i: int
      :param v: value of the item
      :rtype v: str
      """
      self.a[i]=v

  class EditorAction:
    """Class for representing editing actions taken by the user.

    :param par: action keys.
    :type par: str or list
    :param act: callback function when this action is executed
    :type act: callable
    :param help: help string
    :type help: str
    :param n_args: number of argument this action requires
    :type n_args: int
    """
    def __init__(self, par, act, n_args=0, help=None):
      """Object constructor
      """
      ## Action keys.
      self.par=par
      ## Action function.
      self.act=act
      ## Number of user supplied values.
      self.n_args=n_args
      ## Help string.
      self.help=help
    def key_count(self):
      """Count the number of keys for this actions
      
      :return: number of keys for this actions
      :rtype: int
      """
      if isinstance(self.par, str):
        return 1
      return len(self.par)
    def matches(self, ui):
      """Check that the user input matches the action definition

      :param ui: user input
      :type ui: amdapy.editor.Editor.UserInput
      :return: True if the user input is compatible with the action definition, False otherwise.
      :rtype: bool
      """
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
    def apply(self,editor_ptr, ui):
      """Apply the action to the current state of the editor.

      :param editor_ptr: handle of the editor.
      :type editor_ptr: amdapy.editor.Editor
      :param ui: user input
      :type ui: amdapy.editor.Editor.UserInput
      """
      self.act(editor_ptr, ui)
    def __str__(self):
      """Current object string representation.
      
      :return: string representation of the current object.
      :rtype: str
      """
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

class NumericalDataEditor(Editor):
  """Subclass of :class:`amdapy.editor.Editor` for editing NumericalData files.

  :param filename: absolute or relative path to the NumericalData file we want to edit.
  :type filename: str
  :param repo_root: absolute path to the root of the SPASE resource repository, optional
  :type repo_root: str
  """
  def __init__(self,filename,repo_root=spase.DEFAULT_REPOSITORY_ROOT):
    """Object constructor
    """
    super(NumericalDataEditor,self).__init__()
    ## Editor resource, this is the object we want to edit.
    self.resource=NumericalData(filename)
    self.add_editor_actions()
  def add_editor_actions(self):
    """Add the editing action to the current editor object.
    """
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
  @staticmethod
  def set_editing_done(editor, ui):
    """Set the state of the editor to finished

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    editor.set_done(True)
  @staticmethod
  def set_resource_id(editor, ui):
    """Set resource id of the current file.

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    editor.resource.set_resource_id(ui[2])
  @staticmethod
  def set_description(editor, ui):
    """Set resource description

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    editor.resource.set_description(ui[2])
  @staticmethod
  def set_repository(editor, ui):
    """Set repository path

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    editor.repository_root=ui[2]
  @staticmethod
  def set_measurement_type(editor, ui):
    """Set resource measurement type

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    editor.resource.set_measurement_type(ui[2])
  @staticmethod
  def set_start_date(editor, ui):
    """Set resource start date

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    editor.resource.set_start_date(ui[2])
  @staticmethod
  def set_stop_date(editor, ui):
    """Set resource stop date

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    editor.resource.set_stop_date(ui[2])
  @staticmethod
  def set_release_date(editor, ui):
    """Set resource release date

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    editor.resource.set_release_date(ui[2])
  @staticmethod
  def set_cadence_min(editor, ui):
    """Set resource cadence min value

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    editor.resource.set_cadence_min(ui[2])
  @staticmethod
  def set_cadence_max(editor, ui):
    """Set resource cadence max value

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    editor.resource.set_cadence_max(ui[2])
  @staticmethod
  def add_parameter(editor, ui):
    """Add parameter to current resource file

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    p=Parameter.make_parameter_xmlel(name=ui[2], key=ui[3], size=1)
    editor.resource.add_parameter(p)
  @staticmethod
  def add_contact(editor, ui):
    """Add contact to current resource file

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    c=Contact.make_contact_xmlel(ui[2],ui[3])
    editor.resource.add_contact(c)
  @staticmethod
  def remove_parameter(editor, ui):
    """Remove parameter from current resource file

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    editor.resource.remove_parameter(int(ui[2])-1)
  @staticmethod
  def remove_contact(editor, ui):
    """Remove a contact from current resource.

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    editor.resource.remove_contact(int(ui[2])-1)
  @staticmethod
  def set_component_prefix(editor, ui):
    """Set resource component prefix

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    # parameter index
    param_index=int(ui[3])-1
    param_prefix=ui[4]
    editor.resource.set_component_prefix(param_index, param_prefix)
  @staticmethod
  def set_component_suffix(editor, ui):
    """Set resource component suffux. Variable components are name <prefix><suffix>.

    :param editor: handle of the current editor object
    :type editor: amdapy.editor.NumericalDataEditor
    :param ui: user input
    :type ui: amdapy.editor.NumericalDataEditor.UserInput
    """
    param_id=int(ui[3])-1
    suffix=ui[4]
    editor.resource.set_component_suffix(param_id,suffix)

class InstrumentEditor(Editor):
  """SPASE Instrument resource file editor. Simple command line tool for editing and check
  SPASE Instrument resource files.

  :param filename: path to the file we want to edit. If file exists it is loaded otherwise a blank file is created
  :type filename: str
  :param repo_root: absolute or relative path to the SPASE resource file repository, optional
  :type repo_root: str

  """
  def __init__(self, filename, repo_root=spase.DEFAULT_REPOSITORY_ROOT):
    """Object constructor
    """
    super(InstrumentEditor,self).__init__()
    self.resource=Instrument(filename)
    self.add_editor_actions()
  def add_editor_actions(self):
    """Add an editing action to the editor object
    """
    pass

def parse_args():
  """Parse command line arguments

  :return: command line arguments
  :rtype: argparse.Arguments
  """
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
