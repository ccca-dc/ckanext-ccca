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
from ckan.common import _, request
import ckan.lib.navl.dictization_functions as dictization_functions
from ckan.common import _, c, g, request, response
from pylons import config

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
    new_user_form = 'user/new_user_form.html'
    new_user_reply = 'user/new_user_reply.html'

    def _new_form_to_db_schema(self):
        return schema.user_new_form_schema()

    def register(self, data=None, errors=None, error_summary=None):
        context = {'model': model, 'session': model.Session, 'user': c.user,
                   'auth_user_obj': c.userobj}
        try:
            check_access('user_create', context)
        except NotAuthorized:
            abort(403, _('Unauthorized to register as a user.'))

        return self.new_mail_request(data, errors, error_summary)

    def new_mail_request(self, data=None, errors=None, error_summary=None):
        '''GET to display a form for registering a new user.
           or POST the form data to actually mail the user
           ldif file to side admin.
        '''

        context = {'model': model, 'session': model.Session,
                   'user': c.user,
                   'auth_user_obj': c.userobj,
                   'schema': self._new_form_to_db_schema(),
                   'save': 'save' in request.params}

        try:
            check_access('user_create', context)
        except NotAuthorized:
            abort(403, _('Unauthorized to create a user'))

        if context['save'] and not data:
            return self._request_user(context)

        if c.user and not data:
            # #1799 Don't offer the registration form if already logged in
            return render('user/logout_first.html')

        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors, 'error_summary': error_summary}

        c.is_sysadmin = authz.is_sysadmin(c.user)
        c.form = render(self.new_user_form, extra_vars=vars)
        return render('user/new.html')

    def _request_user(self, context):
        try:
            data_dict = logic.clean_dict(unflatten(
                logic.tuplize_dict(logic.parse_params(request.params))))
            context['message'] = data_dict.get('log_message', '')
            captcha.check_recaptcha(request)

            path = config.get('ckanext.ccca.path_for_ldifs')

            send_from = 'test@sandboxdc.ccca.ac.at'
            send_to = ['datenzentrum@ccca.ac.at']
            subject = 'New user request CKAN: ' + data_dict['name']

            if path is None:
                error_msg = _(u'path_for_ldifs not defined.')
                h.flash_error(error_msg)
                return self.new_mail_request(data_dict)

            if os.path.exists(path + '/' + data_dict['name'] + '.ldif'):
                error_msg = _('Username alreay exists, use another one.')
                h.flash_error(error_msg)
                return self.new_mail_request(data_dict)

            text = '''
             A new user registered.
             You can find the file here: ''' + path + '''
             and it is called: ''' + data_dict['name']+'.ldif' + '''
             Create user on your LDAP Server with the following command:
             adduser_ldap.sh HOST FILE'''

            _make_ldif(context, data_dict, config.get('ckanext.ccca.path_for_ldifs') + '/' + data_dict['name']+'.ldif')
            _send_mail(send_from, send_to, subject, text)

        except NotAuthorized:
            error_msg = _(u'Username already exists, use another one.')
            h.flash_error(error_msg)
            return self.new_mail_request(data_dict)
        except NotFound, e:
            abort(404, _('User not found'))
        except DataError:
            abort(400, _(u'Integrity Error'))
        except captcha.CaptchaError:
            error_msg = _(u'Bad Captcha. Please try again.')
            h.flash_error(error_msg)
            return self.new_mail_request(data_dict)
        except ValidationError, e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.new_mail_request(data_dict, errors, error_summary)
        except IOError:
            error_msg = _(u'path_for_ldifs not correctly defined.')
            h.flash_error(error_msg)
            return self.new_mail_request(data_dict)

        h.flash_success('''Your request was delivered to the CCCA Datacentre.
        It will be processed within the upcoming working days.''')
        return render('user/login.html')


def _send_mail(send_from, send_to, subject, text):
    import smtplib
    from email.mime.application import MIMEApplication
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.utils import COMMASPACE, formatdate
    from os.path import basename

    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    smtp = smtplib.SMTP(config.get('smtp.server'))
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()


