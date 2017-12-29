import json
import os
from urllib import request as urllib

from bioconvert.core.registry import Registry
from bioconvert.scripts.converter import main as bioconvert_main
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.fields import empty

from bioconvertapi.exposed_computation_drf.wrappers import ExposedComputationWrapper


class BioconvertWrapper(ExposedComputationWrapper):
    input_file = serializers.FileField(
        required=False,
    )

    input_url = serializers.URLField(
        required=False,
    )
    identifier = serializers.CharField(
        min_length=32,
        max_length=32,
        required=False,
    )
    output_url = serializers.URLField(read_only=True)

    def run_validation(self, data=empty):
        value = super(BioconvertWrapper, self).run_validation(data)
        if data is empty:
            raise self.get_validation_error()
        provided_params = (1 if 'input_file' in data and data['input_file'] != '' else 0) + \
                          (1 if 'input_url' in data and data['input_url'] != '' else 0) + \
                          (1 if 'identifier' in data and data['identifier'] != '' else 0)
        if provided_params != 1:
            raise self.get_validation_error()
        return value

    @staticmethod
    def get_validation_error():
        return ValidationError(detail={
            'input_file': ['Either provide a input_url, identifier or input_file', ],
            'input_url': ['Either provide a input_url, identifier or input_file', ],
            'identifier': ['Either provide a input_url, identifier or input_file', ],
        })

    def run_computation(self, request, data, *args, **kwargs):
        # settings
        input_format = data.get("input_format", "").lower()
        output_format = data.get("output_format", "").lower()
        identifier = data.get("identifier", get_random_string(length=32))
        job_dir = os.path.join('converted', identifier)

        # Fetching file if new job, or getting its information
        content = None
        if 'input_file' in data:
            input_filename = data['input_file'].name
            content = data['input_file'].read()
        elif 'input_url' in data:
            input_filename = data['input_url'][data['input_url'].rindex('/') + 1:]
            response = urllib.urlretrieve(data['input_url'])
            content = open(response[0]).read()
        elif 'identifier' in data:
            try:
                job_info = json.loads(
                    default_storage.open(
                        os.path.join(job_dir, "job_info.json"),
                    ).read()
                )
            except FileNotFoundError:
                raise NotFound()
            if job_info['owner'] != request.user.pk:
                # raise PermissionDenied()
                raise NotFound()
            input_filename = job_info["input_filename"]
        else:
            raise self.get_validation_error()

        # building paths
        path = os.path.join(job_dir, input_filename)
        input_path = os.path.join(settings.MEDIA_ROOT, path)
        output_path = input_path + "." + output_format

        if content:
            # saving fetched file
            default_storage.save(path, ContentFile(content))

            bioconvert_main(args=[
                input_path,
                output_path,
            ])

            # save
            job_info = dict(
                owner=request.user.pk,
                output_path=output_path,
                input_filename=input_filename,
                input_format=input_format,
                output_format=output_format,
            )
            default_storage.save(
                os.path.join(job_dir, "job_info.json"),
                ContentFile(json.dumps(job_info)),
            )
        return dict(
            output_url=request.build_absolute_uri(os.path.join(settings.MEDIA_URL, path + "." + output_format)),
            identifier=identifier,
        )

    def evaluate_computation_feasibility(self, request, data, *args, **kwargs):
        mapper = Registry()
        # conversions = {}
        computation_feasible = False
        for k in sorted(mapper.get_conversions()):
            # if k[0] in conversions:
            #     to = conversions[k[0]]
            # else:
            #     to = []
            #     conversions[k[0]] = to
            # to.append(k[1])
            computation_feasible = \
                computation_feasible or \
                data['input_format'].upper() == k[0] and data['output_format'].upper() == k[1]

        if not computation_feasible:
            raise NotFound(detail='Requested conversion not available')

        # return conversions
