from os.path import exists, expanduser, isfile, join
from os import listdir, makedirs

import ckan.lib.base as base
import requests
from ckanext.ccca.controllers.package_override import PackageContributeOverride
from ckanext.ccca.controllers.view import ViewController
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
        context = {'model': model, 'session': model.Session,
           'user': c.user or c.author, 'auth_user_obj': c.userobj}
        package_list = get_action('package_list')(context, {})
        mypath = expanduser('~'+user.name)+'/ccca-metadata/'
        log.debug('my path: '+mypath)
        if not exists(mypath):
            log.debug('creating dir: ' + mypath)
            makedirs(mypath)
        files = ''
        for p in package_list: 
            log.debug('package: ' + p)
            pkg_dict = get_action('package_show')(context, {'id': p})
            log.debug('package_id: ' + pkg_dict['id'])
            xml = get_action('show_iso_19139')(context, {'id': pkg_dict['id']})
            log.debug('package_xml: ' + xml)
            filename = mypath+'/'+ pkg_dict['id'] + '.xml'
            f = open(filename, 'w')
            f.write(xml.encode('utf8'))
            f.close()
            files = files + filename+'<br>'
        return "<html><body>written files:<br>"+files+"</body></html>"
        
