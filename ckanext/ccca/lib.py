#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'gas' on 2016-06-16.
"""

import os
import itertools
import random
from logging import getLogger
from ckan.model import Session
from pylons import config
from requests.exceptions import HTTPError
import ckan.model as model
from ckan.lib import helpers as h
import ckan.plugins as plugin
#from b2handle.clientcredentials import PIDClientCredentials
#from b2handle.handleclient import EUDATHandleClient

log = getLogger(__name__)

def create_unique_identifier():
    """
    Create a unique identifier, using the prefix and a random uuid
    Checks the random number doesn't exist in the table or the datacite repository
    All unique identifiers are created with
    @return:
    """
    #datacite_api = DOIDataCiteAPI()
    handle_prefix='20.500.11756'
    identifier = os.path.join(handle_prefix, '{0:07}'.format(random.randint(1, 100000)))

    return identifier
