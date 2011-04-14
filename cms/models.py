from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from datetime import datetime
from django.contrib.auth.models import User
from tagging.fields import TagField

URL_TYPE_CHOICES = (
            (False, _('slug')),
            (True, _('URL')),
)

YES_NO_CHOICES = (
            (True, _('Yes')),
            (False, _('No')),
)

STATUS_CHOICES = (
            (0, _('draft')),
            (1, _('published')),
)


class Page(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True, verbose_name=_('parent'), related_name=_('chidren'))
    url = models.CharField(_('URL'), max_length=100, db_index=True, null=True, blank=True)
    slug = models.SlugField(max_length=50, unique=True, verbose_name=_('slug'), null=True, blank=True)
    url_type = models.BooleanField(blank=False, null=False, choices=URL_TYPE_CHOICES, verbose_name=_('URL type'), default=True)
    absolute_url = models.TextField()
    publish_date = models.DateTimeField(default=datetime.now, verbose_name=_('publish date'))
    last_modified = models.DateTimeField(default=datetime.now, verbose_name=_('last modified'))
    menu_name = models.CharField(_('menu name'), max_length=100)
    tags = TagField(max_length=100, blank=True, verbose_name=_('tags'))
    author = models.ForeignKey(User, verbose_name=_('author'), blank=True, null=True)
    status = models.BooleanField(choices=STATUS_CHOICES, default=0, verbose_name=_('status'))
    title = models.CharField(_('title'), max_length=200)
    content = models.TextField(_('content'), blank=True)
    enable_comments = models.BooleanField(choices=YES_NO_CHOICES, verbose_name=_('enable comments'), default=False)
    template_name = models.CharField(_('template name'), max_length=70, blank=True)
    registration_required = models.BooleanField(choices=YES_NO_CHOICES, verbose_name=_('registration required'), default=False)
    sites = models.ManyToManyField(Site, verbose_name=_('sites'))

    ### multilingual support
    language_code = models.CharField(max_length=50, choices=settings.LANGUAGES, verbose_name=_('language code'))
    is_translation = models.BooleanField(choices=YES_NO_CHOICES, verbose_name=_('is translation'), default=False)
    translation_of = models.ForeignKey('self', verbose_name=_('translation of'), blank=True, null=True, related_name=_('translations'))

    class Meta:
        db_table = 'cms_page'
        verbose_name = _('page')
        verbose_name_plural = _('pages')
        permissions = (
            ("view_drafts", "Can see drafts"),
        )

    def save(self):
        if not self.is_translation:
            self.translation_of = self
        self.absolute_url = self.get_absolute_url()
        super(Page, self).save()

    def __unicode__(self):
        return u"%s -- %s (%s)" % (self.menu_name, self.title, self.get_absolute_url())

    def get_absolute_url(self):
        if self.url_type == False:   # if url type is slug
            if self.is_root_node():
                return '/' + self.slug + '/'
            else:
                return self.parent.get_absolute_url() + self.slug + '/'
        else: # url type is url
            return self.url

    def get_url_type(self):
        for option_key, option_value in URL_TYPE_CHOICES:
            if self.url_type == option_key:
                return option_value
        else:
            return None

    def get_translations(self):
        if not self.is_translation:
            return self.translations
        else:
            return self.translation_of.translations

    def get_language(self):
        '''
        returns language name
        '''
        for code, name in settings.LANGUAGES:
            if self.language_code == code:
                return name
        else:
            return None

    def get_status(self):
        '''
        returns status string
        '''
        for val, status in STATUS_CHOICES:
            if self.status == val:
                return status
        else:
            return None

    def get_fields(self):
        '''
        returns all fields of Page model
        rather for debug purpose
        '''
        return [(field.name, field.value_to_string(self)) for field in self._meta.fields]

    def is_published(self):
        ''' Checks if page has status of published and publish date is in past. '''
        return self.status == 1 and self.publish_date <= datetime.now()

    def was_modified(self):
        return self.publish_date < self.last_modified

    def has_translations(self):
        if self.is_translation:
            t = self.translation_of.get_translations()
        else:
            t = self.translations
        if len(t):
            return True
        else:
            return False