def _make_ldif(context, data_dict, filepath):
    """
    Create ldif file in filepath from data_dict input
    """
    schema = context.get('schema') or logic.schema.default_user_schema()
    #schema = context.get('schema') or logic.schema.user_new_form_schema()
    session = context['session']

    check_access('user_create', context, data_dict)

    data, errors = _validate(data_dict, schema, context)

    if errors:
        session.rollback()
        raise ValidationError(errors)

    hash_password = _make_secret(data_dict['password1'])

    data_dict = dict((k, v.encode('utf-8')) for (k, v) in data_dict.items())
    # Add user
    entry_user = {'objectClass': ['top', 'person', 'organizationalPerson',
                                  'inetOrgPerson', 'posixAccount', 'shadowAccount',
                                  'ldapPublicKey'],
                  'uid': [data_dict['name']],
                  'cn': [data_dict['fullname']],
                  'sn': [data_dict['fullname'].split()[-1]],
                  'givenName': [' '.join(data_dict['fullname'].split()[:-1])],
                  'mail': [data_dict['email']],
                  'userPassword': [hash_password],
                  'loginShell': ['/usr/bin/mysecureshell'],
                  'uidNumber': ['UID'],
                  'gidNumber': ['GID'],
                  'homeDirectory': ['/e/user/home/' + data_dict['name']],
                  'sshPublicKey': [data_dict['sshkey']]}
    dn_user = 'uid='+str(data_dict['name'])+',ou=people,dc=ldap,dc=ccca,dc=ac,dc=at'
    with open(filepath, 'w') as file:
        ldif_writer = ldif.LDIFWriter(file, filepath)
        ldif_writer.unparse(dn_user, entry_user)

    # Add specific user group
    dn_group = 'cn='+str(data_dict['name'])+',ou=groups,dc=ldap,dc=ccca,dc=ac,dc=at'
    entry_group = {'objectClass': ['posixGroup'],
                   'cn': [data_dict['name']],
                   'gidNumber': ['GID'],
                   'memberUid': [data_dict['name']]}
    with open(filepath, 'a') as file:
        ldif_writer = ldif.LDIFWriter(file, filepath)
        ldif_writer.unparse(dn_group, entry_group)


    # Add user to general user group
    dn_group_users = 'cn=users,ou=groups,dc=ldap,dc=ccca,dc=ac,dc=at'
    entry_group_users = [(ldap.MOD_ADD,'memberUid',[data_dict['name']])]
    with open(filepath, 'a') as file:
        ldif_writer = ldif.LDIFWriter(file, filepath)
        ldif_writer.unparse(dn_group_users, entry_group_users)

    return filepath


def _check_password(tagged_digest_salt, password):
    """
    Checks the OpenLDAP tagged digest against the given password
    """
    # the entire payload is base64-encoded
    assert tagged_digest_salt.startswith('{SSHA}')

    # strip off the hash label
    digest_salt_b64 = tagged_digest_salt[6:]

    # the password+salt buffer is also base64-encoded.  decode and split the
    # digest and salt
    digest_salt = digest_salt_b64.decode('base64')
    digest = digest_salt[:20]
    salt = digest_salt[20:]

    sha = hashlib.sha1(password)
    sha.update(salt)

    return digest == sha.digest()


def _make_secret(password):
    """
    Encodes the given password as a base64 SSHA hash+salt buffer

    @param password: Password for hashing
    @return: Hashed password
    """
    salt = os.urandom(4)

    # hash the password and append the salt
    sha = hashlib.sha1(password)
    sha.update(salt)

    # create a base64 encoded string of the concatenated digest + salt
    digest_salt_b64 = '{}{}'.format(sha.digest(), salt).encode('base64').strip()

    # now tag the digest above with the {SSHA} tag
    tagged_digest_salt = '{{SSHA}}{}'.format(digest_salt_b64)

    return tagged_digest_salt
