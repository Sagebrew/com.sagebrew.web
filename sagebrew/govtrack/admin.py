from django.contrib import admin
from govtrack.models import SRole , Person , GTBill , GTVotes

admin.site.register(SRole)
admin.site.register(Person)
admin.site.register(GTBill)
admin.site.register(GTVotes)