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
        def get_domain_url(url: str) -> str:
            return url.split('/')[2]
        absolute_url = data.split(get_domain_url(data))[1]
        resolved_data = resolve(absolute_url)
        return self.get_queryset().get(pk=resolved_data.kwargs["pk"])
