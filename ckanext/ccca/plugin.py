import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckan.model as model
import ckan.logic as logic
get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
from pylons import g, c, config, response, request
from ckanext.ccca import helpers
import ckan.plugins.toolkit as tk


import logging

log = logging.getLogger(__name__)

class CccaPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer, inherit=False)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    #plugins.implements(plugins.IAuthFunctions) # Functions moved to iauth
    #plugins.implements(plugins.IMapper)


    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ccca')
        toolkit.add_resource('public/base/vendor', 'vendor')

    # ITemplateHelpers
    # Anja 28.11.16
    def get_helpers(self):
        return {
            'ccca_count_resources': helpers.ccca_count_resources,
            'ccca_get_number_organizations': helpers.ccca_get_number_organizations,
            'ccca_get_random_organization': helpers.ccca_get_random_organization,
            'ccca_get_number_groups': helpers.ccca_get_number_groups,
            'ccca_get_random_group': helpers.ccca_get_random_group,
            'ccca_check_member': helpers.ccca_check_member,
            'ccca_get_user_dataset':helpers.ccca_get_user_dataset,
            'ccca_get_orgs': helpers.ccca_get_orgs,
            'ccca_get_orgs_for_user': helpers.ccca_get_orgs_for_user,
            'ccca_organizations_available_with_private': helpers.ccca_organizations_available_with_private,
            'ccca_check_news': helpers.ccca_check_news,
            'ccca_get_user_name': helpers.ccca_get_user_name,
            'ccca_get_news': helpers.ccca_get_news,
            'ccca_group_show': helpers.ccca_group_show,
            'ccca_group_list': helpers.ccca_group_list,
            'ccca_filter_groupby': helpers.ccca_filter_groupby,
            'ccca_sort_groups_dropdown': helpers.ccca_sort_groups_dropdown,
            'ccca_sort_groups_list': helpers.ccca_sort_groups_list,
            'ccca_get_groups_with_dataset': helpers.ccca_get_groups_with_dataset
            }

    # IRoutes
    def before_map(self, map):
        # About pages
        map.connect('about_news', '/about/news_archive',
                    controller='ckanext.ccca.controllers.about:AboutController',
                    action='news_archive')
        map.connect('about_usage', '/about/usage',
                    controller='ckanext.ccca.controllers.about:AboutController',
                    action='usage')
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
        map.connect('about_data_policy', '/about/data_policy',
                    controller='ckanext.ccca.controllers.about:AboutController',
                    action='data_policy')

        # Mail Request user registration
        map.connect('/user/register',
                    controller='ckanext.ccca.controllers.user:UserController',
                    action='register')
        map.connect('disclaimer', '/disclaimer',
                    controller='ckanext.ccca.controllers.disclaimer:DisclaimerController',
                    action='disclaimer')

        # Sort Organizations
        map.connect('organization', '/organization',
                    controller='ckanext.ccca.controllers.organizations:CCCAOrganizationController',
                    action='index')

        # Groups
        map.connect('group', '/group',
                    controller='ckanext.ccca.controllers.group:CCCAGroupController',
                    action='index')

        # List Members of own organization
        map.connect('organization_list_members', '/organization/members_list/{id}',
                    controller='ckanext.ccca.controllers.organizations:CCCAOrganizationController',
                    action='members_list', ckan_icon='group')

    
        return map

    def after_map(self, map):
        #log.fatal("==================================> %s" % map)
        return map

    #IAuthFunctions
    #def get_auth_functions(self):
        #return {'package_update': package_update}

    """
    #IMapper
    def after_update(mapper, connection, instance):
        print ("After update")

    def before_update(mapper, connection, instance):
        print ("Before update")

    def before_insert(mapper, connection, instance):
        print ("Before insert")
    """
