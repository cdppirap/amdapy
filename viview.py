## NetCDF file resume generator.
#
#  @file viview.py
#  @author Alexandre Schulz
#  @brief Script used to generate a PDF file listing the characteristics of the netcdf files given as input.
import sys
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import os

## VIViewer class documentation.
#
#  This class is used to generate the PDF file.
class VIViewer:
  ## VIViewer.__init__
  #
  #  VIViewer initialization.
  #  @param self object pointer.
  #  @filename netcdf file path.
  def __init__(self, filename):
    self.filename=filename
    self.dataset=Dataset(filename,"r",format="NETCDF3_CLASSIC")
    self.tex_content=""
  ## VIViewer.save
  #
  #  Create the PDF file.
  #  @param self object pointer.
  def save(self):
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
  ## VIViewer.save_tex
  #
  #  Save the tex content.
  #  @param self object pointer.
  #  @param filename name of the tex file.
  def save_tex(self, filename):
    with open(filename , "w") as f:
      f.write(self.tex_content)
      f.close()
  ## VIViewer.init_tex_content
  #
  #  Initialize the tex content.
  #  @param self object pointer.
  def init_tex_content(self):
    self.tex_content="""\\documentclass[a4paper]{article}
\\usepackage{graphicx}
\\begin{document}
                     """
  ## VIViewer.end_tex_content
  #
  #  End the tex document content.
  #  @param self object pointer.
  def end_tex_content(self):
    end_tex="\n\\end{document}"
    self.append_tex_content(end_tex)
  ## VIViewer.append_tex_content
  #
  #  Add content to the tex content.
  #  @param self object pointer.
  #  @param content tex content to add to document.
  def append_tex_content(self, content):
    self.tex_content=self.tex_content+"\n"+content
  ## VIViewer.tex_variable_table
  #
  #  Get tex code for the variable table.
  #  @param self object pointer.
  #  @return str tex table.
  def tex_variable_table(self):
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
  ## VIViewer.tex_dimension_table
  #
  #  Get tex code for the dimension table.
  #  @param self object pointer.
  #  @return str tex table.
  def tex_dimension_table(self):
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
  ## VIViewer.plot_timeseries
  #
  #  Plot a timeseries.
  #  @param self object pointer.
  #  @param var variable.
  def plot_timeseries(self, varname, var, t, output):
    plt.figure()
    plt.title("Variable : {}".format(varname))
    plt.plot(t,var)
    plt.savefig(output)
    plt.close("all")
  ## VIViewer.get_time_data
  #
  #  Get the time data.
  #  @param self object pointer.
  #  @return np.array
  def get_time_data(self):
    return np.array(self.dataset.variables["Time"][:])
  ## VIViewer.tex_plots
  #
  #  Get the plots.
  #  @param self object pointer.
  #  @return str tex content.
  def tex_plots(self):
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
