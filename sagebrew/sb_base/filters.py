from rest_framework import filters


class MostRecentFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return sorted(queryset, key=lambda k: k.created, reverse=True)