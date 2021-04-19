
import os
import docker



def dockerMyContainerID():
    with open('/proc/self/cgroup', 'r') as f:
        cgroup = {e.split(':')[0]:e.split(':') for e in f.read().splitlines()}
        if 3 > len(cgroup['1']):
            return ''
        if 'docker' != cgroup['1'][1]:
            return ''
        return cgroup['1'][2]

def dockerPathMap(dockersock, targetContainer, targetDirectory, sourceContainer=''):
    if '' == sourceContainer:
        sourceContainer = dockerMyContainerID()
    client = docker.DockerClient(base_url=dockersock)
    cAttrsbyName = {c.attrs['Name']: c.attrs for c in client.containers.list()}
    print(cAttrsbyName)
    cAttrsbyId = {c.id: c.attrs for c in client.containers.list()}
    if targetContainer in cAttrsbyName.keys():
        targetContAttrs = cAttrsbyName[targetContainer]
    elif targetContainer in cAttrsbyId.keys():
        targetContAttrs = cAttrsbyId[targetContainer]
    if sourceContainer in cAttrsbyName.keys():
        sourceContAttrs = cAttrsbyName[sourceContainer]
    elif sourceContainer in cAttrsbyId.keys():
        sourceContAttrs = cAttrsbyId[sourceContainer]
    sourceMap = {e['Destination']: e['Source'] for e in sourceContAttrs['Mounts']}
    targetMap = {e['Destination']: e['Source'] for e in targetContAttrs['Mounts']}
    targetMounts = {os.path.normpath(d): os.path.normpath(s) for d, s in targetMap.items() if os.path.normpath(d) == os.path.commonpath([os.path.normpath(d),os.path.normpath(targetDirectory)])}
    targetSources = [os.path.join(s,os.path.relpath(os.path.normpath(targetDirectory), d)) for d, s in targetMounts.items()]
    sourceDestinations = [os.path.join(d,os.path.relpath(os.path.normpath(ts),s))  for ts in targetSources for d, s in sourceMap.items() if os.path.normpath(s) == os.path.commonpath([os.path.normpath(s),os.path.normpath(ts)])]
    return sourceDestinations


