from django.http import QueryDict
from rest_framework import serializers


class ExposedComputationWrapper(serializers.Serializer):
    output_field_names = None

    def __init__(self, only_input_parameter=False, **kwargs):
        if only_input_parameter:
            output_field_names = [key for key, field in self.fields.items() if field.read_only]
            for output_field_name in output_field_names:
                del self.fields[output_field_name]
        super(ExposedComputationWrapper, self).__init__(**kwargs)

    def create(self, validated_data):
        # never called when used with ExposedComputationView
        pass

    def update(self, instance, validated_data):
        # never called when used with ExposedComputationView
        pass

    def run_computation(self, request, data, *args, **kwargs):
        raise NotImplementedError(
            "%s must implement run_computation method and return a dict containing all "
            "the results, i.e fields with read_only=True." % self.__class__.__name__
        )

    def evaluate_computation_feasibility(self, request, data, *args, **kwargs):
        raise NotImplementedError(
            "%s must implement evaluate_computation_feasibility method" % self.__class__.__name__
        )
