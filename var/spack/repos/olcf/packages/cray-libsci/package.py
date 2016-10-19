from spack import *

class CrayLibsci(Package):
    """Description"""

    homepage = "http://www.example.com"
    url      = "https://github.com/robertdfrench/empty"

    version('16.06.1', git='https://github.com/robertdfrench/empty.git')

    def install(self, spec, prefix):
      mkdirp(prefix.lib)
      which('ln')
      ln('-s',prefix.lib+'/libblas.a','/opt/cray/libsci/16.06.1/GNU/4.9/mc8/lib/libsci_gnu_49.a')
