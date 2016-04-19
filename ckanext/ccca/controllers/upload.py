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
        #ckan_url = config.get('ckan.site_url', '//localhost:5000')
        mypath = expanduser('~'+user.name)+'/'
        filename = reqData['filename']
        url = mypath + reqData['filename']
        log.debug('upload file url: '+ url)
        log.debug('upload package id: '+ reqData['package_id'])
        #response = requests.post(ckan_url+'/api/action/resource_create',
        upload = cgi.FieldStorage()
        upload.filename = filename
        upload.filepath = mypath
        upload.file=file(url)
        data={'package_id': reqData['package_id'],
            'url': url,
            'upload': upload
        }
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
        resource_dict = get_action('resource_create')(context, data)
        return json.dumps(resource_dict);