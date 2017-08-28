import re
import datetime
import pytz

from pylons import config
from pylons.i18n import gettext

import ckan.logic as logic
get_action = logic.get_action


""" Anja 29.9.2016 """
import  ckan.plugins.toolkit as tk
context = tk.c
import ckan.lib.base as base
Base_c = base.c
from pylons import c
import logging
log = logging.getLogger(__name__)
""" Anja 29.9.2016 """
""" Anja 23.11.2016 """
import random
""" Anja 9.6.2017 """
import ckan.lib.helpers as h


def ccca_organizations_available_with_private():
    '''Return a list of organizations including (private) package_count
    '''

    context = {'user': c.user}
    data_dict = {'permission': 'read'}
    # delivers only public packages (count)
    org_list = logic.get_action('organization_list_for_user')(context, data_dict)

    for org in org_list:
        if 'name' in org:
            data_dict['id'] = org['name']
            corr_org = logic.get_action('organization_show')(context, data_dict)
            if 'package_count' in corr_org:
                org['package_count'] = corr_org['package_count']

    return org_list


def ccca_get_org_and_role(user):

    if  user['name'] != None:
        user_name = user['name']
    else:
        return None

    user_orgs = ccca_get_orgs_for_user(user_name)
    #print "****************** ccca_get_org_and_role"
    #print user_orgs
    if  user_orgs != None:
        for org in user_orgs:
            #print org
            org_users = tk.get_action('organization_show')({},{'id':org['name'], 'include_users':True})
            for u in org_users['users']:
                if u['name'] == user_name:
                    if u['capacity'] == 'admin':
                        org['role'] = 'Admin'
                    elif u['capacity'] == 'editor':
                        org['role'] = 'Editor'
                    elif u['capacity'] == 'member':
                        org['role'] = 'Member'
                    else:
                        org['role'] = u['capacity']

                    break
    #print user_orgs
    return user_orgs

def ccca_get_orgs_for_user (user_name):
    """ Delivers list of organizations for a user"""

    try:
        all_orgs = tk.get_action('organization_list')({},{'all_fields':True, 'include_users':True})
        all_users = tk.get_action('user_list')({},{})
    except:
        return None

    # make a simple list of users in every org
    user_org_list = {}
    for org in all_orgs:
        u_list = []
        users = org['users']
        for us in users:
            u_list.append(us['name'])
        user_org_list[org['name']] = u_list

    # make the return dict
    orgs_for_user = []
    for org in all_orgs:
        # check of current user (u) in list
        if user_name in user_org_list[org['name']] and user_org_list[org['name']] != None:

            org_sum = {}
            org_sum['name'] = org['name']
            org_sum['display_name'] = org['display_name']
            org_sum['url'] = h.url_for(controller='organization', action='read', id=org['name'])
            orgs_for_user.append(org_sum)


    return orgs_for_user

def ccca_get_orgs ():
    """ Delivers an user-dependent list of organizations and users"""

    all_orgs = tk.get_action('organization_list')({},{'all_fields':True, 'include_users':True})
    all_users = tk.get_action('user_list')({},{})

    # make a simple list of users in every org
    user_org_list = {}
    for org in all_orgs:
        u_list = []
        users = org['users']
        for us in users:
            u_list.append(us['name'])
        user_org_list[org['name']] = u_list

    # make the return dict
    user_orgs = {}
    for u in all_users:

        orgs_for_user = []
        for org in all_orgs:
            # check of current user (u) in list
            if u['name'] in user_org_list[org['name']] and user_org_list[org['name']] != None:

                org_sum = {}
                org_sum['name'] = org['name']
                org_sum['display_name'] = org['display_name']
                org_sum['url'] = h.url_for(controller='organization', action='read', id=org['name'])
                orgs_for_user.append(org_sum)

                #just one
                #user_orgs[u['name']] = org_sum
                # one org is enough
                #break

        user_orgs[u['name']] =  orgs_for_user
        #print user_orgs[u['name']]
    #print "USer_org_list"
    #print user_orgs
    return user_orgs



""" Anja 9.6.2017"""
def ccca_get_user_dataset(user_id):

    #print user_id
    if user_id == None or user_id == '':
        return None

    try:
        all_sets = tk.get_action('user_show')({}, {"id": user_id, "include_datasets": True})
    except:
        return None

    try:
        #for x in all_sets['datasets']:
            #print x['id']
        one_set = all_sets['datasets'][0]
        #print one_set['id']
        return one_set
    except:
        return None

def ccca_check_member (context, org_id):
    user_groups = h.organizations_available(permission="read")
    for g in user_groups:
        if org_id == g['id']:
            return True

    return False
""" Anja 9.6.2017 End """

""" Anja 23.11.2016 """
def ccca_count_resources():
    """ Anja 21.11.2016
    log.debug("ccca_count_resources ******************")
    Attention: Hard limit of 1000 Datasets - parameter obviously "rows" not "limit" ...
    """

    all_sets = tk.get_action('package_search')({}, {"rows": 1000})
    all_count = all_sets['count']

    if all_count > 999:
        all_count = 999

    current_set = 0
    all_resource_count = 0
    while current_set < c.package_count:
        all_sets['results'][current_set]['title']
        all_resource_count += all_sets['results'][current_set]['num_resources']
        current_set += 1
    return all_resource_count


def ccca_get_number_organizations():
    # log.debug("ccca_get_number_organization ******************")
    '''
    Code adapted from ckan: get_featured_organizations(count=1):
    '''
    config_orgs = config.get('ckan.featured_orgs', '').split()
    count = len(config_orgs)
    # log.debug(count)
    '''
    orgs = h.featured_group_org(get_action='organization_show',
                              list_action='organization_list',
                              count=count,
                              items=config_orgs)
    log.debug(orgs)
    '''
    return count

def ccca_get_random_organization():
    # log.debug("ccca_random_organization ******************")
    '''
    Code adapted from ckan: get_featured_organizations(count=1):
    '''
    config_orgs = config.get('ckan.featured_orgs', '').split()

    if not config_orgs:
        return ""
    # log.debug(config_orgs)

    count = len(config_orgs)
    rand_org = random.choice(config_orgs)

    # log.debug(count)
    # log.debug(rand_org)

    '''
    orgs = h.featured_group_org(get_action='organization_show',
                              list_action='organization_list',
                              count=count,
                              items=config_orgs)
    log.debug(orgs)
    '''
    return rand_org

def ccca_get_number_groups():
    # log.debug("ccca_get_number_groups ******************")

    '''
    Code adapted from ckan: get_featured_goups(count=1):
    '''
    config_groups = config.get('ckan.featured_groups', '').split()
    count = len(config_groups)
    # log.debug(count)

    return count

def ccca_get_random_group():
    # log.debug("ccca_random_group ******************")
    '''
    Code adapted from ckan: get_featured_groups(count=1):

    '''
    config_groups = config.get('ckan.featured_groups', '').split()
    # log.debug(config_groups)

    if not config_groups:
        return ""
    rand_group = random.choice(config_groups)
    # log.debug(rand_group)

    return rand_group
