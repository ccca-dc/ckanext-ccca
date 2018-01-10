
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

            #get a list with news messages
            news_list = []
            #get the newest files with different resource titles
            files = []
            d_titles = []

            nd = ''
            newest_res = {}
            newest_title = ''
            # consider distributions and look for latest change
            newest_res = {}
            #FIXME: Wenn neueste Version nur eine Distribuion hat, werden die alten nicht angezeigt...
            for x in news_pkg['resources']:
                #latest change
                if x['last_modified'] > nd:
                    nd = x['last_modified']
                    newest_res = x
                    newest_title = x['name']
                #consider distributions
                f = []
                f_entry = {}
                f_entry['url'] = x['url']
                f_entry['name'] = x['name']
                f_entry['format'] = x['format']
                f.append(f_entry)
                files.append(f)


            news_list.append(newest_res)

            #Look for older versions and append them to list for template
            relations = news_pkg['relations']
            if len(relations) > 0:
                has_older_versions = True
            else:
                has_older_versions = False

            while has_older_versions:

                for x in relations:
                    if x['relation'] == 'is_version_of':
                        older_version= x['id']
                        news_pkg = tk.get_action('package_show')({}, {'id':older_version, 'include_datasets':True})

                        # implicates that all distributions have the same description!
                        news_list.append(news_pkg['resources'][0])

                        #Consider distributions and titles#
                        #FIXME: Might lead to a durcheinander if distributions are not always in the same order....
                        # and different numbers of distributions.... and latest change not first in list ....
                        #check dict entrys...
                        if news_pkg['resources'][0]['name'] != newest_title:
                             newest_title = news_pkg['resources'][0]['name']
                             index = 0
                             for x in news_pkg['resources']:
                                 #print "hi"
                                 f_entry = {}
                                 f_entry['url'] = x['url']
                                 f_entry['name'] = x['name']
                                 f_entry['format'] = x['format']
                                 for fl in files:
                                     for f in fl:
                                         if f['format'] == f_entry['format']:
                                            fl.append(f_entry)
                                            break
                                 index +=1
                        # NExt loop
                        relations = news_pkg['relations']
                        if len(relations) > 0:
                            has_older_versions = True
                        else:
                            has_older_versions = False
                    elif x['relation'] == 'has_version' and len(relations) == 1 :
                        has_older_versions = False
                        break
                    else:
                        continue

        except:
            print "des war nix ..."
            return

        #print files

        return p.toolkit.render('about/news_archive.html', {'title': 'News Archive', 'news': news_list, 'files': files })


        # Reverse order
        news_list = list(reversed(news_list))

        # Remove versions and save urls and titles of older archives
        files = []
        for x in news_list:
            if 'newer_version' in x and x['newer_version'] == "":
                f_entry = {}
                f_entry['url'] = x['url']
                f_entry['name'] = x['name']
                files.append(f_entry)
                #print x['name']

        #print files
        #print json.dumps(news_res_list, indent=3)
        #print json.dumps (list(reversed(news_res_list)),indent=3)
        #print json.dumps(files, indent=3)

        return p.toolkit.render('about/news_archive.html', {'title': 'News Archive', 'news': news_list, 'files': files })

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
