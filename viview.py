"""
Module and tool for visualizing the contents of a NetCDF dataset or a Virtual Instrument data collection

Basic use of the script : python3 viview.py <path to netcdf file>

Output of the script : produce a pdf file containing a resume of the NetCDF file passed as argument

Format of the output file : 1. Name of the file, table of dimensions, table of variables

Table of dimensions : 

\begin{tabular}{cc}
\texbf{Name} & \textbf{Size} \\
dim1 & dim1_size \\
dim2 & dim2_size \\
\end{tabular}

Table of variables : 
\begin{tabular}{ccc}
\textbf{Name} & \textbf{Datatype} & \textbf{Fill Value} \\
var1 & var1_datatype & var1_fillvalue \\
\end{tabular}

For each variable in the file try to plot the data over the whole timespan
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import os

class VIViewer:
  def __init__(self, filename):
    self.filename=filename
    self.dataset=Dataset(filename,"r",format="NETCDF4_CLASSIC")
    self.tex_content=""
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
    print("TEX CONTENT")
    print(self.tex_content)
    os.system("pdflatex temp.tex")
    os.system("xdg-open temp.pdf")
  def save_tex(self, filename):
    with open(filename , "w") as f:
      f.write(self.tex_content)
      f.close()
  def init_tex_content(self):
    self.tex_content="""\\documentclass[a4paper]{article}
\\usepackage{graphicx}
\\begin{document}
                     """
  def end_tex_content(self):
    end_tex="\n\\end{document}"
    print("adding end of tex document")
    self.append_tex_content(end_tex)
  def append_tex_content(self, content):
    print("appending content : ", content)
    self.tex_content=self.tex_content+"\n"+content
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
  def tex_plots(self):
    plots={}
    for v in self.dataset.variables:
      # if datatype is float then create a plot of the data and save it
      var=self.dataset.variables[v]
      if var.datatype==np.float64:
        plt.figure()
        plt.title(v)
        plt.plot(var[:])
        plt.savefig("{}.png".format(v))
        plots[v]="{}.png".format(v)
        a="\\section{Plot $"+v+"$}\n\\begin{center}\n\\includegraphics{"+v+".png }\n\\end{center}"
        self.append_tex_content(a)
if __name__=="__main__":
  nc_filename=sys.argv[1]
  viewer=VIViewer(nc_filename)
  viewer.save()
