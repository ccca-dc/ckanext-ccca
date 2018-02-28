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
# Anja 27.9.17
from ckanext.filtersearch import helpers as hf
from ckanext.scheming import helpers as hs

from pylons import config

import json

import ckan.model as model

# Store group_list and group_type_list globally: Anja, 28.2.18
# to get them only once
group_list = []
group_type_list =[]


def _get_group_index_list (name,list_of_items):
#for the list of groups as prepared for group list
    for i, x in enumerate(list_of_items):
        if x['name'] == name:
            return i
    return -1

def _get_group_index_dropdown (name,list_of_items):
#for the list of groups as prepared for dropdown
    for i, x in enumerate(list_of_items):
        if x[1] == name:
            return i
    return -1

def _get_group(id):
    global group_list
    if not group_list:
        group_list = logic.get_action('group_list')({}, {'all_fields':True, 'include_extras':True})

    if not group_list:
        return None
    result = (item for item in group_list if item['id'] == id).next()

    return result

def _get_group_type_label(name):
    global group_type_list
    label = ''
    if not group_type_list:
        schema = hs.scheming_group_schemas()
        group_info = schema['group']
        field_list = group_info['fields']
        for x in field_list:
            if x['field_name'] == 'type_of_group':
                group_type_list = x['choices']

    if not group_type_list:
        return ''
    label = ''
    for x in group_type_list:
        if x['value']==name:
            label = x['label']
            break
    return label

def ccca_sort_groups_dropdown(pkg_groups):

    #reverse Order because of insertion method below
    rev_groups = sorted(pkg_groups, key=lambda tup: tup[1], reverse=True)

    sorted_groups = []
    for x in rev_groups:
        group = _get_group(x[0])
        group_type = ''
        group_type_label = ''
        if 'type_of_group' in group:
            group_type = group['type_of_group']
        if group_type:
            group_type_label = _get_group_type_label(group_type)
        else:
            group_type = 'other'
            group_type_label = 'Other'
        if not sorted_groups or _get_group_index_dropdown(group_type_label,sorted_groups) <0:
            f = []
            f.append('-') # Empty id for group types
            f.append( group_type_label)
            f.append(False)
            x.append(True)
            sorted_groups.append(f)
            sorted_groups.append(x)
        else:
            index=_get_group_index_dropdown(group_type_label,sorted_groups)
            if  index >= 0:
                x.append(True)
                sorted_groups.insert(index+1, x)

    for g in sorted_groups:
        if not g[2]:
            g[1] = g[1] + ': '

    #print sorted_groups
    return sorted_groups

def ccca_sort_groups_list(pkg_groups):
# sorting for the group_list
    #reverse Order because of insertion method below
    rev_groups = sorted(pkg_groups,  key=lambda k: k['name'], reverse=True)
    sorted_groups = []
    for x in rev_groups:
        group = _get_group(x['id'])
        group_type = ''
        group_type_label = ''
        if 'type_of_group' in group:
            group_type = group['type_of_group']
        if group_type:
            group_type_label = _get_group_type_label(group_type)
        else:
            group_type = 'other'
            group_type_label = 'Other'
        if not sorted_groups or _get_group_index_list(group_type,sorted_groups) <0:
            f = {}
            f['description'] = group['description']
            f['name'] = group_type
            f['display_name'] = group_type_label + ': '
            f['title'] = group_type_label + ': '
            f['is_type'] = True
            sorted_groups.append(f)
            x['is_type'] = False
            sorted_groups.append(x)
        else:
            index=_get_group_index_list(group_type,sorted_groups)
            if  index >= 0:
                x['is_type'] = False
                sorted_groups.insert(index+1, x)

    return sorted_groups

def ccca_get_news ():
    news_id = ccca_check_news();

    if not news_id:
        return None

    try:
        news_pkg = tk.get_action('package_show')({}, {'id': news_id, 'include_datasets':True})

        news_res_list = news_pkg['resources']

        newest_res = {}
        for x in news_res_list:
            nd = x['created']
            newest_res = x
            if x['created'] > nd:
                nd = x['created']
                newest_res = x

    except:
        return None

    #print json.dumps(news_res, indent=4)
    return newest_res

def ccca_check_news():
    if 'ckanext.ccca.news_id' in config:
        news_id =  config.get ('ckanext.ccca.news_id')
        try:
            news_pkg = tk.get_action('package_show')({}, {'id': news_id})
            if news_pkg['private']:
                return ""
        except:
            return ""
        return news_id
    else:
        return ""

def ccca_get_user_name(user_id):

    try:
        uname = tk.get_action('user_show')({}, {'id': user_id })

    except:
        return " "

    if 'display_name' in uname:
        return uname['display_name']
    else:
        return " "

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


def ccca_group_show(group_id):
    return tk.get_action('group_show')({}, {"id": group_id})


def ccca_group_list(type_of_group=None):
    context = {'model': model,
               'user': c.user}

    groups = tk.get_action('group_list')(context, {'all_fields': True, 'include_dataset_count': True, 'include_extras': True})

    if type_of_group is None:
        return groups

    return [group for group in groups if group.get('type_of_group', None) == type_of_group]


def ccca_group_list(type_of_group=None):
    context = {'model': model,
               'user': c.user}

    groups = tk.get_action('group_list')(context, {'all_fields': True, 'include_dataset_count': True, 'include_extras': True})

    if type_of_group is None:
        return groups

    return [group for group in groups if group.get('type_of_group', None) == type_of_group]

def ccca_filter_groupby(tuple_groupby, filter_string):
    filtered = filter(lambda x: filter_string in x[0], tuple_groupby)
    try:
        return filtered[0][1]
    except:
        return filtered
