from sb_posts.utils import delete_post_info
from sb_comments.utils import delete_comment_util

# TODO add logging for not deleted items


def delete_posts_util(garbage_can):
    posts = garbage_can.posts.all()
    for post in posts:
        delete_post_info(post.post_id)


def delete_comments_util(garbage_can):
    comments = garbage_can.comments.all()
    for comment in comments:
        delete_comment_util(comment.comment_id)