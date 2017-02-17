import re

import ckan.controllers.group as group
import ckan.controllers.organization as organization
from ckan.common import OrderedDict, c, g, request, _
import ckan.model as model
import ckan.lib.helpers as h
import ckan.lib.base as base

render = base.render


import ckan.plugins as plugins


class CCCAOrganizationController(organization.OrganizationController):

    """
    Overwrites Controller for the display of the organization list (Path: /organization )
    in order to change the default search order

    Function index copied from orginal - modifications marked
    """
    def index(self):
        group_type = self._guess_group_type()

        page = self._get_page_number(request.params) or 1
        items_per_page = 21

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'with_private': False}

        q = c.q = request.params.get('q', '')

        # ****************** Modified part start (Anja 3.1.17)
        criteria = request.params.get('sort')

        if criteria != None:
            sort_by = c.sort_by_selected = request.params.get('sort')
        else:
            sort_by = c.sort_by_selected = 'package_count'
        # ****************** Modified part end (Anja 3.1.17)

        try:
            self._check_access('site_read', context)

        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        # pass user info to context as needed to view private datasets of
        # orgs correctly
        if c.userobj:
            context['user_id'] = c.userobj.id
            context['user_is_admin'] = c.userobj.sysadmin

        data_dict_global_results = {
            'all_fields': False,
            'q': q,
            'sort': sort_by,
            'type': group_type or 'group',
        }
        global_results = self._action('group_list')(context,
                                                    data_dict_global_results)

        data_dict_page_results = {
            'all_fields': True,
            'q': q,
            'sort': sort_by,
            'type': group_type or 'group',
            'limit': items_per_page,
            'offset': items_per_page * (page - 1),
        }
        page_results = self._action('group_list')(context,
                                                  data_dict_page_results)

        c.page = h.Page(
            collection=global_results,
            page=page,
            url=h.pager_url,
            items_per_page=items_per_page,
        )

        c.page.items = page_results
        return render(self._index_template(group_type),
                      extra_vars={'group_type': group_type})