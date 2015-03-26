from django.template.loader import render_to_string

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from neomodel import CypherException

from api.utils import execute_cypher_query
from sb_docstore.utils import get_notification_docs

from .neo_models import NotificationBase
from .forms import GetNotificationForm


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
    notification_data = request.DATA
    notification_array = []
    if (type(notification_data) != dict):
        return Response({"details": "Please Provide a JSON Object"}, status=400)
    try:
        notification_form = GetNotificationForm(notification_data)
        valid_form = notification_form.is_valid()
    except AttributeError:
        return Response({"details": "Invalid Form"}, status=400)
    if valid_form:
        html_array = []
        res = get_notification_docs(request.user.username)
        if isinstance(res, Exception):
            return Response({"detail": "fail"}, status=400)
        if not res:
            query = 'match (p:Pleb) where p.username="%s" ' \
                'with p ' \
                'match (p)-[:RECEIVED_A]-(n:NotificationBase) ' \
                'where n.seen=False ' \
                'with p, n ' \
                'order by n.time_sent desc ' \
                'with n skip %s limit %s return n' % (
                request.user.username,
                str(notification_form.cleaned_data['range_start']),
                str(notification_form.cleaned_data['range_end']))
            try:
                notifications, meta = execute_cypher_query(query)
            except CypherException:
                return Response(status=500)
            notifications = [NotificationBase.inflate(row[0])
                             for row in notifications]
            for notification in notifications:
                from_user = notification.notification_from.all()[0]
                notification_dict = {'about': notification.about,
                        'time_sent': notification.time_sent,
                        'from_user': from_user.first_name+' '+from_user.last_name}
                notification_array.append(notification_dict)
            html = render_to_string('notifications.html', notification_array)
        else:
            for notification in res:
                html_array.append(render_to_string('notification_detail.html',
                    {"notification": notification}))
            print html_array
            html = render_to_string('notification_detail.html',
                                    {'notifications': res})
        return Response({'html': html}, status=200)
    else:
        return Response(status=400)
