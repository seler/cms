from django import forms
from django.contrib import admin
from cms.models import Page
from django.utils.translation import ugettext_lazy as _
from mptt.admin import MPTTModelAdmin
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils import translation
from django.contrib.auth.models import User


class PageForm(forms.ModelForm):
    url = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/\.~]+$', required=False,
        help_text=_("Example: '/about/contact/'. Make sure to have leading"
                      " and trailing slashes."),
        error_message=_("This value must contain only letters, numbers,"
                          " dots, underscores, dashes, slashes or tildes."))

    #translates = forms.ModelChoiceField(queryset=Page.objects.filter(is_translation=False).exclude(pk=1), empty_label="(Nothing)", required=False)

    class Meta:
        model = Page

    '''
    def clean_translates(self):
        is_translation = self.cleaned_data.get('is_translation')
        if not is_translation:
            return self
        else:
            return self.cleaned_data.get('translates')
    '''
    def clean_sites(self):
        sites = self.cleaned_data.get('sites')
        print sites
        return [Site.objects.get(id=settings.SITE_ID)]


class PageAdmin(MPTTModelAdmin):
    form = PageForm
    fieldsets = (
                 (_('Language setup'), {'fields': ('language_code', 'is_translation', 'translates')}),
                 (None, {'fields': ('parent', 'title', 'menu_name', 'slug', 'status', 'author', 'content')}),
                 (_('Advanced options'), {'classes': ('collapse',), 'fields': ('url_type', 'url', 'tags', 'publish_date', 'last_modified', 'enable_comments', 'registration_required', 'template_name', 'sites')}),
                 )
    list_filter = ('sites', 'language_code', 'registration_required')
    search_fields = ('url', 'title')
    prepopulated_fields = {'slug': ('title',)}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            kwargs["initial"] = User.objects.get(pk=request.user.pk)
            kwargs["empty_label"] = _('none')
        if db_field.name == "translates":
            kwargs["queryset"] = Page.objects.filter(is_translation=False)
            kwargs["empty_label"] = _('nothing')
        return super(PageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Page, PageAdmin)
