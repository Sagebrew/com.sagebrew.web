import logging
from json import dumps
from django.template.loader import render_to_string

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .neo_models import NotificationBase
from .forms import GetNotificationForm
from api.utils import execute_cypher_query

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
        notification_data = request.DATA
        if (type(notification_data) != dict):
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        notification_form = GetNotificationForm(notification_data)

        if notification_form.is_valid():
            query = 'match (p:Pleb) where p.email="%s" ' \
                'with p ' \
                'match (p)-[:RECEIVED_A]-(n:NotificationBase) ' \
                'where n.seen=False ' \
                'with p, n ' \
                'order by n.time_sent desc ' \
                'with n skip %s limit %s return n' % (
            notification_form.cleaned_data['email'],
            str(notification_form.cleaned_data['range_start']),
            str(notification_form.cleaned_data['range_end']))

            notifications, meta = execute_cypher_query(query)
            notifications = [NotificationBase.inflate(row[0]) for row in notifications]
            for notification in notifications:
                from_user = notification.notification_from.all()[0]
                notification_dict = {'notification_about': notification.notification_about,
                        'time_sent': notification.time_sent,
                        'from_user': from_user.first_name+' '+from_user.last_name}
                notification_array.append(notification_dict)
                notification_dict = {}
            html  = render_to_string('notifications.html', notification_array)
            return Response({'html': html}, status=200)
        else:
            return Response(status=400)
    except Exception:
        logger.exception(dumps({"function": get_notifications.__name__,
                                "excpetion": "UnhandledException: "}))
        return Response(status=400)





