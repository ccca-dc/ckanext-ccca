from pylons import config

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.app_globals as app_globals
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.model as model
import ckan.logic as logic
import ckan.plugins as plugins
import ckan.controllers.admin as admin


c = base.c
request = base.request
_ = base._



class CCCAAdminController(admin.AdminController):

    def _get_news(self):

        items = [
            {'name': 'ckan.site_about', 'control': 'input', 'label': _('Date'), 'placeholder': _('Date')},
            {'name': 'ckan.site_intro_text', 'control': 'markdown', 'label': _('News'), 'placeholder': _('Text for the News Section')}
        ]
        return items

    def news(self):

        items = self._get_news()
        data = request.POST
        if 'save' in data:
            try:
                # really?
                data_dict = logic.clean_dict(
                    dict_fns.unflatten(
                        logic.tuplize_dict(
                            logic.parse_params(
                                request.POST))))

                del data_dict['save']

                data = logic.get_action('config_option_update')(
                    {'user': c.user}, data_dict)
            except logic.ValidationError, e:
                errors = e.error_dict
                error_summary = e.error_summary
                vars = {'data': data, 'errors': errors,
                        'error_summary': error_summary, 'form_items': items}
                return base.render('admin/news.html', extra_vars=vars)

            h.redirect_to(controller='ckanext.ccca.controllers.admin:CCCAAdminController', action='news')

        schema = logic.schema.update_configuration_schema()
        data = {}
        for key in schema:
            data[key] = config.get(key)

        vars = {'data': data, 'errors': {}, 'form_items': items}
        return base.render('admin/news.html',
                           extra_vars=vars)
