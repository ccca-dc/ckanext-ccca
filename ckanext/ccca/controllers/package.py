import cgi
import paste.fileapp
import mimetypes
import json
import logging
import os
import ckan.model as model
import ckan.logic as logic
import pylons.config as config
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.plugins as p
from ckan.common import request, c, g, response
import ckan.lib.uploader as uploader
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.lib.dictization as dictization
from pylons.i18n.translation import _, ungettext
import ckan.lib.i18n as i18n
from ckan.controllers.package import PackageController
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.authz as authz

from urlparse import urlparse
from posixpath import basename, dirname

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params

log = logging.getLogger(__name__)

class PackageContributeOverride(p.SingletonPlugin, PackageController):
    ''' Package Controller
    '''
    # Restrict download from resource to registered user
    def resource_download(self, id, resource_id, filename=None):
        """
        Provides a direct download by either redirecting the user to the url
        stored or downloading an uploaded file directly.
        """
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}

        try:
            rsc = get_action('resource_show')(context, {'id': resource_id})
            get_action('package_show')(context, {'id': id})
        except (NotFound, NotAuthorized):
            abort(404, _('Resource not found'))

        if authz.auth_is_anon_user(context):
            abort(401, _('Unauthorized to read resource %s') % id)
        else:
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

    def resource_datapreview(self, id, resource_id):
        '''
        Embedded page for a resource data-preview.

        Depending on the type, different previews are loaded.  This could be an
        img tag where the image is loaded directly or an iframe that embeds a
        webpage, or a recline preview.
        '''
        context = {
            'model': model,
            'session': model.Session,
            'user': c.user,
            'auth_user_obj': c.userobj
        }

        if authz.auth_is_anon_user(context):
            abort(401, _('Unauthorized to read resource %s') % id)
        else:
            try:
                c.resource = get_action('resource_show')(context,
                                                        {'id': resource_id})
                c.package = get_action('package_show')(context, {'id': id})

                data_dict = {'resource': c.resource, 'package': c.package}

                preview_plugin = datapreview.get_preview_plugin(data_dict)

                if preview_plugin is None:
                    abort(409, _('No preview has been defined.'))

                preview_plugin.setup_template_variables(context, data_dict)
                c.resource_json = json.dumps(c.resource)
                dataset_type = c.package['type'] or 'dataset'
            except (NotFound, NotAuthorized):
                abort(404, _('Resource not found'))
            else:
                return render(preview_plugin.preview_template(context, data_dict),
                            extra_vars={'dataset_type': dataset_type})
