import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.base as base
from pylons import g, c
from jinja2 import Environment, FileSystemLoader
from os import listdir
from os.path import isfile, join, expanduser

import logging
import json

log = logging.getLogger(__name__)

class CccaPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ccca')
        
    def before_map(self, map):
        map.connect('sftp_upload', '/sftp_upload', controller='ckanext.ccca.plugin:UploadController', action='show_filelist')
        return map
    
    
    def after_map(self, map):
        #log.fatal("==================================> %s" % map)
        return map

class UploadController(base.BaseController):
    
    def show_filelist(self):
        user = c.userobj
        data = base.request.params
        log.debug(user)
        if 'apikey' in data and data['apikey']==user.apikey:
            #mypath = expanduser("~")+'/../'+user.name+'/ckan/'
            mypath = '/Users/ck/git/ckanext-ccca/ckanext/ccca/public/test'
            onlyfiles = [f for f in listdir(mypath) if (isfile(join(mypath, f)) and not f.startswith('.'))]
            return json.dumps(onlyfiles)
        else:
             return "no API key"
        