from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (RetrieveUpdateDestroyAPIView)


class ObjectRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def perform_destroy(self, instance):
        instance.content = ""
        instance.to_be_deleted = True
        instance.save()
        return instance