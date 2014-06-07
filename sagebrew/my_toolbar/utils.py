from fnmatch import fnmatch

def custom_show_toolbar(request):
    if(fnmatch(request.path.strip(), '/admin*')):
        return False
    elif(fnmatch(request.path.strip(), '/secret/*')):
        return False
    return True # Always show toolbar, for example purposes only.
