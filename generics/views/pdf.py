# -*- coding: utf-8 -*-
import os
from cgi import escape
from cStringIO import StringIO

from django.template import loader, Context, RequestContext
from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponse

from wkhtmltopdf.utils import wkhtmltopdf, make_absolute_paths
from tempfile import NamedTemporaryFile

def content_to_pdf(content, encoding='utf-8', **options):
    """
    Write into *dest* file object the given html *content*.
    Returns the PDF Content
    """
    content = make_absolute_paths(content)
    tempfile = NamedTemporaryFile(mode='w+b',
                                  bufsize=-1,
                                  suffix='.html',
                                  prefix='tmp',
                                  dir=None,
                                  delete=True)

    tempfile.write(content.encode(encoding))
    tempfile.flush()
    # options['redirect-delay'] = 5000
    return wkhtmltopdf(pages=[tempfile.name], **options)

def content_to_response(content, filename=None):
    """
    Return a pdf response using given *content*.
    """
    response = HttpResponse(content, mimetype='application/pdf')
    if filename is not None:
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

def render_to_pdf(request, template, context, filename=None, encoding='utf-8', 
    **kwargs):
    """
    Render a pdf response using given *request*, *template* and *context*.
    """
    if not isinstance(context, Context):
        context = RequestContext(request, context)

    content = loader.render_to_string(template, context)
    buffer = StringIO()

    content = content_to_pdf(content, encoding, **kwargs)
    return content_to_response(content, filename)

class PDFTemplateResponseMixin(TemplateResponseMixin):
    """
    Mixin for Django class based views.
    Switch normal and pdf template based on request.

    The switch is made when the request has a particular querydict, e.g.::

        http://www.example.com?format=pdf

    The key and value of the querydict can be overridable using *as_view()*.
    That pdf url will be present in the context as *pdf_url*.

    For example it is possible to define a view like this::
        
        from django.views.generic import View

        class MyView(PDFTemplateResponseMixin, View):
            template_name = 'myapp/myview.html'
            pdf_filename = 'report.pdf'

    The pdf generation is automatically done by *xhtml2pdf* using
    the *myapp/myview_pdf.html* template.

    Note that the pdf template takes the same context as the normal template.
    """
    pdf_template_name = None
    pdf_template_name_suffix = ''
    pdf_querydict_key = 'format'
    pdf_querydict_value = 'pdf'
    pdf_encoding = 'utf-8'
    pdf_filename = None
    pdf_url_varname = 'pdf_url'
    pdf_kwargs = {}

    standalone_view = False # If this mixin is not combined with a DetailView

    def is_pdf(self):
        if self.standalone_view:
            return True
        value = self.request.REQUEST.get(self.pdf_querydict_key, '')
        return value.lower() == self.pdf_querydict_value.lower()

    def _get_pdf_template_name(self, name):
        base, ext = os.path.splitext(name)
        return '%s%s%s' % (base, self.pdf_template_name_suffix, ext)

    def get_pdf_template_names(self):
        """
        If the template name is not given using the class attribute
        *pdf_template_name*, then it is obtained using normal template
        names, appending *pdf_template_name_suffix*, e.g.::

            path/to/detail.html -> path/to/detail_pdf.html
        """
        if self.pdf_template_name is None:
            names = super(PDFTemplateResponseMixin, self).get_template_names()
            return map(self._get_pdf_template_name, names)
        return [self.pdf_template_name]

    def get_pdf_filename(self):
        """
        Return the pdf attachment filename.
        If the filename is None, the pdf will not be an attachment.
        """
        return self.pdf_filename

    def get_pdf_url(self):
        """
        This method is used to put the pdf url in the context.
        """
        querydict = self.request.GET.copy()
        querydict[self.pdf_querydict_key] = self.pdf_querydict_value
        return '%s?%s' % (self.request.path, querydict.urlencode())

    def get_pdf_response(self, context, **response_kwargs):
        return render_to_pdf(
            request=self.request,
            template=self.get_pdf_template_names(),
            context=context,
            encoding=self.pdf_encoding,
            filename=self.get_pdf_filename(),
            **self.pdf_kwargs
        )

    def render_to_response(self, context, **response_kwargs):
        if self.is_pdf():
            from django.conf import settings
            context['STATIC_ROOT'] = settings.STATIC_ROOT
            return self.get_pdf_response(context, **response_kwargs)
        context[self.pdf_url_varname] = self.get_pdf_url()
        return super(PDFTemplateResponseMixin, self).render_to_response(
            context, **response_kwargs)
