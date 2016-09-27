import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
#import ckan.lib.base as base

import ckan.model as model
import ckan.logic as logic
get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
#import ckanext.ccca.logic.action.metadata as action
#import helpers as h
import ckanext.ccca.helpers as helpers
import ckanext.ccca.logic.auth as auth
import ckanext.ccca.logic.action.metadata as metadata
import ckanext.ccca.logic.action.get as get
from ckanext.ccca.lib import create_unique_identifier
import requests

from pylons import g, c, config, response, request
from jinja2 import Environment, FileSystemLoader
from os import listdir
from os.path import isfile, join, expanduser

import logging

log = logging.getLogger(__name__)

class CccaPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer, inherit=False)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ccca')

    def before_map(self, map):
        # About pages
        map.connect('about_citation', '/about/citation',
                    controller='ckanext.ccca.controllers.about:AboutController',
                    action='citation')
        map.connect('about_download', '/about/download',
                    controller='ckanext.ccca.controllers.about:AboutController',
                    action='download')
        map.connect('about_credits', '/about/credits',
                    controller='ckanext.ccca.controllers.about:AboutController',
                    action='credits')
        map.connect('about_prototype', '/about/prototype',
                    controller='ckanext.ccca.controllers.about:AboutController',
                    action='prototype')

        map.connect('get_fields_iso', '/metadata/fields_iso',
                    controller='ckanext.ccca.controllers.view:ViewController',
                    action='get_fields_iso')
        map.connect('show_iso_19139', '/metadata/iso-19139/{id}.xml',
                    controller='ckanext.ccca.controllers.view:ViewController',
                    action='show_iso_19139')

        map.connect('resource_download', '/dataset/{id}/resource/{resource_id}/download/{filename}', controller='ckanext.ccca.controllers.package_override:PackageContributeOverride', action='resource_download')
        #map.connect('resource_views', '/dataset/{id}/resource/{resource_id}/view/{view_id}', controller='ckanext.ccca.controllers.package_override:PackageContributeOverride', action='resource_datapreview')


        # map.connect('dataset_new_metadata', '/dataset/new_metadata/{id}',
        #             controller='ckanext.ccca.controllers.package_override:PackageContributeOverride',
        #             action='new_metadata')
        # map.connect('dataset_metadata', '/dataset/metadata/{id}',
        #             controller='ckanext.ccca.controllers.package_override:PackageContributeOverride',
        #             action='metadata',  ckan_icon='edit')

        map.connect('export_metadata', '/export_metadata',
                    controller='ckanext.ccca.controllers.export:ExportController',
                    action='export_metadata_xml')

        # Mail Request user registration
        map.connect('/user/mail_request',
                    controller='ckanext.ccca.controllers.user:UserController',
                    action='mail_request')

        return map

    def after_map(self, map):
        #log.fatal("==================================> %s" % map)
        return map
