from os.path import expanduser, isfile, join
from os import listdir

import ckan.lib.base as base
import requests
from ckanext.ccca.controllers.package_override import PackageContributeOverride
from pylons import config

import cgi
import logging
import json
import ckan.model as model
import ckan.logic as logic
get_action = logic.get_action

c = base.c
request = base.request
log = logging.getLogger(__name__)

'''

@author: Christoph Kinkeldey
'''
class ExportController(base.BaseController):
    
    def export_metadata_xml(self):
        user = c.userobj
        data = base.request.params
        log.debug('username: '+user.name)
        log.debug('apikey: '+user.apikey)
        if 'apikey' in data and data['apikey']==user.apikey:
            mypath = expanduser('~'+user.name)+'/'
            log.debug('my path: '+mypath)
            onlyfiles = [f for f in listdir(mypath) if (isfile(join(mypath, f)) and not f.startswith('.'))]
            return json.dumps(onlyfiles)
        else:
            return "no API key"
         
    