##############################################################################
# Copyright (c) 2013-2016, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the LICENSE file for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################

from spack import *


class Jdk(Package):
    """Install PPC64LE java JDK"""

    homepage = "https://www.ibm.com/developerworks/java/jdk/docs.html"
    url      = "https://gitlab.ccs.ornl.gov/ua/IBM-java-PPC64LE/repository/archive.zip?ref=master"

    version('8.0-3.11', '###')

    def install(self, spec, prefix):
        install_bin = self.package_dir + "/ibm-java-sdk-8.0-3.11-ppc64le-archive.bin"
        # Make bin executable
        chmod=which("chmod")
        chmod("+x", install_bin)

        # Write installer properties to file
        installer_properties = """ LICENSE_ACCEPTED=TRUE
                                   USER_INSTALL_DIR=""" + prefix
        properties_file = open(self.package_dir + "installer.properties")
        properties_file.write(installer_properties)
        properties_file.close()

        # Run .bin
	source=which("source")
        source(install_bin + "-f installer.properties -i silent")
