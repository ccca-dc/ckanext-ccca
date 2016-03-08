import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.base as base
import requests

from pylons import g, c, config
from jinja2 import Environment, FileSystemLoader
from os import listdir
from os.path import isfile, join, expanduser

import logging
import json

log = logging.getLogger(__name__)

class CccaPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IDatasetForm)
    
    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ccca')
        
    def before_map(self, map):
        map.connect('sftp_filelist', '/sftp_filelist', controller='ckanext.ccca.plugin:UploadController', action='show_filelist')
        map.connect('sftp_upload', '/sftp_upload', controller='ckanext.ccca.plugin:UploadController', action='upload_file')
        return map
    
    def after_map(self, map):
        #log.fatal("==================================> %s" % map)
        return map
    
    def create_package_schema(self):
        schema = super(CccaPlugin, self).create_package_schema()
        schema.update({
            'res_access': [toolkit.get_validator('boolean_validator'),
                            toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def update_package_schema(self):
        schema = super(CccaPlugin, self).update_package_schema()
        schema.update({
            'res_access': [toolkit.get_validator('boolean_validator'),
                            toolkit.get_converter('convert_to_extras')]
        })
        return schema
    
    def show_package_schema(self):
        schema = super(CccaPlugin, self).show_package_schema()
        schema.update({
            'res_access': [toolkit.get_converter('convert_from_extras'),
                           toolkit.get_validator('boolean_validator')]
        })
        return schema
    
    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []
    
class UploadController(base.BaseController):
    
    def show_filelist(self):
        user = c.userobj
        data = base.request.params
        log.debug('username: '+user.name)
        if 'apikey' in data and data['apikey']==user.apikey:
            mypath = '/Users/ck/ccca-import/'
            onlyfiles = [f for f in listdir(mypath) if (isfile(join(mypath, f)) and not f.startswith('.'))]
            return json.dumps(onlyfiles)
        else:
             return "no API key"
         
    def upload_file(self):
        reqData = base.request.params
        ckan_url = config.get('ckan.site_url', '//localhost:5000')
        response = requests.post(ckan_url+'/api/action/resource_create',
              data={'package_id': reqData['package_id'],
                    'url': reqData['url'],
                    #'name': reqData['name']
                    },
              headers={"X-CKAN-API-Key": reqData['apikey']},
              files=[('upload', file(reqData['url']))])
        return response
        
        