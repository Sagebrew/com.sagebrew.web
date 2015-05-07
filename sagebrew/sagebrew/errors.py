from rest_framework import status

CYPHER_EXCEPTION = {
    "detail": "Error connecting to the database",
    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
    "developer_message":
        "We've run into an issue while attempting to query the database. This "
        "is usually resolved with a subsequent retry query. Please visit "
        "https://api.sagebrew.com/docs/CypherException/ for additional "
        "information"
}

DYNAMO_TABLE_EXCEPTION = {
    "detail": "Error connecting to the document store",
    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
    "developer_message":
        "We've run into an issue while attempting to query the document store. "
        "This  is usually resolved with a subsequent retry query. Please visit "
        "https://api.sagebrew.com/docs/DocStoreException/ for additional "
        "information"
}

CYPHER_INDEX_EXCEPTION = {
    "detail": "Error connecting to the database",
    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
    "developer_message":
        "We've run into an issue while attempting to query the database. This "
        "is usually resolved with a subsequent retry query. Please visit "
        "https://api.sagebrew.com/docs/CypherException/ for additional "
        "information"
}

QUERY_DETERMINATION_EXCEPTION = {
    "detail": "Sorry we didn't understand that filter query.",
    "status": status.HTTP_400_BAD_REQUEST,
    "developer_message":
        "We currently have limited support for filter operations. "
        "We also haven't had a chance to document them yet :/. But once we do "
        "we'll provide a link here to reference. In the mean time please feel "
        "free to reach out to us via the intercom or send us a note at "
        "developers@sagebrew.com."
}

JSON_ERROR_EXCEPTION = {
    "detail": "Sorry looks like we're having some difficulty with making "
              "some requests.",
    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
    "developer_message":
        "We are currently experiencing some difficulties making requests."
        " This is often times caused by an unexpected large increase in "
        "load. We're alerted of these increases and are working to "
        "alleviate the issue."
}

DOES_NOT_EXIST_EXCEPTION = {
    "detail": "Sorry this object does not exist.",
    "status": status.HTTP_404_NOT_FOUND,
    "developer_message":
        "This object currently does not exist in our database. If you believe "
        "this is incorrect please feel free to contact us at "
        "developers@sagebrew.com."
}
