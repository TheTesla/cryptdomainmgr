#!/usr/bin/env python3
# -*- encoding: UTF8 -*-


try:
    import git
    repo = git.Repo(search_parent_directories=False)
    __version__ = '-'.join(repo.git.describe('--tags').split('-')[:2])
    with open('version', 'wt') as v:
        v.write(__version__)
except Exception as e:
#except ImportError as e:
    try:
        with open('version', 'rt') as v:
            __version__ = v.read()
    except OSError as e:
        log.warn("Can't open version file.")
        __version__ = ''


