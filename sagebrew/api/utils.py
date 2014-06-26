from json import loads

def get_post_data(request):
    try:
        post_info = loads(request.body)
    except(ValueError):
        post_info = request.DATA
    return post_info