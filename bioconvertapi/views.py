from bioconvert.core.registry import Registry
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from bioconvertapi.exposed_computation_drf.views import ExposedComputationView
from bioconvertapi.wrappers import BioconvertWrapper


class BioconvertView(ExposedComputationView):
    """
    REST API wrapping bioconvert possible conversion
    """
    permission_classes = (AllowAny,)
    serializer_class = BioconvertWrapper


class BioconvertConversionView(GenericAPIView):
    """
    Conversions proposed by bioconvert
    """
    def get(self, request, input_format, *args, **kw):
        mapper = Registry()
        conversions = {}
        for k in sorted([k for k in mapper.get_conversions() if input_format is None or k[0].upper() == input_format]):
            if k[0] in conversions:
                to = conversions[k[0]]
            else:
                to = dict(
                    url=request.build_absolute_uri(
                        reverse(
                            'bioconvertapi:bioconvert_io_for_input',
                            kwargs=dict(
                                input_format=k[0],
                            ),
                        )),
                    output=[],
                )
                conversions[k[0]] = to
            to["output"].append(
                dict(
                    url=request.build_absolute_uri(
                        reverse(
                            'bioconvertapi:bioconvert',
                            kwargs=dict(
                                input_format=k[0],
                                output_format=k[1],
                            ),
                        )),
                    format=k[1],
                )
            )
        return Response(conversions or {}, status=status.HTTP_200_OK)
