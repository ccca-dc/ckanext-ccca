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

            # check for unique email addresses within our system
            # i.e. every email only once
            new_mail = u''
            full_name = u''
            for k,v in data_dict.iteritems():
                if (k == 'email'):
                    new_mail = v
                if (k == 'fullname'):
                    full_name = v

            if full_name == u'':
                error_msg = _(u'Please insert full name.')
                h.flash_error(error_msg)
                return self.new_mail_request(data_dict)
            #print new_mail
            if new_mail == u'':
                error_msg = _(u'Please insert a valid mail address.')
                h.flash_error(error_msg)
                return self.new_mail_request(data_dict)

            #print "HEre we are"
            # ATTENTION: This action requires that userlist is available for anon users!
            u_list = get_action('user_list')({},{"order_by": "email"})

            #print "HEre we are 2"

            # need to access the ckan email_hash
            otto = model.User(email=new_mail)
            #print otto.email_hash
            for x in u_list:
                if x['email_hash'] == otto.email_hash:
                    error_msg = _(u'Error: Email Address already registered: ' + new_mail + '.  If you are insecure about this message please contact us: datanzentrum@ccca.ac.at')
                    h.flash_error(error_msg)
                    return self.new_mail_request(data_dict)

            # end check email unique

            path = config.get('ckanext.ccca.path_for_ldifs')

            send_from = 'new_user@data.ccca.ac.at'
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

            #print "HEre we are 2"

            text = '''
             A new user registered.
             You can find the file here: ''' + path + '''
             and it is called: ''' + data_dict['name']+'.ldif' + '''
             Create user on your LDAP Server with the following command:
             adduser_ldap_ckan.sh HOST FILE APIKey'''

            _make_ldif(context, data_dict, config.get('ckanext.ccca.path_for_ldifs') + '/' + data_dict['name']+'.ldif')
            #print "Here we are 3"
            _send_mail(send_from, send_to, subject, text)

        except NotAuthorized, e:
            print (e)
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
        except EnvironmentError, e:
            errors={}
            errors['Message'] = 'Internal Problem; please try again in a few minutes'
            return self.new_mail_request(data_dict, errors, errors)
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


    smtp_connection = smtplib.SMTP()
    smtp_server = config.get('smtp.server')
    smtp_starttls = paste.deploy.converters.asbool(
                config.get('smtp.starttls'))
    smtp_user = config.get('smtp.user')
    smtp_password = config.get('smtp.password')

   # smtp = smtplib.SMTP(config.get('smtp.server'))
    smtp_connection.connect(smtp_server)
    try:
        #smtp_connection.set_debuglevel(True)

        # Identify ourselves and prompt the server for supported features.
        smtp_connection.ehlo()

        # If 'smtp.starttls' is on in CKAN config, try to put the SMTP
        # connection into TLS mode.
        if smtp_starttls:
            if smtp_connection.has_extn('STARTTLS'):
                smtp_connection.starttls()
                # Re-identify ourselves over TLS connection.
                smtp_connection.ehlo()
            else:
                raise MailerException("SMTP server does not support STARTTLS")

        # If 'smtp.user' is in CKAN config, try to login to SMTP server.
        if smtp_user:
            assert smtp_password, ("If smtp.user is configured then "
                    "smtp.password must be configured as well.")
            smtp_connection.login(smtp_user, smtp_password)

        smtp_connection.sendmail(send_from, send_to, msg.as_string())
        log.info("Sent email to {0}".format(send_to))

    except smtplib.SMTPException, e:
        msg = '%r' % e
        log.exception(msg)
        raise MailerException(msg)
    finally:
        smtp_connection.quit()


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
                  'sn': [data_dict['fullname'].split()[-1]] if data_dict['fullname'] else [''],
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
