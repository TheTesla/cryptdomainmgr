#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2021 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import os
from shutil import copyfile
from subprocess import check_output, CalledProcessError
from simpleloggerplus import simpleloggerplus as log
from subprocess import check_output, CalledProcessError
from cryptdomainmgr.modules.common.cdmstatehelper import isReady
from cryptdomainmgr.modules.common.cdmfilehelper import makeDir

import docker

defaultConfig = {'depends': 'dhparam, cert','dhparam': 'auto', 'cert': 'auto', 'dirint': 'auto', 'dirext': 'auto', 'dockersock': 'unix://var/run/docker.sock'}


def dockerMyContainerID():
    with open('/proc/self/cgroup', 'r') as f:
        cgroup = {e.split(':')[0]:e.split(':') for e in f.read().splitlines()}
        if 3 > len(cgroup['1']:
            return ''
        if 'docker' != cgroup['1'][1]:
            return ''
        return cgroup['1'][2]



def dockerPathMap(dockersock, targetContainer, targetDirectory, sourceContainer, sourceDirectory):
    client = docker.DockerClient(base_url=dockersock)
    cAttrsbyName = {c.attrs['Name']: c.attrs for c in client.containers.list()}
    cAttrsbyId = {c.id: c.attrs for c in client.containers.list()}
    if targetContainer in cAttrsbyName.keys():
        targetContAttrs = cAttrsbyName[targetContainer]
    elif targetContainer in cAttrsbyId.keys():
        targetContAttrs = cAttrsbyId[targetContainer]
    if sourceContainer in cAttrsbyName.keys():
        sourceContAttrs = cAttrsbyName[sourceContainer]
    elif sourceContainer in cAttrsbyId.keys():
        sourceContAttrs = cAttrsbyId[sourceContainer]


def prepare(serviceConfig, serviceState, state):
    serviceState.setOpStateDone()

def rollover(serviceConfig, serviceState, state):
    serviceState.setOpStateWaiting()
    if not isReady(serviceConfig, state, ['dhparam', 'cert']):
        return
    serviceState.setOpStateRunning()
    certNames = serviceConfig['cert']


    if 'auto' == serviceConfig['dirext'] or 'auto' == serviceConfig['dirint']:
        client = docker.DockerClient(base_url=serviceConfig['dockersock'])

        containers = [c for c in client.containers.list() if c.attrs['Name'][1:] == serviceConfig['container']]
        if len(containers) == 0:
            log.error("container does not exist")
        container = containers[0]
        log.info("Updating traefik container: {}".format(container.attrs['Name']))
        destinations = [e.replace(' ','').split('=')[1] for e in container.attrs['Args'] if e.replace(' ','').split('=')[0] == '--providers.file.directory']
        if len(destinations) == 0:
            log.error("traefik container misses providers.file.directory argument")
        destination = destinations[0]
        mounts = [e for e in container.attrs['Mounts'] if os.path.normpath(e['Destination']) == os.path.normpath(destination)]
        if len(mounts) == 0:
            log.error("volume missing for providers.file.directory")
        mount = mounts[0]


    traefikProvidersFileDirectory = mount['Source'] if 'auto' == serviceConfig['dirext'] else serviceConfig['dirext'] #'./configuration'
    traefikConfigFilename = os.path.join(traefikProvidersFileDirectory,'files/configuration.toml')
    traefikCertDir = os.path.join(traefikProvidersFileDirectory,'certs')
    traefikProvidersFileDirectoryMount = mount['Destination'] if 'auto' == serviceConfig['dirint'] else serviceConfig['dirint'] # '/configuration'
    traefikConfigFilenameMount = os.path.join(traefikProvidersFileDirectoryMount,'files/configuration.toml')
    traefikCertDirMount = os.path.join(traefikProvidersFileDirectoryMount,'certs')

    log.info(" -> Volume: {}:{}".format(traefikProvidersFileDirectory, traefikProvidersFileDirectoryMount))

    tcfc = ''
    for certName in certNames:
        certState = state.getSubstate('cert').getSubstate(certName).result
        certPath = os.path.join(traefikCertDir,certName,'cert.pem')
        keyPath = os.path.join(traefikCertDir,certName,'key.pem')
        certPathMount = os.path.join(traefikCertDirMount,certName,'cert.pem')
        keyPathMount = os.path.join(traefikCertDirMount,certName,'key.pem')
        makeDir(os.path.dirname(certPath))
        copyfile(certState['fullchainfile'], certPath)
        log.info('  {} -> {}'.format(certState['fullchainfile'], certPath))
        copyfile(certState['keyfile'], keyPath)
        log.info('  {} -> {}'.format(certState['keyfile'], keyPath))
        tcfc += '[[tls.certificates]]\n   certFile = "{}"\n   keyFile = "{}"\n\n'.format(certPathMount, keyPathMount)
        makeDir(os.path.dirname(traefikConfigFilename))
        with open(traefikConfigFilename,'w') as f:
            f.write(tcfc)
        # traefik reloads config and certs only if a random file is written in 
        # traefik's config root directory specified by:
        # --providers.file.directory = <config root directory>
        with open(os.path.join(traefikProvidersFileDirectory,'reloadtrigger'), 'w') as f:
            f.write('')

    #print(tcfc)
    log.info('  -> Traefik reload')
    try:
        pass
        #rv = check_output(('systemctl', 'start', 'apache2'))
        #rv = check_output(('systemctl', 'reload', 'apache2'))
    except CalledProcessError as e:
        log.error(e.output)
        raise(e)
    serviceState.setOpStateDone()

def cleanup(serviceConfig, serviceState, state):
    serviceState.setOpStateDone()

