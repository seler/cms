from cms.models import Page
from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.core.xheaders import populate_xheaders
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from django.db.models.base import get_absolute_url
from django.utils import translation

DEFAULT_TEMPLATE = 'pages/default.html'

def page(request, url):
    if not url.endswith('/') and settings.APPEND_SLASH:
        return HttpResponseRedirect("%s/" % request.path)
    if not url.startswith('/'):
        url = "/" + url

    if 'lang' not in request.COOKIES:
        translation.activate(translation.get_language_from_request(request))
        request.COOKIES['lang'] = translation.get_language_from_request(request)
    if 'lang' in request.GET:
        if translation.check_for_language(request.GET['lang']):
            translation.activate(request.GET['lang'])
            request.COOKIES['lang'] = request.GET['lang']

    p = Page.objects.filter(absolute_url__exact=url, sites__id__exact=settings.SITE_ID)
    if len(p.all()) == 0:
        raise Http404
    elif len(p.all()) > 1:
        #p1 = p.filter(language_code=translation.get_language_from_request(request))
        p1 = p.filter(language_code=translation.get_language())
        if len(p1.all()) == 0:
            p1 = p.filter(language_code=settings.LANGUAGE_CODE)
        p = p1[0]
    else: p = p[0]
    #f = get_object_or_404(Page, absolute_url__exact=url, sites__id__exact=settings.SITE_ID)
    return render_page(request, p)

@csrf_protect
def render_page(request, p):
    """
    Internal interface to the page view.
    """
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    # If page is not pusblished and user is not admin of pages then raises 404
    if not p.is_published() and not request.user.has_perm('cms.view_drafts'):
        raise Http404
    if p.registration_required and not request.user.is_authenticated():
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.path)
    if p.template_name:
        t = loader.select_template((p.template_name, DEFAULT_TEMPLATE))
    else:
        t = loader.get_template(DEFAULT_TEMPLATE)

    # To avoid having to always use the "|safe" filter in page templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    p.title = mark_safe(p.title)
    p.content = mark_safe(p.content)

    c = RequestContext(request, {
        'page': p,
    })
    response = HttpResponse(t.render(c))
    populate_xheaders(request, response, Page, p.id)
    return response
