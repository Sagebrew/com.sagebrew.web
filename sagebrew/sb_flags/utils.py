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
                                "exception": "UnhandledException: "}))
        return e