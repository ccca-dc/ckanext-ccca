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
#import ckanext.ccca.helpers as helpers # Anja 28.11.16
from pylons import g, c, config, response, request
""" Anja 28.11.2016 """
from ckanext.ccca import helpers

import logging

log = logging.getLogger(__name__)

class CccaPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer, inherit=False)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)


    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ccca')

    # ITemplateHelpers
    # Anja 28.11.16
    def get_helpers(self):
        return {
            'ccca_count_resources': helpers.ccca_count_resources,
            'ccca_get_number_organizations': helpers.ccca_get_number_organizations,
            'ccca_get_random_organization': helpers.ccca_get_random_organization,
            'ccca_get_number_groups': helpers.ccca_get_number_groups,
            'ccca_get_random_group': helpers.ccca_get_random_group
            }


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

        # Mail Request user registration
        '''
        map.connect('/user/mail_request',
                    controller='ckanext.ccca.controllers.user:UserController',
                    action='mail_request')
        '''
        map.connect('disclaimer', '/disclaimer',
                    controller='ckanext.ccca.controllers.disclaimer:DisclaimerController',
                    action='disclaimer')

        return map

    def after_map(self, map):
        #log.fatal("==================================> %s" % map)
        return map
