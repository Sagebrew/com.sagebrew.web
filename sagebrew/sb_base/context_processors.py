import json
def js_settings(request):

    data = {}
    data['user'] = {}

    if request.user.is_authenticated():
        data['user']['type'] = "auth"
        data['user']['username'] = request.user.username
    else:
        data['user']['type'] = "anon"

    settings = "var SB_APP_SETTINGS = "
    settings += json.dumps(data)
    settings += ";"
    return {
        'js_settings': settings,
    }