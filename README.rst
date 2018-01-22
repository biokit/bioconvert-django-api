================================
Bioconvert API
================================

.. image:: https://badge.fury.io/py/bioconvert-django-api.svg
    :target: https://pypi.python.org/pypi/bioconvert-django-api

.. image:: https://secure.travis-ci.org/biokit/bioconvert-django-api.png
    :target: http://travis-ci.org/biokit/bioconvert-django-api

A Django app using `django-rest-framwork`_ to propose bioconvert_ convertion through a REST API


Quick start
-----------

1.
Add "rest_framework" and then the "bioconvertapi" to your INSTALLED_APPS setting like this:
::

    INSTALLED_APPS = [
        ...
        'rest_framework',
        'bioconvertapi',
    ]

2.
Include the bioconvertapi URLconf in your project urls.py and serve the media directory like this:
::

    urlpatterns = [
        ...
        url(r'^bioconvert-api/', include('bioconvertapi.urls')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



3.
Visit http://127.0.0.1:8000/bioconvert-api/fastq/fasta/ to convert from fastq to fasta

.. _bioconvert: https://github.com/biokit/bioconvert
.. _django-rest-framwork: http://www.django-rest-framework.org/
