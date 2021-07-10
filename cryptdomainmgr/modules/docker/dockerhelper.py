#!/usr/bin/env python3

import docker

def kill(targetContainer, signal):
    client = docker.DockerClient(base_url=dockersock)
    containerByName = {c.attrs['Name']: c for c in client.containers.list()}
    containerById = {c.id: c for c in client.containers.list()}
    if targetContainer in containerByName.keys():
        targetContObj = containerByName[targetContainer]
    elif targetContainer in containerById.keys():
        targetContObj = containerById[targetContainer]
    targetContObj.kill(signal)



