import logging
from django.template.loader import render_to_string

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .forms import GetNotificationForm
from api.utils import get_post_data
from plebs.neo_models import Pleb

logger = logging.getLogger('loggly_logs')

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def create_notification(request):
    pass


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_notifications(request):
    '''
    When this api is hit it will take a users email address and a number,
    it will then get the most recent notifications up to that number that
    have the attribute seen==False

    :param request:
    :return:
    '''
    try:
        notification_array = []
        notification_data = get_post_data(request)
        if (type(notification_data) != dict):
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        notification_form = GetNotificationForm(notification_data)
        if notification_form.is_valid():
            citizen = Pleb.index.get(email=notification_form.cleaned_data['email'])
            notifications = citizen.traverse('notifications').where('seen', '=',
                    False).order_by_desc('time_sent').skip(
                    notification_form.cleaned_data['range_start']).limit(
                    notification_form.cleaned_data['range_end']).run()

            for notification in notifications:
                from_user = notification.traverse('notification_from').run()[0]
                notification_dict = {'notification_about': notification.notification_about,
                        'time_sent': notification.time_sent,
                        'from_user': from_user.first_name+' '+from_user.last_name,
                        'notification_about_id': notification.notification_about_id}
                notification_array.append(notification_dict)
                notification_dict = {}
            html  = render_to_string('notifications.html', notification_array)
            return Response({'html': html}, status=200)
        else:
            return Response(status=400)
    except Exception:
        logger.exception("UnhandledException: ")
        return Response(status=400)





