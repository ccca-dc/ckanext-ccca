# encoding: utf-8

from pylons import cache
import sqlalchemy.exc

import ckan.logic as logic
import ckan.lib.maintain as maintain
import ckan.lib.search as search
import ckan.lib.base as base
import ckan.model as model
import ckan.lib.helpers as h

from ckan.common import _, g, c

CACHE_PARAMETERS = ['__cache', '__no_cache__']


class DisclaimerController(base.BaseController):

    def disclaimer(self):
        return base.render('home/disclaimer.html')
