from os.path import expanduser, isfile, join
from os import listdir

import ckan.lib.base as base
import requests

from pylons import config

import logging
import json

c = base.c
request = base.request
log = logging.getLogger(__name__)

'''

@author: Christoph Kinkeldey
'''
class UploadController(base.BaseController):
    
    def show_filelist(self):
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
         
    def upload_file(self):
        user = c.userobj
        reqData = base.request.params
        ckan_url = config.get('ckan.site_url', '//localhost:5000')
        mypath = expanduser('~'+user.name)+'/ccca-import/'
        url = mypath + reqData['filename']
        log.debug('file url: '+ url)
        log.debug('package id: '+ reqData['package_id'])
        response = requests.post(ckan_url+'/api/action/resource_create',
              data={'package_id': reqData['package_id'],
                    'url': url,
                    #'name': reqData['name']
                    },
              headers={"X-CKAN-API-Key": reqData['apikey']},
              files=[('upload', file(url))])
        return response