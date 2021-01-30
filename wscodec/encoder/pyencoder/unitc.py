#  cuplcodec encodes environmental sensor data into a URL and the reverse.
#
#  https://github.com/cuplsensor/cuplcodec
#
#  Original Author: Malcolm Mackay
#  Email: malcolm@plotsensor.com
#  Website: https://cupl.co.uk
#
#  Copyright (C) 2021. Plotsensor Ltd.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import cffi
import subprocess
import re
import pycparser
from pycparser import c_generator
import os
import importlib
import weakref
import pkg_resources

resource_package = __package__
print(__package__)
c_encoder_path = '/'.join(('', 'c_encoder', ''))
pycparser_path = '/'.join(('', 'pycparser', ''))
sharedobj_path = '/'.join(('', 'sharedobj', ''))

ENCODER_CSOURCE_PATH = pkg_resources.resource_filename(resource_package, c_encoder_path)
PYCPARSER_PATH = pkg_resources.resource_filename(resource_package, pycparser_path)
SHAREDOBJ_PATH = pkg_resources.resource_filename(resource_package, sharedobj_path)

global_weakkeydict = weakref.WeakKeyDictionary()


class CFFIGenerator(pycparser.c_generator.CGenerator):
    def __init__(self, blacklist):
        super().__init__()
        self.blacklist = blacklist

    def visit_Decl(self, n, *args, **kwargs):
        result = super().visit_Decl(n, *args, **kwargs)
        if isinstance(n.type, pycparser.c_ast.FuncDecl):
            if n.name not in self.blacklist:
                return 'extern "Python+C" ' + result
        return result


def convert_function_declarations(source, blacklist):
    return CFFIGenerator(blacklist).visit(pycparser.CParser().parse(source))


class FunctionList(pycparser.c_ast.NodeVisitor):
    def __init__(self, source):
        self.funcs = set()
        self.visit(pycparser.CParser().parse(source))

    def update(self, otherlist):
        self.funcs.update(otherlist)

    def visit_FuncDef(self, node):
        self.funcs.add(node.decl.name)


def preprocess(source):
    return subprocess.run(['gcc', '-E', '-P', '-', '-I'+ENCODER_CSOURCE_PATH, '-I'+PYCPARSER_PATH+'/utils/fake_libc_include'],
                          input=source, stdout=subprocess.PIPE,
                          universal_newlines=True, check=True).stdout


def load(filename, depfilenames=list()):
 """
 Load a file
 """
 name = __package__ + '.sharedobj.' + filename + 'py'
 # load source code
 source = open(ENCODER_CSOURCE_PATH + filename + '.c').read()

 for depfilename in depfilenames:
     depsource = open(ENCODER_CSOURCE_PATH + depfilename + '.c').read()
     source = source + depsource

 # preprocess all header files for CFFI
 includes = preprocess(''.join(re.findall('\s*#include\s+.*', source)))

 # Obtain a list of local functions
 local_functions = FunctionList(preprocess(source)).funcs
 # prefix external functions (not in the list) with extern "Python+C"
 includes = convert_function_declarations(includes, local_functions)

 # Obtain the absolute directory path of this file.
 abspath = os.path.dirname(__file__)

 # Pass source code and libraries to FFI Builder
 ffibuilder = cffi.FFI()

 # Add all includes to the cdef attribute
 ffibuilder.cdef(includes + "nv_t nv;", packed=False)

 print("SOURCE " + source)

 # Add the source, library sources and include directories
 ffibuilder.set_source(name, source, include_dirs=[ENCODER_CSOURCE_PATH])

 return ffibuilder
