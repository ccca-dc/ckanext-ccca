import re
import json
import logging
import os.path as path
from ckanext.ccca.common import config
from ckanext.ccca.common import pylons_i18n
from ckanext.ccca.common import base, logic
from ckanext.ccca.common import helpers as h
from itertools import count
from ckan.lib.navl.dictization_functions import Invalid
from ckan.model import (MAX_TAG_LENGTH, MIN_TAG_LENGTH)

#from ckan.logic import ValidationError
ValidationError = logic.ValidationError
import ckan.lib.navl.dictization_functions as df
StopOnError = df.StopOnError
get_action = logic.get_action
import os


log = logging.getLogger(__name__)

def is_valid_json(key, data, errors, context):
    """
    Checks that a string can be parsed as JSON.

    @param key:
    @param data:
    @param errors:
    @param context:
    @return: None
    """

    try:
        json.loads(data[key])
    except:
        errors[key].append(pylons_i18n._('Must be JSON serializable'))
