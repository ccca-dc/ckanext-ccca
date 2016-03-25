import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
#import ckan.lib.base as base

from ckanext.metadata.common import c, model, logic
get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
import logic.action as action
import helpers as h

import requests

from pylons import g, c, config, response, request
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
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers)
    #plugins.implements(p.IAuthFunctions)
    
    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ccca')
        
    def before_map(self, map):
                
        map.connect('sftp_filelist', '/sftp_filelist', controller='ckanext.ccca.controllers.upload:UploadController', action='show_filelist')
        map.connect('sftp_upload', '/sftp_upload', controller='ckanext.ccca.controllers.upload:UploadController', action='upload_file')
        #map.connect('/dataset/{id}/resource/{resource_id}/download', controller='ckanext.ccca.plugin:DownloadController', action='resource_download_ext')
        #map.connect('/dataset/{id}/resource/{resource_id}/download/{filename}', controller='ckanext.ccca.plugin:DownloadController', action='resource_download_ext')
        map.connect('get_fields_iso', '/metadata/fields_iso', controller='ckanext.ccca.controllers.view:ViewController', action='get_fields_iso')
        map.connect('show_iso_19139', '/metadata/iso-19139/{id}.xml', controller='ckanext.ccca.controllers.view:ViewController', action='show_iso_19139')
        
        map.connect('pkg_new', '/dataset/new_resource/{id}', controller='ckanext.ccca.controllers.package_override:PackageContributeOverride', action='new_resource')
        map.connect('custom_resource_edit', '/dataset/{id}/resource_edit/{resource_id}', controller='ckanext.ccca.controllers.package_override:PackageContributeOverride', action='resource_edit')
        map.connect('new_metadata', '/dataset/new_metadata/{id}', controller='ckanext.ccca.controllers.package_override:PackageContributeOverride', action='new_metadata',  ckan_icon='edit')
        return map
    
    def after_map(self, map):
        #log.fatal("==================================> %s" % map)
        return map
    
        # IActions
    def get_actions(self):
        return {
           'show_iso_19139': action.iso_19139
        }
       
    def _modify_package_schema(self, schema):
        schema.update({
            'res_access': [toolkit.get_validator('boolean_validator'),
                toolkit.get_converter('convert_to_extras')]
        })
        schema.update({
            'custom_text': [toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')]
        })
        return schema
     
    def create_package_schema(self):
        schema = super(CccaPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(CccaPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema
    
    def show_package_schema(self):
        schema = super(CccaPlugin, self).show_package_schema()
        schema.update({
            'res_access': [toolkit.get_converter('convert_from_extras'),
                           toolkit.get_validator('boolean_validator')]
        })
        schema.update({
            'custom_text': [toolkit.get_converter('convert_from_extras'),
                           toolkit.get_validator('ignore:missing')]
        })
        return schema
    
    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return False

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []
    
        # ITemplateHelpers
    def get_helpers(self):
        return {
            'md_get_vanilla_ckan_version': h.md_get_vanilla_ckan_version,
            'md_package_extras_processor': h.md_package_extras_processor,
            'md_resource_extras_processer': h.md_resource_extras_processer,
            'usgin_check_package_for_content_model': h.usgin_check_package_for_content_model,
            #'geothermal_prospector_url': metahelper.get_prospector_url,
        }