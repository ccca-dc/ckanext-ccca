import logging
import os
import ldif
import ldap
import hashlib

import pylons

import ckan.plugins as p
import ckan.model as model
import ckan.logic as logic
import ckan.logic.schema as schema
import ckan.lib.helpers as h
import ckan.lib.base as base
import ckan.authz as authz
import ckan.lib.captcha as captcha
import ckan.lib.dictization.model_dictize as model_dictize
from ckan.common import _, request
import ckan.lib.navl.dictization_functions as dictization_functions
from ckan.common import _, c, g, request, response
from paste.deploy.converters import asbool

from pylons import config
import paste.deploy.converters

log = logging.getLogger(__name__)


abort = base.abort
render = base.render

_validate = dictization_functions.validate
check_access = logic.check_access
get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
UsernamePasswordError = logic.UsernamePasswordError

DataError = dictization_functions.DataError
unflatten = dictization_functions.unflatten


class MultipleMatchError(Exception):
    pass


class UserConflictError(Exception):
    pass


class UserController(p.toolkit.BaseController):


    def read(self, id=None):
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj,
                   'for_view': True}
        data_dict = {'id': id,
                     'user_obj': c.userobj,
                     'include_datasets': True,
                     'include_num_followers': True}

        self._setup_template_variables(context, data_dict)

        # The legacy templates have the user's activity stream on the user
        # profile page, new templates do not.
        if asbool(config.get('ckan.legacy_templates', False)):
            c.user_activity_stream = get_action('user_activity_list_html')(
                context, {'id': c.user_dict['id']})

        return render('user/read.html')

    def _setup_template_variables(self, context, data_dict):
        c.is_sysadmin = authz.is_sysadmin(c.user)
        try:
            # calling adapted user_show instead of CKAN's user_show
            user_dict = _user_show(context, data_dict)
        except NotFound:
            abort(404, _('User not found'))
        except NotAuthorized:
            abort(403, _('Not authorized to see this page'))

        c.user_dict = user_dict
        c.is_myself = user_dict['name'] == c.user
        c.about_formatted = h.render_markdown(user_dict['about'])

# user_show from CKAN but changed the limit in order to show more than 50 packages
def _user_show(context, data_dict):
    '''Return a user account.

    Either the ``id`` or the ``user_obj`` parameter must be given.

    :param id: the id or name of the user (optional)
    :type id: string
    :param user_obj: the user dictionary of the user (optional)
    :type user_obj: user dictionary
    :param include_datasets: Include a list of datasets the user has created.
        If it is the same user or a sysadmin requesting, it includes datasets
        that are draft or private.
        (optional, default:``False``, limit:50)
    :type include_datasets: boolean
    :param include_num_followers: Include the number of followers the user has
        (optional, default:``False``)
    :type include_num_followers: boolean
    :param include_password_hash: Include the stored password hash
        (sysadmin only, optional, default:``False``)
    :type include_password_hash: boolean

    :returns: the details of the user. Includes email_hash, number_of_edits and
        number_created_packages (which excludes draft or private datasets
        unless it is the same user or sysadmin making the request). Excludes
        the password (hash) and reset_key. If it is the same user or a
        sysadmin requesting, the email and apikey are included.
    :rtype: dictionary

    '''
    model = context['model']

    id = data_dict.get('id', None)
    provided_user = data_dict.get('user_obj', None)
    if id:
        user_obj = model.User.get(id)
        context['user_obj'] = user_obj
        if user_obj is None:
            raise NotFound
    elif provided_user:
        context['user_obj'] = user_obj = provided_user
    else:
        raise NotFound

    check_access('user_show', context, data_dict)

    # include private and draft datasets?
    requester = context.get('user')
    sysadmin = False
    if requester:
        sysadmin = authz.is_sysadmin(requester)
        requester_looking_at_own_account = requester == user_obj.name
        include_private_and_draft_datasets = (
            sysadmin or requester_looking_at_own_account)
    else:
        include_private_and_draft_datasets = False
    context['count_private_and_draft_datasets'] = \
        include_private_and_draft_datasets

    include_password_hash = sysadmin and asbool(
        data_dict.get('include_password_hash', False))

    user_dict = model_dictize.user_dictize(
        user_obj, context, include_password_hash)

    if context.get('return_minimal'):
        log.warning('Use of the "return_minimal" in user_show is '
                    'deprecated.')
        return user_dict

    if asbool(data_dict.get('include_datasets', False)):
        user_dict['datasets'] = []

        fq = "+creator_user_id:{0}".format(user_dict['id'])

        # changed rows- previously 50
        search_dict = {'rows': 10000}

        if include_private_and_draft_datasets:
            if include_private_and_draft_datasets:
                search_dict.update({
                    'include_private': True,
                    'include_drafts': True})

        search_dict.update({'fq': fq})

        user_dict['datasets'] = \
            logic.get_action('package_search')(context=context,
                                               data_dict=search_dict) \
            .get('results')

    if asbool(data_dict.get('include_num_followers', False)):
        user_dict['num_followers'] = logic.get_action('user_follower_count')(
            {'model': model, 'session': model.Session},
            {'id': user_dict['id']})

    return user_dict
