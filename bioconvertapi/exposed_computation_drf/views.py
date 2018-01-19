from django.http import QueryDict
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from bioconvertapi.exposed_computation_drf.wrappers import ExposedComputationWrapper


class ExposedComputationView(GenericAPIView):

    def get_serializer_class(self):
        assert issubclass(self.serializer_class, ExposedComputationWrapper), (
                "'%s' should either include a `serializer_class` attribute, "
                "or override the `get_serializer_class()` method that return a "
                "serialzer inheriting from ExposedComputationSerializer."
                % self.__class__.__name__
        )
        return super(ExposedComputationView, self).get_serializer_class()

    def post(self, request, *args, **kw):
        serializer = self.get_serializer(data=request.data)
        # print(request.data)
        if serializer.is_valid():
            # print("b")

            validated_data = dict(
                list(serializer.validated_data.items()) +
                list(kw.items())
            )

            # do the computation
            results_as_dict = serializer.run_computation(request=request, data=validated_data)

            results = QueryDict('', mutable=True)
            # results.update(validated_data)
            results.update(results_as_dict)

            # serialize the input parameter and the results
            serializer = self.get_serializer(instance=results, data=results)
            # Are the results compliante as declare in the serializer ?
            if serializer.is_valid():
                # return parameter and results
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kw):
        serializer = self.get_serializer()
        evaluation = serializer.evaluate_computation_feasibility(request=request, data=dict(
            list(request.data.items()) +
            list(kw.items())
        ))
        return Response(evaluation or {}, status=status.HTTP_200_OK)
