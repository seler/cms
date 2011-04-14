from cms.models import Page
from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.conf import settings
from django.core.xheaders import populate_xheaders
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from django.db.models.base import get_absolute_url

DEFAULT_TEMPLATE = 'pages/default.html'

# This view is called from PageFallbackMiddleware.process_response
# when a 404 is raised, which often means CsrfViewMiddleware.process_view
# has not been called even if CsrfViewMiddleware is installed. So we need
# to use @csrf_protect, in case the template needs {% csrf_token %}.
# However, we can't just wrap this view; if no matching page exists,
# or a redirect is required for authentication, the 404 needs to be returned
# without any CSRF checks. Therefore, we only
# CSRF protect the internal implementation.
def page(request, url):
    if not url.endswith('/') and settings.APPEND_SLASH:
        return HttpResponseRedirect("%s/" % request.path)
    if not url.startswith('/'):
        url = "/" + url
    f = get_object_or_404(Page, absolute_url__exact=url, sites__id__exact=settings.SITE_ID)
    return render_page(request, f)

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
