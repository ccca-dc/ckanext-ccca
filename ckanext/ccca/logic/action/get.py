'''API functions for searching for and getting data from CKAN.'''

import uuid
import logging
import json
import datetime
import socket

from pylons import config
import sqlalchemy
from paste.deploy.converters import asbool

import ckan.lib.dictization
import ckan.logic as logic
import ckan.logic.action
import ckan.logic.schema
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.navl.dictization_functions
import ckan.model as model
import ckan.model.misc as misc
import ckan.plugins as plugins
import ckan.lib.search as search
import ckan.lib.plugins as lib_plugins
import ckan.lib.activity_streams as activity_streams
import ckan.lib.datapreview as datapreview
import ckan.authz as authz
import ckan.lib.lazyjson as lazyjson

from ckan.common import _

log = logging.getLogger('ckan.logic')

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = ckan.lib.navl.dictization_functions.validate
_table_dictize = ckan.lib.dictization.table_dictize
_check_access = logic.check_access
NotFound = logic.NotFound
ValidationError = logic.ValidationError
_get_or_bust = logic.get_or_bust

_select = sqlalchemy.sql.select
_aliased = sqlalchemy.orm.aliased
_or_ = sqlalchemy.or_
_and_ = sqlalchemy.and_
_func = sqlalchemy.func
_desc = sqlalchemy.desc
_case = sqlalchemy.case
_text = sqlalchemy.text



def resource_show(context, data_dict):
    '''Return the metadata of a resource.

    :param id: the id of the resource
    :type id: string
    :param include_tracking: add tracking information to dataset and
        resources (default: False)
    :type include_tracking: bool

    :rtype: dictionary

    '''
    model = context['model']
    id = _get_or_bust(data_dict, 'id')

    resource = model.Resource.get(id)
    resource_context = dict(context, resource=resource)

    if not resource:
        raise NotFound

    pkg = model.Package.get(resource.package_id)
    _check_access('resource_show', resource_context, data_dict)

    pkg_dict = logic.get_action('package_show')(
        dict(context),
        {'id': resource.package.id,
        'include_tracking': asbool(data_dict.get('include_tracking', False))})

    for resource_dict in pkg_dict['resources']:
        if resource_dict['id'] == id:
            break
    else:
        log.error('Could not find resource ' + id)
        raise NotFound(_('Resource was not found.'))

    return resource_dict