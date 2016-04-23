import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.base as base

from ckanext.ccca.common import c, model, logic
get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
import logic.action as action

import requests

from pylons import g, c, config, response, request
from jinja2 import Environment, FileSystemLoader
from os import listdir
from os.path import isfile, join, expanduser

import logging
import json

log = logging.getLogger(__name__)

class DownloadController(base.BaseController):    
    """ Download of resources
    Extended by check if resources are set to publicly available.
    """    
    def resource_download_ext(self, id, resource_id, filename=None):
        """
        Provides a direct download by either redirecting the user to the url 
        stored or downloading an uploaded file directly.
        This is an extension of the resource_download action. It checks an 
        additional flag of the dataset ('res_access') determining if the 
        resources should be publicly accessible.
        """
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}
        data = base.request.params
        res_access = c.package.extras.res_access
        mydataset = (c.userobj.id == c.package.creator_user_id)

        if not (res_access or mydataset):
            abort(404, _('The resource is not accessible.'))
        
        try:
            rsc = get_action('resource_show')(context, {'id': resource_id})
            get_action('package_show')(context, {'id': id})
        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % id)

        if rsc.get('url_type') == 'upload':
            upload = uploader.ResourceUpload(rsc)
            filepath = upload.get_path(rsc['id'])
            fileapp = paste.fileapp.FileApp(filepath)
            try:
                status, headers, app_iter = request.call_application(fileapp)
            except OSError:
                abort(404, _('Resource data not found'))
            response.headers.update(dict(headers))
            content_type, content_enc = mimetypes.guess_type(
                rsc.get('url', ''))
            if content_type:
                response.headers['Content-Type'] = content_type
            response.status = status
            return app_iter
        elif not 'url' in rsc:
            abort(404, _('No download is available'))
        redirect(rsc['url'])