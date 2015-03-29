def determine_update_values(prev_status, update_status, upvote_value,
                            downvote_value):
    if update_status==2 and prev_status==1:
        upvote_value -= 1
    elif update_status==2 and prev_status==0:
        downvote_value -= 1
    elif update_status==1 and prev_status==0:
        downvote_value -= 1
        upvote_value += 1
    elif update_status==0 and prev_status==1:
        downvote_value += 1
        upvote_value -= 1
    elif update_status==1 and prev_status==2:
        upvote_value += 1
    elif update_status==0 and prev_status==2:
        downvote_value += 1
    return upvote_value, downvote_value
