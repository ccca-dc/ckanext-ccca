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
import ckan.plugins.toolkit as tk

import logging

log = logging.getLogger(__name__)

#Anja 13.6.2017
#global last_session
#global last_access
#last_session = ""
#last_access = False

def package_update(context, data_dict=None):
    #print "Hello"
    #print context

    s = context['session'] # always exists

    try:
        my_package = context['package'] # not on resources or page reload
        owner_org =  my_package.owner_org
        #print owner_org
    except: # per resource: session; and on page reload: only session
        try:
            if s == last_session:
                if last_access:
                    return {'success': True}
                else:
                    return {'success': False, 'msg': 'You are only allowed to edit your own datasets'}
            else:
                #print "internal problem"
                return {'success': False, 'msg': 'Access denied'} # We should not run into this path :-)
        except:
            #print "some internal problem"
            return {'success': False, 'msg': 'Sorry, access denied'} # We should not run into this path :-)

    # SAVE  follwing resources that pass through this function and for page relaods
    global last_session
    last_session = context['session']
    #print last_session

    #check if ADMIN
    user_mail = context['auth_user_obj']
    org_list = tk.get_action('organization_list_for_user')({}, {"id": user_mail.id, "permission": "member_create"})
    #print "Hello2"
    #print org_list
    for x in org_list:
        #print x.values()
        if owner_org in x.values():
                #print "success"
                #print last_session
                global last_access
                last_access = True
                return {'success': True}

    # Editors only allowed to edit own packages
    if user_mail.email == my_package.maintainer_email or user_mail.email == my_package.author_email:
        global last_access
        last_access = True
        return {'success': True}
    else:
        global last_access
        last_access = False
        return {'success': False, 'msg': 'You are only allowed to edit your own datasets'}


# Geht nicht - ist schon in resourceversions ...
#def package_delete(context, data_dict=None):
#    return {'success': False, 'msg': 'Not allwoed to delete}

class CccaPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer, inherit=False)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IAuthFunctions)
    #plugins.implements(plugins.IMapper)


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
            'ccca_get_random_group': helpers.ccca_get_random_group,
            'ccca_check_member': helpers.ccca_check_member,
            'ccca_get_user_dataset':helpers.ccca_get_user_dataset
            }

    # IRoutes
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

        # List Members of own organization
        map.connect('organization_list_members', '/organization/members_list/{id}',
                    controller='ckanext.ccca.controllers.organizations:CCCAOrganizationController',
                    action='members_list', ckan_icon='group')
        return map

    def after_map(self, map):
        #log.fatal("==================================> %s" % map)
        return map

    #IAuthFunctions
    def get_auth_functions(self):
        return {'package_update': package_update}

    """
    #IMapper
    def after_update(mapper, connection, instance):
        print ("After update")

    def before_update(mapper, connection, instance):
        print ("Before update")

    def before_insert(mapper, connection, instance):
        print ("Before insert")
    """
