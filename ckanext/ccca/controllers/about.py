
import ckan.plugins as p
from ckan.common import _, g, c
import ckan.lib.helpers as h
from ckanext.stats import stats as stats_lib


class AboutController(p.toolkit.BaseController):
    """
    Controller for displaying about pages
    """
    def news(self):
        return p.toolkit.render('about/news_archive.html', {'title': 'News Archive'})

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
