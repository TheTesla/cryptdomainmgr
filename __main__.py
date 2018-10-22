#!/usr/bin/env python
# -*- encoding: UTF8 -*-

#######################################################################
#
#    Copyright (c) 2018 Stefan Helmert <stefan.helmert@t-online.de>
#
#######################################################################

import argparse
from cryptdomainmgr.cdmcore import ManagedDomain

if '__main__' == __name__:
    parser = argparse.ArgumentParser(description='Cryptdomainmgr handles interleaved certificate, tlsa, dkim renewal and domain update.')
    parser.add_argument('config_files', metavar='configfiles', type=str, nargs='*', default=[], help='list of configuration files')
    parser.add_argument('--next', dest='phase', action='store_const', const='next', help='Runs rollover if previous run was prepare or cleanup if rollover or prepare if cleanup/first run.') 
    parser.add_argument('--update', dest='phase', action='store_const', const='update', help='Running update sets all static records including A and AAAA regualrly not having an expire date. This should be run as very first time e. g. to upload CAA records.') 
    parser.add_argument('--prepare', dest='phase', action='store_const', const='prepare', help='Creates new certificates and dkim keys. Publishes new TLSA and DKIM records.') 
    parser.add_argument('--rollover', dest='phase', action='store_const', const='rollover', help='Applies new certificates and dkim keys.') 
    parser.add_argument('--cleanup', dest='phase', action='store_const', const='cleanup', help='Removes old unused records and files.') 
    parser.add_argument('--config-content', dest='configcontent', type=str, default='', help='configuration content as argument instead of configuration files')
    
    
    args = parser.parse_args()
    print(args)
    configcontent = str(args.configcontent).replace(' ', '\n')

    
    mgr = ManagedDomain()
    mgr.run(args.config_files, args.phase, configcontent)





