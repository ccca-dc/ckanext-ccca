import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.base as base
#import ckan.lib.render as render
#import ckan.model as model
#from ckan.controllers.package import PackageController

from ckanext.metadata.common import c, model, logic
get_action = logic.get_action
#import ckan.logic as logic
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
import logic.action as action

import requests

from pylons import g, c, config, response, request
from jinja2 import Environment, FileSystemLoader
from os import listdir
#from os.path import isfile, join, expanduser

import logging
import json

log = logging.getLogger(__name__)

class CccaPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IActions)
    
    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'ccca')
        
    def before_map(self, map):
        map.connect('sftp_filelist', '/sftp_filelist', controller='ckanext.ccca.plugin:UploadController', action='show_filelist')
        map.connect('sftp_upload', '/sftp_upload', controller='ckanext.ccca.plugin:UploadController', action='upload_file')
        #map.connect('/dataset/{id}/resource/{resource_id}/download', controller='ckanext.ccca.plugin:DownloadController', action='resource_download_ext')
        #map.connect('/dataset/{id}/resource/{resource_id}/download/{filename}', controller='ckanext.ccca.plugin:DownloadController', action='resource_download_ext')
        map.connect('/dataset/{id}/gmd', controller='ckanext.ccca.controllers.view:ViewController', action='show_iso_19139')
        #map.connect('metadata_iso_19139', '/metadata/iso-19139/{id}.xml', controller='ckanext.ccca.controllers.view:ViewController', action='show_iso_19139')
        return map
    
    def after_map(self, map):
        #log.fatal("==================================> %s" % map)
        return map
    
        # IActions
    def get_actions(self):
        return {
            'iso_19139': action.iso_19139
        }
        
    def create_package_schema(self):
        schema = super(CccaPlugin, self).create_package_schema()
        schema.update({
            'res_access': [toolkit.get_validator('boolean_validator'),
                            toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def update_package_schema(self):
        schema = super(CccaPlugin, self).update_package_schema()
        schema.update({
            'res_access': [toolkit.get_validator('boolean_validator'),
                            toolkit.get_converter('convert_to_extras')]
        })
        return schema
    
    def show_package_schema(self):
        schema = super(CccaPlugin, self).show_package_schema()
        schema.update({
            'res_access': [toolkit.get_converter('convert_from_extras'),
                           toolkit.get_validator('boolean_validator')]
        })
        return schema
    
    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return False

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []
    
class UploadController(base.BaseController):
    
    def show_filelist(self):
        user = c.userobj
        data = base.request.params
        log.debug('username: '+user.name)
        if 'apikey' in data and data['apikey']==user.apikey:
            mypath = '/Users/ck/ccca-import/'
            onlyfiles = [f for f in listdir(mypath) if (isfile(join(mypath, f)) and not f.startswith('.'))]
            return json.dumps(onlyfiles)
        else:
             return "no API key"
         
    def upload_file(self):
        reqData = base.request.params
        ckan_url = config.get('ckan.site_url', '//localhost:5000')
        response = requests.post(ckan_url+'/api/action/resource_create',
              data={'package_id': reqData['package_id'],
                    'url': reqData['url'],
                    #'name': reqData['name']
                    },
              headers={"X-CKAN-API-Key": reqData['apikey']},
              files=[('upload', file(reqData['url']))])
        return response

class DownloadController(base.BaseController):    
    
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
        
        res_access = c.package.res_access
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
        
''' class ExportController(PackageController):
        
    def gmd(self, id):
        format = 'html'

        # response.headers['Content-Type'] = ctype
        response.headers['Content-Type'] = 'application/vnd.iso.19139+xml; charset=utf-8'.encode("ISO-8859-1")
        response.headers["Content-Disposition"] = ("attachment; filename=" + id + ".xml").encode("ISO-8859-1")
        package_type = self._get_package_type(id.split('@')[0])
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'auth_user_obj': c.userobj}
        data_dict = {'id': id}

        # interpret @<revision_id> or @<date> suffix
        split = id.split('@')
        if len(split) == 2:
            data_dict['id'], revision_ref = split
            if model.is_id(revision_ref):
                context['revision_id'] = revision_ref
            else:
                try:
                    date = h.date_str_to_datetime(revision_ref)
                    context['revision_date'] = date
                except TypeError, e:
                    base.abort(400, _('Invalid revision format: %r') % e.args)
                except ValueError, e:
                    base.abort(400, _('Invalid revision format: %r') % e.args)
        elif len(split) > 2:
            base.abort(400, _('Invalid revision format: %r') %
                       'Too many "@" symbols')

        # check if package exists
        try:
            c.pkg_dict = logic.get_action('package_show')(context, data_dict)
            c.pkg = context['package']
        except NotFound:
            base.abort(404, _('Dataset not found'))
        except NotAuthorized:
            base.abort(401, _('Unauthorized to read package %s') % id)

        # used by disqus plugin
        c.current_package_id = c.pkg.id
        c.related_count = c.pkg.related_count

        # can the resources be previewed?
        for resource in c.pkg_dict['resources']:
            resource['can_be_previewed'] = self._resource_preview(
                {'resource': resource, 'package': c.pkg_dict})

        self._setup_template_variables(context, {'id': id},
                                       package_type=package_type)

        #package_saver.PackageSaver().render_package(c.pkg_dict, context)

        template = 'package/read.gmd'

        try:
            return base.render(template, extra_vars={'dataset_type': package_type})
        except render.TemplateNotFound:
            msg = _("Viewing {package_type} datasets in {format} format is "
                    "not supported (template file {file} not found).".format(
                package_type=package_type, format=format, file=template))
            base.abort(403, msg)

        assert False, "We should never get here"

        #return p.toolkit.render('package/read.gmd.xml', loader_class=MarkupTemplate)
'''
        