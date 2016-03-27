#import ckan.plugins as p
import ckan.logic as logic
import ckan.authz as authz
from ckan.lib.base import _
from ckan.logic.auth import (get_package_object, get_group_object,
                            get_resource_object, get_related_object)
import logging
log = logging.getLogger(__name__)

'''
Created on Mar 25, 2016

@author: ck
'''

def resource_show_ext(context, data_dict):
    model = context['model']
    user = context.get('user')
    resource = get_resource_object(context, data_dict)
    package_id = resource.package_id
    #log.debug('extras: ' + context['extras'])
    
    # check authentication against package
    pkg = model.Package.get(resource.package_id)
    if not pkg:
        raise logic.NotFound(_('No package found for this resource, cannot check auth.'))

    pkg_dict = {'id': pkg.id}
    authorized = authz.is_authorized('package_show', context, pkg_dict).get('success')

    if not authorized:
        return {'success': False, 'msg': _('User %s not authorized to read resource %s') % (user, resource.id)}
    else:
        return {'success': True}