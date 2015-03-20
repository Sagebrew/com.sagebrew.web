import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UnicodeSetAttribute


class SolutionModel(Model):
    class Meta:
        table_name = '%s-public_solutions' % os.environ.get(
            "CIRCLE_BRANCH", "unknown").replace('/', '-')
        read_capacity_units = 1
        write_capacity_units = 1
    # Question that Solution is on
    parent_object = UnicodeAttribute(hash_key=True)
    object_uuid = UnicodeAttribute(range_key=True)
    content = UnicodeAttribute()
    last_edited_on = UnicodeAttribute()
    up_vote_number = UnicodeAttribute()
    down_vote_number = UnicodeAttribute()
    object_vote_count = UnicodeAttribute()
    solution_owner_name = UnicodeAttribute()
    solution_owner_url = UnicodeAttribute()
    time_created = UnicodeAttribute()
    comments = UnicodeAttribute()
    solution_owner_email = UnicodeAttribute()
    edits = UnicodeSetAttribute()
    object_type = UnicodeAttribute()
    html_content = UnicodeAttribute()