#!/usr/bin/env python3
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2021 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import subprocess as sp
import sys
from simpleloggerplus import simpleloggerplus as log

def runCmdGen(cmd, stderr=sp.STDOUT, env=None):
    if int(sys.version.split('.')[1]) < 7:
        proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=stderr, shell=True,
                        universal_newlines=True, env=env)
    else:
        proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=stderr, shell=True,
                        text=True, encoding='utf-8', env=env)
    for stdoutLine in iter(proc.stdout.readline, ""):
        yield stdoutLine
    proc.stdout.close()
    rc = proc.wait()
    if rc:
        raise sp.CalledProcessError(rc, cmd)

def runCmd(cmd, stderr=sp.STDOUT, env=None):
    log.info("RUN CMD: {}".format(cmd))
    stdout = ""
    try:
        for stdoutLine in runCmdGen(cmd, stderr, env):
            log.relog("    "+stdoutLine[:-1])
            stdout += stdoutLine
    except sp.CalledProcessError as e:
        raise sp.CalledProcessError(e.returncode, e.cmd, stdout)
    return stdout

