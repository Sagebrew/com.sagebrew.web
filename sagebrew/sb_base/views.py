from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (RetrieveUpdateDestroyAPIView)

from .neo_models import SBContent


class ObjectRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return SBContent.nodes.get(
            object_uuid=self.kwargs[self.lookup_url_kwarg])

    def perform_destroy(self, instance):
        instance.content = ""
        instance.to_be_deleted = True
        instance.save()
        return instance