#!/usr/bin/env python
# coding=utf-8
"""
EQTeXSVG3 is the fork of EQTeXSVG, and can be used in Inkscape v1.0 which depends on Python3. 
- License: GNU General Public License v2.0
"""


import os
import sys
import tempfile
from subprocess import Popen, PIPE
from io import BytesIO
import platform
import inkex
from lxml import etree


# Manual Setting for Mac ("latex" command's path is required) 
MACOS_PATH = "/Library/TeX/texbin/"


def exec_cmd(cmd_line):
    """Launch given command line"""
    process = Popen(cmd_line, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (std_out, std_err) = process.communicate()
    return process.returncode, std_out, std_err


class Equation:
    """Current LaTeX equation"""
    def __init__(self, param):

        self.document = param["document"]
        self.pkgstring = param["packages"]
        self.orig_dir_path = os.getcwd()
        self.header = None
        self.file = "eq"
        self.file_tex = self.file + ".tex"
        self.file_dvi = self.file + ".dvi"
        self.svg = None

        if param["formula"] != "":
            self.formula = param["formula"] 
        else:
            raise inkex.AbortExtension("Without formula, no equation will be generated")

        try:
            self.temp_dir = tempfile.TemporaryDirectory()
        except:
            raise inkex.AbortExtension("Temporary directory cannot be created")


    def path_programs(self):
        """Try to launch latex and dvisvgm commands"""
        if platform.system() == "Darwin":
            latex_cmd = MACOS_PATH + "latex --version"
            dvisvgm_cmd = MACOS_PATH + "dvisvgm -V"
        else:
            latex_cmd = "latex --version" 
            dvisvgm_cmd = "dvisvgm -V" 

        retcode_latex = exec_cmd(latex_cmd)[0]
        retcode_dvisvgm = exec_cmd(dvisvgm_cmd)[0]
        
        if (retcode_latex or retcode_dvisvgm) != 0: 
            self.temp_dir.cleanup()
            raise inkex.AbortExtension("TeX Live cannot be used") 


    def parse_pkgs(self):
        """Add custom packages to TeX source"""
        header = ""

        if self.pkgstring != "":
            pkglist = self.pkgstring.replace(" ", "").split(",")
            for pkg in pkglist:
                if pkg:
                    header += "\\usepackage{{{}}}\n".format(pkg)
        
        self.header = header


    def generate_tex(self):
        """Generate the LaTeX equation file"""
        self.parse_pkgs()

        # delete the Math delimiters
        delimiters = [
            "$", "\\(", "\\)", "\\[", "\\]", 
            "\\begin{equation}", "\\end{equation}", 
            "\\begin{equation*}", "\\end{equation*}", 
            "\\begin{math}", "\\end{math}", 
            "\\begin{displaymath}", "\\end{displaymath}"
            ]
        for delimiter in delimiters:
            self.formula = self.formula.replace(delimiter, "")
        self.formula = self.formula.strip()

        texstring = "\\documentclass{article}\n"
        texstring += "\\usepackage{amsmath}\n"
        texstring += "\\usepackage{amssymb}\n"
        texstring += "\\usepackage{amsfonts}\n"
        texstring += self.header
        texstring += "\\thispagestyle{empty}\n"
        texstring += "\\begin{document}\n"
        texstring += "$" + self.formula + "$"
        texstring += "\n\\end{document}\n"

        try:
            os.chdir(self.temp_dir.name)
            tex = open(self.file_tex, "w")
            tex.write(texstring)
            tex.close()
        except IOError:
            os.chdir(self.orig_dir_path)
            self.temp_dir.cleanup()
            raise inkex.AbortExtension("TeX file not generated") 
        
        os.chdir(self.orig_dir_path)


    def generate_dvi(self):
        """Generate the DVI equation file"""
        if platform.system() == "Darwin":
            cmd_line = MACOS_PATH + "latex "
        else:
            cmd_line = "latex "
        cmd_line += "-output-directory={}".format(self.temp_dir.name)
        cmd_line += " -halt-on-error "
        cmd_line += "{}".format(self.file_tex)

        os.chdir(self.temp_dir.name)
        retcode = exec_cmd(cmd_line)[0]
        os.chdir(self.orig_dir_path)

        if retcode != 0:
            self.temp_dir.cleanup()
            raise inkex.AbortExtension("DVI file not generated with LaTeX")  


    def generate_svg(self):
        """Generate the SVG equation string/file"""
        if platform.system() == "Darwin":
            cmd_line = MACOS_PATH + "dvisvgm "
        else:
            cmd_line = "dvisvgm "
        cmd_line += "-v0 -a -n -s " 
        cmd_line += "{}".format(self.file_dvi)

        os.chdir(self.temp_dir.name)
        retcode, std_out,_ = exec_cmd(cmd_line)
        os.chdir(self.orig_dir_path)

        self.temp_dir.cleanup()

        if retcode == 0:
            self.svg = std_out
        else:
            raise inkex.AbortExtension("SVG file not generated with dvisvgm")


    def import_svg(self):
        """Import the SVG equation file into current layer"""
        svg_uri = inkex.NSS["svg"]
        xlink_uri = inkex.NSS["xlink"]
        try:
            tree = etree.parse(BytesIO(self.svg))
            eq_tree = tree.getroot()
        except Exception:
            raise inkex.AbortExtension("SVG file not imported")
        
        # Collect document ids
        doc_ids = {}
        doc_id_nodes = self.document.xpath("//@id")

        for id_nodes in doc_id_nodes:
            doc_ids[id_nodes] = 1

        name = "equation_00"

        # Make sure that the id/name is unique
        index = 0
        while name in doc_ids:
            name = "equation_{:02}".format(index)
            index += 1

        # Create new group node containing the equation
        eqn = etree.Element("{{{}}}g".format(svg_uri))
        eqn.set("id", name)
        eqn.set("style", "fill: black;")
        eqn.set("title", str(self.formula))

        dic = {}
        counter = 0

        # Get the Ids from <defs/> and make unique Ids from name and counter
        for elt in eq_tree:
            if elt.tag == ("{{{}}}defs".format(svg_uri)):
                for subelt in elt:
                    dic[subelt.get("id")] = "{}_{:02}".format(name, counter)
                    counter += 1
        
        # Build new equation nodes
        for elt in eq_tree:
            eqn_elt = etree.SubElement(eqn, elt.tag)
            if "id" in elt.keys():
                eqn_elt.set("id", name + "_" + elt.tag.split("}")[-1])
            for subelt in elt:
                eqn_subelt = etree.SubElement(eqn_elt, subelt.tag)
                for key in subelt.keys():
                    eqn_subelt.set(key, subelt.attrib[key])
                if "id" in subelt.attrib:
                    eqn_subelt.set("id", dic[subelt.get("id")])
                xlink = "{{{}}}href".format(xlink_uri)
                if xlink in subelt.attrib:
                    eqn_subelt.set(xlink, "#" + dic[subelt.get(xlink).split("#")[-1]])
        
        self.svg = eqn


    def generate(self):
        """Generate SVG from LaTeX equation file"""
        self.path_programs()
        self.generate_tex()
        self.generate_dvi()
        self.generate_svg()
        self.import_svg()
        return self.svg


class InsertEquation(inkex.EffectExtension):
    """Insert LaTeX equation into the current Inkscape instance"""
    def add_arguments(self, pars):
        pars.add_argument("-f", "--formule", type=str, default="", help="LaTeX formula")
        pars.add_argument("-p", "--packages", type=str, default="", help="Additional packages")


    def effect(self):
        """Generate inline equation"""
        param = {
            "document": getattr(self, "document", None),
            "formula": self.options.formule,
            "packages": self.options.packages
        }
        equation = Equation(param=param)
        current_eq = equation.generate()

        if current_eq != None:
            self.svg.get_current_layer().append(current_eq)
        else:
            raise inkex.AbortExtension("Equation not generated")


if __name__ == "__main__":
    InsertEquation().run()
