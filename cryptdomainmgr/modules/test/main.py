#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2020 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################


def prepare(config, state):
    subState = state.getSubstate('test')
    subState.setOpStateDone()

    for testSecName, testConfig in config['test'].items():
        sub2State = subState.getSubstate(testSecName)
        sub2State.setOpStateDone()

