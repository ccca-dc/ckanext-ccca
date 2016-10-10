import ckan.logic as logic
import ckan.authz as authz
from ckan.lib.base import _
from ckan.logic.auth import (get_resource_object)
import logging
log = logging.getLogger(__name__)

'''
Created on Mar 25, 2016
'''

def resource_show_ext(context, data_dict):
    model = context['model']
    user = context.get('user')
    userobj = context.get('auth_user_obj')
    resource = get_resource_object(context, data_dict)
    
    # check authentication against package
    pkg = model.Package.get(resource.package_id)
    if not pkg:
        raise logic.NotFound(_('No package found for this resource, cannot check auth.'))

    pkg_dict = {'id': pkg.id}
    authorized = authz.is_authorized('package_show', context, pkg_dict).get('success')
    
    if not authorized:
        return {'success': False, 'msg': _('User %s not authorized to read resource %s') % (user, resource.id)}
    
    if 'res_access' in data_dict:
        res_access = data_dict['res_access']
    else:
        res_access = True
        
    if userobj == None: 
        mydataset = False
    else:
        mydataset = (userobj.id == pkg.creator_user_id)
        
    if not (mydataset or res_access):
        return {'success': False, 'msg': _('User %s not authorized to read resource (access not public) %s') % (user, resource.id)}
    
    return {'success': True}
