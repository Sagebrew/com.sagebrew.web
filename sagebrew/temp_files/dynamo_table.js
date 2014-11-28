[
    {
        "table_name": "users_full",
        "hash_key": "email"
    },
    {
        "table_name": "comments",
        "hash_key": "parent_object",
        "range_key": "object_uuid"
    },
    {
        "table_name": "votes",
        "hash_key": "parent_object"
    },
    {
        "table_name": "users_barebones",
        "hash_key": "email"
    },
    {
        "table_name": "friends",
        "hash_key": "email"
    },
    {
        "table_name": "private_questions",
        "hash_key": "object_uuid"
    },
    {
        "table_name": "private_solutions",
        "hash_key": "parent_object",
        "range_key": "object_uuid"
    },
    {
        "table_name": "public_questions",
        "hash_key": "object_uuid"
    },
    {
        "table_name": "public_solutions",
        "hash_key": "parent_object",
        "range_key": "object_uuid"
    },
    {
        "table_name": "posts",
        "hash_key": "object_uuid"
    },
    {
        "table_name": "news_feed",
        "hash_key": "email"
    },
    {
        "table_name": "flags",
        "hash_key": "parent_object"
    },
    {
        "table_name": "notifications",
        "hash_key": "email"
    },
    {
        "table_name": "location",
        "hash_key": "state",
        "range_key": "district"
    },
    {
        "table_name": "house_reps",
        "hash_key": "email",
        "range_key": "state",
        "local_index": "district"
    },
    {
        "table_name": "senators",
        "hash_key": "email",
        "range_key": "state"
    }]