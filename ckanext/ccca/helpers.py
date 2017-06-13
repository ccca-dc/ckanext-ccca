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



""" Anja 9.6.2017"""
def ccca_get_user_dataset(user_id):
    all_sets = tk.get_action('user_show')({}, {"id": user_id, "include_datasets": True})
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
    #print org_id
    #print user_groups
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
