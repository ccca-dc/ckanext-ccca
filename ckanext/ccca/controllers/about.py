
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

def _check_existing_formats(ff, list_of_formats):

    for x in list_of_formats:
        for d in x:
            if d['format'] == ff:
                return True
            else:
                break
    return False


class AboutController(p.toolkit.BaseController):
    """
    Controller for displaying about pages
    """
    def news_archive(self):

        #Show list of news: Abstract of newest resource per version
        #Display Archive: One File/Link per Format per Year - Year identified via name

        news_id  = hc.ccca_check_news()

        if not news_id:
            return
        try:
            news_pkg = tk.get_action('package_show')({}, {'id': news_id, 'include_datasets':True})
        except:
            print "No News Dataset founds ..."
            return

        #get a list with news messages
        news_list = []
        #get the newest files with different resource titles
        formats_and_files = []
        d_titles = []

        nd = ''
        newest_res = {}
        newest_title = ''
        # consider distributions and look for latest change
        newest_res = {}
        # Build initial formatlist
        for x in news_pkg['resources']:
            #latest change
            if x['created'] > nd or  x['last_modified'] > nd:
                nd = x['last_modified'] if x['last_modified'] else x['created']
                newest_res = x
                newest_title = x['name']
            #consider distributions
            f = []
            f_entry = {}
            f_entry['url'] = x['url']
            f_entry['name'] = x['name']
            f_entry['format'] = x['format']
            if x['format'] == '': # presumably URL
                f_entry['format'] = "Link"

            f.append(f_entry)
            formats_and_files.append(f)

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

                    #Search formats years
                    for res in news_pkg['resources']:
                         f_entry = {}
                         f_entry['url'] = res['url']
                         f_entry['name'] = res['name']
                         f_entry['format'] = res['format']
                         if res['format'] == '': # presumably URL
                              f_entry['format'] = 'Link'
                         if not _check_existing_formats(f_entry['format'], formats_and_files):
                             # New list of files for format
                             ff = []
                             ff.append(f_entry)
                             formats_and_files.append(ff)
                         else:
                             if res['name'] != newest_title: #one file per format per year
                                 newest_title = res['name']
                                 for fl in formats_and_files:
                                     for f in fl:
                                         if f['format'] == f_entry['format']:
                                            fl.append(f_entry)
                                            break
                        # Next loop
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



        #print formats_and_files

        # Link as last item(s)
        sorted_format_and_files =[]
        for ff in formats_and_files:
            if ff[0]['format'] != 'Link':
                sorted_format_and_files.append(ff)
        for ff in formats_and_files:
            if ff[0]['format'] == 'Link':
                sorted_format_and_files.append(ff)

        print "FINAL LIst"
        print sorted_format_and_files

        return p.toolkit.render('about/news_archive.html', {'title': 'News Archive', 'news': news_list, 'files': sorted_format_and_files })

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
