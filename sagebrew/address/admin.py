from django.contrib import admin
from models import Address


class AddressAdmin(admin.ModelAdmin):
    'Admin interface for Address Model'
    list_display = ('street', 'city', 'state',
        'postal_code', 'country')
    list_filter = ('state',)

admin.site.register(Address, AddressAdmin)
