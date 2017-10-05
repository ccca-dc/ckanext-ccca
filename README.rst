============
ckanext-ccca
============

This is a plugin for the CKAN data server software http://ckan.org/ to extend its functionality for the CCCA (http://data.ccca.ac.at) open data server


------------
Requirements
------------

This plugin is tested with CKAN version 2.5.2 and 2.5.3.
It depends on ckanext-mdedit (categories) and ckanext-filtersearch (categories - iso_tpCat)
Overrides major settings from main.css - span9 width etc

Load as first plugin!

Implements as well top level nav-item "Categories" (together with ckanext-mdedit and ckanext-filtersearch)
Implements a News Box on front page; Configure as sysadmin "News-Tab"
Leave "Date" empty: Display featured_group - no news
Leave Text Empty: Default Text is displayed (sorry, so far hard coded)
If news_archive configured (see below) news will be stored in the news_archive

Change your INI-File (development.ini / production.ini) in the following way::
    ckan.plugins =  ccca resource_proxy text_view image_view recline_view geo_view geojson_view spatial_metadata harvest ckan_harvester csw_harvester doc_harvester ccca
    [...]
    ckan.views.default_views = image_view text_view recline_view geojson_view geo_view
    [...]
    ## Front-End Settings
    ckan.site_title = CCCA
    ckan.site_logo = /images/CCCA_DS_Header.png
    ckan.site_description =
    ckan.favicon = /images/favicon.ico

    ckan.featured_orgs = ....
    ckan.featured_groups = ....


------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-ccca:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-ccca Python package into your virtual environment::

     pip install ckanext-ccca

3. Add ``ccca`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``). Best at the last position

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


---------------
Config Settings
---------------

Document any optional config settings here. For example::

    # Create a news archive (ensure access rights for the file):
    ckanext.ccca.news_archive = /etc/ckan/default/news_archive.txt
    # Enable tracking
    ckan.tracking_enabled = true
    # Path where new user requests are stored
    ckanext.ccca.path_for_ldifs = /etc/ckan/default/ldif




------------------------
Development Installation
------------------------

To install ckanext-ccca for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/ccca-dc/ckanext-ccca.git
    cd ckanext-ccca
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.ccca --cover-inclusive --cover-erase --cover-tests


--------------------------------
Registering ckanext-ccca on PyPI
--------------------------------

ckanext-ccca should be availabe on PyPI as
https://pypi.python.org/pypi/ckanext-ccca. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags


---------------------------------------
Releasing a New Version of ckanext-ccca
---------------------------------------

ckanext-ccca is availabe on PyPI as https://pypi.python.org/pypi/ckanext-ccca.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags

-------------------
Copying and License
-------------------

This material is copyright (c) 2016 Climate Change Centre Austria (CCCA) http://www.ccca.ac.at

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
