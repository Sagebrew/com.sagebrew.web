from .neo_models import SBComment
from sb_posts.neo_models import SBPost

from plebs.neo_models import Pleb
from .tasks import create_upvote_comment, create_downvote_comment


def get_post_comments(post_info):
    comment_array = []
    post_array = []
    for post in post_info:
        post_comments = post.traverse('comments').run()
        #TODO Get which user posted the comment
        for comment in post_comments:
            comment_dict = {'comment_content': comment.content, 'comment_id': comment.comment_id, 'comment_up_vote_number': comment.up_vote_number, 'comment_down_vote_number': comment.down_vote_number,'comment_last_edited_on': comment.last_edited_on}#, 'comment_posted_by': comment.is_owned_by}
            comment_array.append(comment_dict)
        post_dict = {'content': post.content, 'post_id': post.post_id, 'up_vote_number': post.up_vote_number, 'down_vote_number': post.down_vote_number, 'last_edited_on': post.last_edited_on, 'comments': comment_array}
        post_array.append(post_dict)
        comment_array = []
    return post_array

def create_comment_vote(comment_info):
    my_pleb = Pleb.index.get(email = comment_info['pleb'])
    my_comment = SBComment.index.get(comment_id = comment_info['comment_uuid'])
    if my_comment.up_voted_by.is_connected(my_pleb) or my_comment.down_voted_by.is_connected(my_pleb):
        print "You have voted already!"
        return
    else:
        if comment_info['vote_type'] == 'up':
            create_upvote_comment.apply_async([comment_info,])
            print "Thanks for voting"
        elif comment_info['vote_type'] == 'down':
            create_downvote_comment.apply_async([comment_info,])
            print "Thanks for voting"