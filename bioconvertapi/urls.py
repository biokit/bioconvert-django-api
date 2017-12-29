# Create your views here.
from django.conf.urls import url

# Routers provide an easy way of automatically determining the URL conf.
from bioconvertapi.views import BioconvertView, BioconvertConversionView

app_name = 'bioconvertapi'
urlpatterns = [
    url(r'^$', BioconvertConversionView.as_view(),dict(input_format=None), name='bioconvert_io'),
    url(r'^(?P<input_format>\w+)/$', BioconvertConversionView.as_view(), name='bioconvert_io_for_input'),
    url(r'^(?P<input_format>\w+)/(?P<output_format>\w+)/$', BioconvertView.as_view(), name='bioconvert'),
]
