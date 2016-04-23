from os.path import exists, expanduser, isfile, join
from os import listdir, makedirs

import ckan.lib.base as base
import requests
from ckanext.ccca.controllers.package_override import PackageContributeOverride
from ckanext.ccca.controllers.view import ViewController
from pylons import config

import sys
import cgi
import logging
import json
import ckan.model as model
import ckan.logic as logic
get_action = logic.get_action

c = base.c
request = base.request
log = logging.getLogger(__name__)

class ExportController(base.BaseController):
    ''' Export metadata from CKAN to a local directory.
    '''    
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
        count = 0;
        for p in package_list: 
            try:
                log.debug('package: ' + p)
                pkg_dict = get_action('package_show')(context, {'id': p})
                log.debug('package_id: ' + pkg_dict['id'])
                xml = get_action('show_iso_19139')(context, {'id': pkg_dict['id']})
                #log.debug('package_xml: ' + xml)
                filename = mypath+'/'+ pkg_dict['id'] + '.xml'
                f = open(filename, 'w')
                f.write(xml.encode('utf8'))
                f.close()
                count+=1
                files = files + filename+'<br>'
            except:
                log.debug('Could not export package ' , str(p) , ": " , sys.exc_info()[0])
        return "<html><body>CCCA CKAN metadata exporter<br><br>Exported ",count," files:<br>",files,"</body></html>"
        
