
import ckan.plugins as p
from ckan.common import _, g, c
import ckan.lib.helpers as h
from ckanext.stats import stats as stats_lib

from pylons import config

class AboutController(p.toolkit.BaseController):
    """
    Controller for displaying about pages
    """
    def news_archive(self):

        if 'ckanext.ccca.news_archive' in config:
            news_file =  config.get ('ckanext.ccca.news_archive')

        news_list = []
        dict_item = {}
        try:
            news_f = open (news_file, 'r')
            if news_f:
                 for line in news_f:
                      if line.startswith('Date#:'):
                          splitLine = line.split('Date#:')
                          if len(splitLine) > 1:
                             news_list.append(dict_item)
                             dict_item = {}
                             dict_item['date'] = splitLine[1]
                             dict_item['news'] = ''
                      else:
                          dict_item['news']+= line

                 # add last element
                 news_list.append(dict_item)
                 # remove first element
                 news_list.pop(0)
                 # Newest first
                 news_list = list(reversed(news_list))
                 
                 news_f.close()
        except: pass

        return p.toolkit.render('about/news_archive.html', {'title': 'News Archive', 'news_list': news_list})

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
