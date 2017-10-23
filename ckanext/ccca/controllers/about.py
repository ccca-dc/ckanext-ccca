
import ckan.plugins as p
from ckan.common import _, g, c
import ckan.lib.helpers as h

from pylons import config

import ckan.model as model
import ckan.plugins.toolkit as tk
import ckan.logic as logic
import ckan.lib.base as base

get_action = logic.get_action
context = tk.c
Base_c = base.c
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError

from ckanext.ccca import helpers as hc
import json

class AboutController(p.toolkit.BaseController):
    """
    Controller for displaying about pages
    """
    def news_archive(self):

        news_id  = hc.ccca_check_news()

        if not news_id:
            return
        try:
            news_pkg = tk.get_action('package_show')({}, {'id': news_id, 'include_datasets':True})

            news_res_list = news_pkg['resources']

        except:
            return

        # Reverse order
        news_res_list = list(reversed(news_res_list))

        n_file = news_res_list[0]['url']
        #print json.dumps(news_res_list, indent=3)
        #print json.dumps (list(reversed(news_res_list)),indent=3)

        return p.toolkit.render('about/news_archive.html', {'title': 'News Archive', 'news': news_res_list, 'file': n_file })

    def usage(self):
        return p.toolkit.render('about/usage.html', {'title': 'Usage Information'})

    def citation(self):
        return p.toolkit.render('about/citation.html', {'title': 'Citation and Identification'})

    def download(self):
        return p.toolkit.render('about/download.html', {'title': 'Download and API'})

    def prototype(self):
        return p.toolkit.render('about/prototype.html', {'title': 'Prototype Declaration'})

    def credits(self):
        return p.toolkit.render('about/credits.html', {'title': 'Acknowledgements'})

    def terms(self):
        return p.toolkit.render('about/terms.html', {'title': 'Open Source Data Platform'})

    def data_policy(self):
        return p.toolkit.render('about/data_policy.html', {'title': 'Data Policy'})
