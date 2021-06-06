#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

import os

# VERSION
__version__ = "0.2.3-62"

try:
    import git
    #from git.exc import InvalidGitRepositoryError
    repo = git.Repo(search_parent_directories=False)
    __version__ = '-'.join(repo.git.describe('--tags').split('-')[:2])
    print(__file__)
    print(os.path.realpath(__file__))
    with open(os.path.realpath(__file__), 'rt') as v:
        print(__file__)
        initfile = v.read()
        lines = initfile.splitlines()
        bg = [i for i, e in enumerate(lines) if 'VERSION' in e][0]
        print(bg)
        lines[bg+1] = "__version__ = \"{}\"".format(__version__)
        initfile = '\n'.join(lines)
    with open(os.path.realpath(__file__), 'wt') as v:
        v.write(initfile)
#except ImportError as e:
except Exception as e:
    print(e)