from __future__ import print_function

import argparse
import re
import collections
import os
import shutil
import sys
import time

import llnl.util.tty as tty
import spack
import spack.cmd
from spack.cmd.view import filter_exclude, flatten
import spack.cmd.common.arguments as arguments
from llnl.util.filesystem import join_path, mkdirp, ancestor
from llnl.util.lang import partition_list
from spack.modules import module_types, parse_config_options


description = "OLCF Specific functions"


def setup_parser(subparser):
    olcf_parsers = subparser.add_subparsers(metavar='SUBCOMMAND',
                                            dest='olcf_command')

    # Subcommands
    olcf_actions = {
            'modules': olcf_parsers.add_parser('modules',
                                               help='Manage module files'),
            }
    subparsers = dict()
    for k, p in olcf_actions.items():
        subparsers[k] = p.add_subparsers(metavar='SUBCOMMAND', dest='action')
    modules = {
            'create': subparsers['modules'].add_parser(
                    'create', help='Create modulefiles'),
            }

    # module management
    modules['create'].add_argument(
            '--delete-tree', action='store_true',
            help='Delete the modulefile tree with refresh')
    modules['create'].add_argument(
            '--naming-scheme', help='Modulefile name pattern.')
    modules['create'].add_argument(
            'query_specs', nargs=argparse.REMAINDER,
            help='optional targeted specs')
    arguments.add_common_arguments(modules['create'], ['yes_to_all'])


class OLCFModule(module_types['tcl']):
    sw_root = ancestor(__file__, 6)
    path = join_path(sw_root, 'modulefiles')
    default_naming_format = '{name}/{version}'

    @property
    def file_name(self):
        compver = str(self.spec.compiler.version)
        match = re.search('(^[0-9]*\.[0-9]*)', compver)
        compver = match.group(1) if match else compver
        return join_path(self.path, self.use_name)
    
    @property
    def use_name(self):
        naming_tokens = self.tokens
        naming_scheme = self.naming_scheme
        name = naming_scheme.format(**naming_tokens)
        # Not everybody is working on linux...
        parts = name.split('/')
        name = join_path(*parts)
        # Add optional suffixes based on constraints
        configuration, _ = parse_config_options(self)
        suffixes = [name]
        for constraint, suffix in configuration.get('suffixes', {}).items():
            if constraint in self.spec:
                suffixes.append(suffix)
        name = '-'.join(suffixes)
        return name


def iso8601(epoch_seconds):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(epoch_seconds))


def _handle_module_name_clashes(file2writer, writers):
    history = collections.defaultdict(dict)
    if len(file2writer) != len(writers):
        message = 'Name clashes detected in module files:\n'
        for filename, writer_list in file2writer.items():
            writers_by_ctime = history[filename]
            if len(writer_list) > 1:
                message += '\nfile : {0}\n'.format(filename)
                for _writer in writer_list:
                    spec = _writer.spec
                    ctime = os.path.getctime(spec.prefix)
                    writers_by_ctime[ctime] = _writer
                    message += 'spec : {0}\n'.format(_writer.spec.cshort_spec)
                    message += '       created {0}\n'.format(iso8601(ctime))
                writer = writers_by_ctime[max(writers_by_ctime)]
                message += 'used : {0}\n'.format(
                        writer.spec.cshort_spec)
                file2writer[filename] = [writer]
        tty.error(message)


def create_modules(args):
    """Generate module files for item in specs"""
    # Prompt a message to the user about what is going to change
    q_args = {
        'explicit': True,
        'installed': True,
        'known': True,
    }

    query_specs = spack.cmd.parse_specs(args.query_specs)
    query_specs, nonexisting = partition_list(
        query_specs, lambda s: spack.repo.exists(s.name) or not s.name)

    if nonexisting:
        msg = "No such package%s: " % ('s' if len(nonexisting) > 1 else '')
        msg += ", ".join(s.name for s in nonexisting)
        tty.msg(msg)
        if not query_specs:
            return

    if not query_specs:
        specs = set(spack.installed_db.query(**q_args))
    else:
        results = [set(spack.installed_db.query(qs, **q_args))
                   for qs in query_specs]
        specs = set.union(*results)

    if not specs:
        tty.msg('No package matches your query')
        return


    cls = OLCFModule
    if args.naming_scheme is not None:
        cls.naming_scheme = args.naming_scheme 

    writers = [cls(spec) for spec in specs]
    file2writer = collections.defaultdict(list)
    for item in writers:
        file2writer[item.file_name].append(item)

    _handle_module_name_clashes(file2writer, writers)

    for fname, writers in file2writer.items():
        for x in writers:
            print('==>', x.spec.cshort_spec, 'at\n',
                  '  ', x.file_name)

    # Proceed generating module files
    if os.path.isdir(cls.path) and args.delete_tree:
        shutil.rmtree(cls.path, ignore_errors=False)
    mkdirp(cls.path)
    for x in writers:
        x.write(overwrite=True)


def modules(args):
    action = {'create': create_modules,}
    action[args.action](args)


def olcf(parser, args):
    action = {'modules': modules,
             }
    action[args.olcf_command](args)

