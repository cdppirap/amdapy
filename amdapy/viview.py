"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:brief: Script for generating a pdf file with a summary of a dataset.

This script is used to generate a pdf file containing a summary of the data contained in a dataset 
installed or about to be installed into AMDA. The scripts produces basic plots and tables of the 
variables contained in the dataset , their datatype, and their shapes. 

"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import os

class VIViewer:
  """Class for generating the pdf summary of a collection of netCDF files.

  :param filename: path to the dataset files
  :type filename: str
  """
  def __init__(self, filename):
    """Object constructor
    """
    self.filename=filename
    self.dataset=Dataset(filename,"r",format="NETCDF3_CLASSIC")
    self.tex_content=""
  def save(self):
    """Save the pdf file
    """
    output_file="output.pdf"
    print("saving the resume for file : {} to {}".format(self.filename, output_file))
    self.init_tex_content()
    self.append_tex_content(self.tex_dimension_table())
    self.append_tex_content(self.tex_variable_table())
    self.tex_plots()
    self.end_tex_content()
    # save the tex_content to a tex file and then use pdflatex
    self.save_tex("temp.tex")
    os.system("pdflatex temp.tex")
    os.system("xdg-open temp.pdf")
  def save_tex(self, filename):
    """Save the Tex content to a temporary file before calling the pdflatex tool.
    
    :param filename: filename to the Tex file
    :type filename: str
    """
    with open(filename , "w") as f:
      f.write(self.tex_content)
      f.close()
  def init_tex_content(self):
    """Initialize the Tex content
    """
    self.tex_content="""\\documentclass[a4paper]{article}
\\usepackage{graphicx}
\\begin{document}
                     """
  def end_tex_content(self):
    """End the Tex content
    """
    end_tex="\n\\end{document}"
    self.append_tex_content(end_tex)
  def append_tex_content(self, content):
    """Append Tex content to current object

    :param content: Tex content to append
    :type content: str
    """
    self.tex_content=self.tex_content+"\n"+content
  def tex_variable_table(self):
    """Generate a Tex table string containing a description of the variables contained in the dataset
    """
    a="""
\\section{Variables}
\\begin{center}
\\begin{tabular}{|c|c|c|}
\\hline
\\textbf{Variable name} & \\textbf{Datatype} & \\textbf{Dimensions} \\\\
"""
    for var in self.dataset.variables:
      v=self.dataset.variables[var]
      a=a+"${}$ & ${}$ & ${}$ \\\\\n".format(var,v.datatype,v.dimensions) 
    a=a+"\\hline\\end{tabular}\\end{center}"
    return a
  def tex_dimension_table(self):
    """Generate a Tex table containing descriptions of the dimensions contained in the dataset.
    """
    a="""
\\section{Dimensions}
\\begin{center}
\\begin{tabular}{|c|c|}
\\hline
\\textbf{Dimension name} & \\textbf{Size} \\\\\n"""
    for dim in self.dataset.dimensions:
      a=a+"{} & {} \\\\\n".format(dim,self.dataset.dimensions[dim].size)
    a=a+"\\hline\\end{tabular}\\end{center}"
    return a
  def plot_timeseries(self, varname, var, t, output):
    """Generate a Timeseries plot

    :param varname: name of the variable to plot
    :type varname: str
    :param var: variable data
    :type var: list type object 
    :param t: time vector
    :type t: list type object
    :param output: path at which to save to figure
    :type output: str
    """
    plt.figure()
    plt.title("Variable : {}".format(varname))
    plt.plot(t,var)
    plt.savefig(output)
    plt.close("all")
  def get_time_data(self):
    """Get the time data for current dataset
    """
    return np.array(self.dataset.variables["Time"][:])
  def tex_plots(self):
    """Add plots to Tex content
    """
    plots={}
    time_data=self.get_time_data()
    for v in self.dataset.variables:
      # if datatype is float then create a plot of the data and save it
      var=self.dataset.variables[v]
      if var.datatype==np.float64:
        var_data=np.array(var[:])
        self.plot_timeseries(v,var_data,time_data, "{}.png".format(v)) 
        plots[v]="{}.png".format(v)
        a="\\section{Plot $"+v+"$}\n\\begin{center}\n\\includegraphics{"+v+".png }\n\\end{center}"
        self.append_tex_content(a)

if __name__=="__main__":
  nc_filename=sys.argv[1]
  viewer=VIViewer(nc_filename)
  viewer.save()
