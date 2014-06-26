def get_pleb_posts(pleb_object):
    post_array = []
    try:
        pleb_posts = pleb_object.traverse('posts').run()
        for item in pleb_posts:
            post_dict = {'content': item.content, 'post_id': item.post_id}
            post_array.append(post_dict)
        return post_array
    except:
        print "You have no posts!"
