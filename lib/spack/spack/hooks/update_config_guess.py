from spack import *
import llnl.util.tty as tty
import os

def files_named(name):
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in [f for f in filenames if f == name]:
            yield os.path.join(dirpath, filename)

def pre_install(pkg):
    cp = which("cp")
    config_dir = os.path.dirname(__file__)

    updated_config_guess = os.path.join(config_dir, "config.guess")
    for f in files_named("config.guess"):
        tty.msg("Updating %s" % f)
        cp(updated_config_guess, f)

    updated_config_sub = os.path.join(config_dir, "config.sub")
    for f in files_named("config.sub"):
        tty.msg("Updating %s" % f)
        cp(updated_config_sub, f)
