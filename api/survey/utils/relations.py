from django.urls.base import resolve

from rest_framework import serializers


class ModelRelaitedField(serializers.RelatedField):
    def __init__(self, serializer_class, **kwargs):
        self.serializer_class: serializers.Serializer = serializer_class
        assert self.serializer_class != None, "Serializer wasn't provided."
        assert not isinstance(
            self.serializer_class, serializers.Serializer), "Provided class isn't Serializer."
        super().__init__(**kwargs)

    def to_representation(self, value):
        return self.serializer_class(value, context={'request': self.context["request"]}).data

    def to_internal_value(self, data):
        assert isinstance(data, str), f"Unsupported data type (type: {type(data)})"
        def strip_domain_url(absolute_url: str) -> str:
            """Function provide domain striped url. It's based on that domain always placed between 2'th and 3'th '/' letters."""
            return absolute_url.split(absolute_url.split('/')[2])[1]
        resolved_data = resolve(strip_domain_url(data))
        return self.get_queryset().get(pk=resolved_data.kwargs["pk"])
