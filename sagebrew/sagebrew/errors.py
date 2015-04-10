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