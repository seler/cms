===========
CMS Project
===========

Dependencies
============

CMS requires:
 - django-multilingual (http://code.google.com/p/django-multilingual/)
 - cos tam jeszcze

Instalation
===========

1. Install the sites framework by adding 'django.contrib.sites' to your INSTALLED_APPS setting, if it’s not already in there.

2. Make sure you’ve correctly set SITE_ID to the ID of the site the settings file represents. This will usually be 1 (i.e. SITE_ID = 1, but if you’re using the sites framework to manage multiple sites, it could be the ID of a different site.

3. Add 'cms' to your INSTALLED_APPS setting

4. Add 'cms.middleware.PageFallbackMiddleware' to your MIDDLEWARE_CLASSES setting.

5. Configure Django Multilingual (http://django-multilingual.googlecode.com/svn/trunk/docs/_build/html/overview.html#configuration)

x. Run the command manage.py syncdb.



 