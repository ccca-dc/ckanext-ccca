import re
import ckan.logic as logic

import ckan.controllers.group as group
import ckan.controllers.organization as organization
from ckan.common import OrderedDict, c, g, request, _
import ckan.model as model
import ckan.lib.helpers as h
import ckan.lib.base as base
import  ckan.plugins.toolkit as tk
context = tk.c

abort = base.abort
render = base.render
NotAuthorized = logic.NotAuthorized
from ckanext.filtersearch import helpers as hf

import ckan.plugins as plugins

# FIXME: Check if filtersearch loaded

class CCCACategoriesController(base.BaseController):

    """
        Use Group Controller to build Categories
    """
    def index(self):

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'with_private': False}

         # FIXME: How to get them from scheming JSON???
        values =["001","002", "004", "005", "009", "012", "017", "018", "019", "020"]

        topic_field = hf.filtersearch_get_topic_field()

        # Get count of datasets for topics
        data_dict={'sort': None, 'fq': '', 'rows': 20, 'facet.field': [ topic_field ], 'q': u'', 'start': 0, 'extras': {}}

        query = tk.get_action('package_search')(context, data_dict)
        #print query['search_facets']
        #print query

        facets = query['search_facets']
        topic_facets = facets[topic_field]
        topic_facets = topic_facets['items']

        cat = []
        for val in values:
            categories = {}
            match = next((t for t in topic_facets if t['name'] == val), None)
            if val == "012":
                categories['image_display_url'] = h.url_for_static('/images/water.png')
            elif val == "001":
                categories['image_display_url'] = h.url_for_static('/images/agriculture.png')
            elif val == "005":
                categories['image_display_url'] = h.url_for_static('/images/tourism.png')
            elif val == "002":
                categories['image_display_url'] = h.url_for_static('/images/pheno.png')
            elif val == "004":
                categories['image_display_url'] = h.url_for_static('/images/climate.png')
            elif val == "009":
                categories['image_display_url'] = h.url_for_static('/images/health.png')
            elif val == "017":
                categories['image_display_url'] = h.url_for_static('/images/infrastructure.png')
            elif val == "018":
                categories['image_display_url'] = h.url_for_static('/images/transport.png')
            elif val == "019":
                categories['image_display_url'] = h.url_for_static('/images/energy.png')
            elif val == "020":
                categories['image_display_url'] = h.url_for_static('/images/disaster.png')

            categories['count'] = match['count'] if match else 0
            categories['value'] = val
            categories['name'] =  hf.filtersearch_get_topic(topic_field,val)
            cat.append(categories)

        c.categories= cat
        return render('categories/index.html')
