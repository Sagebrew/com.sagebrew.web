from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from neomodel import DoesNotExist

from sb_registration.utils import verify_completed_registration

from .neo_models import Update
from .serializers import UpdateSerializer


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def edit_update(request, object_uuid=None):
    try:
        update = Update.nodes.get(object_uuid=object_uuid)
    except (Update.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    return render(request, 'create_update.html', UpdateSerializer(update).data)
