import logging
from json import dumps

logger = logging.getLogger("loggly_logs")


def flag_object_util(current_pleb, sb_object, flag_reason):
    '''
    This function takes a pleb object,
    sb_object(SBAnswer, SBQuestion, SBComment, SBPost), and a flag reason.
    It will then apply a flag to the object based upon the flag reason given.

    :param current_pleb:
    :param sb_object:
    :param flag_reason:
    :return:
    '''
    # TODO can we move acceptable flag reasons to the actual object
    # Example SBPost would have an array associated with the variable
    # flags that we could iterate through here after gathering the actual
    # object. Then up the count on the given counter.
    # That way we have more flexibility over what things can get flagged for.
    # Potentially could also have a standard list of flags associated with the
    # base models and then if there are additional ones or ones that don't
    # apply modify it in the model that rule is applicable to.
    try:
        if flag_reason not in sb_object.allowed_flags:
            return False

        if sb_object.flagged_by.is_connected(current_pleb):
            return True

        sb_object.flagged_by.connect(current_pleb)
        if flag_reason == "spam":
            sb_object.flagged_as_spam_count += 1
        elif flag_reason == "explicit":
            sb_object.flagged_as_explicit_count += 1
        elif flag_reason == "other":
            sb_object.flagged_as_other_count += 1
        elif flag_reason == "unsupported":
            sb_object.flagged_as_unsupported_count += 1
        elif flag_reason == "duplicate":
            sb_object.flagged_as_duplicate_count += 1
        elif flag_reason == "changed":
            sb_object.flagged_as_changed += 1
        else:
            return False

        sb_object.save()
        return True

    except Exception as e:
        logger.exception(dumps({"function": flag_object_util.__name__,
                                "exception": "Unhandled Exception"}))
        return e