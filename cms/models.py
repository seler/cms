from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

class Language(models.Model):
    """
    Languages definied for every site.
    """
    symbol = models.CharField(_('symbol'), max_length=5)
    name = models.CharField(_('name'), max_length=100)
    sites = models.ManyToManyField(Site)
    
    class Meta:
        db_table = 'cms_language'
        verbose_name = _('language')
        verbose_name_plural = _('language')
        ordering = ('symbol',)

class Page(models.Model):
    language = models.ManyToManyField(Language)
    url = models.CharField(_('URL'), max_length=100, db_index=True)
    title = models.CharField(_('title'), max_length=200)
    content = models.TextField(_('content'), blank=True)
    enable_comments = models.BooleanField(_('enable comments'))
    template_name = models.CharField(_('template name'), max_length=70, blank=True,
        help_text=_("Example: 'pages/contact_page.html'. If this isn't provided, the system will use 'pages/default.html'."))
    registration_required = models.BooleanField(_('registration required'), help_text=_("If this is checked, only logged-in users will be able to view the page."))
    sites = models.ManyToManyField(Site)

    class Meta:
        db_table = 'cms_page'
        verbose_name = _('page')
        verbose_name_plural = _('pages')
        ordering = ('url',)

    def __unicode__(self):
        return u"%s -- %s" % (self.url, self.title)

    def get_absolute_url(self):
        return self.url
