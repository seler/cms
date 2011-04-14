from django import forms
from django.contrib import admin
from cms.models import Page
from django.utils.translation import ugettext_lazy as _
from mptt.admin import MPTTModelAdmin
from django.conf import settings
from django.contrib.sites.models import Site


class PageForm(forms.ModelForm):
    url = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/\.~]+$', required=False,
        help_text=_("Example: '/about/contact/'. Make sure to have leading"
                      " and trailing slashes."),
        error_message=_("This value must contain only letters, numbers,"
                          " dots, underscores, dashes, slashes or tildes."))

    class Meta:
        model = Page

    '''
    def clean_translation_of(self):
        is_translation = self.cleaned_data.get('is_translation')
        if not is_translation:
            return self
        else:
            return self.cleaned_data.get('translation_of')
    '''
    def clean_sites(self):
        sites = self.cleaned_data.get('sites')
        print sites
        return [Site.objects.get(id=settings.SITE_ID)]

"""
class PageAdmin(admin.ModelAdmin):
    form = PageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
    list_display = ('url', 'title')
    list_filter = ('sites', 'enable_comments', 'registration_required')
    search_fields = ('url', 'title')

admin.site.register(Page, PageAdmin)
"""

class PageAdmin(MPTTModelAdmin):
    form = PageForm
    fieldsets = (
                 (_('Language setup'), {'fields': ('language_code', 'is_translation', 'translation_of')}),
                 (None, {'fields': ('parent', 'title', 'menu_name', 'slug', 'status', 'author', 'content')}),
                 (_('Advanced options'), {'classes': ('collapse',), 'fields': ('url_type', 'url', 'tags', 'publish_date', 'last_modified', 'enable_comments', 'registration_required', 'template_name', 'sites')}),
                 )
    list_filter = ('sites', 'language_code', 'registration_required')
    search_fields = ('url', 'title')

admin.site.register(Page, PageAdmin)
