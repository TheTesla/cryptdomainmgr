#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################


from copy import deepcopy

def deepReplace(structure, replaceDict):
    if type(structure) is list:
        for e in structure:
            deepReplace(e, replaceDict)
    elif type(structure) is dict:
        for k, v in structure.items():
            deepReplace(v, replaceDict)
            if k in replaceDict:
                if callable(replaceDict[k]):
                    structure[k] = replaceDict[k](structure[k])
                else:
                    structure[k] = replaceDict[k]
    return


def starPW(x):
    return len(x) * '*'

def passwordFilter(structure):
    s = deepcopy(structure)
    deepReplace(s, {'passwd': starPW})
    deepReplace(s, {'password': starPW})
    deepReplace(s, {'passwort': starPW})
    return s

