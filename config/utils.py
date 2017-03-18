def neo_node(neo_result):
    """
    Takes the results of a cypher query and formalizes it into a standard
    format. If there is no result then we return None. If there is a
    result we return a Node. This should not be used when you are expecting
    back a group of nodes, aka when you're attempting to do something like:
    [Pleb.inflate(row[0]) for row in res].

    :param neo_result:
    :return:
    """
    result = neo_result[0] if neo_result else None
    if result is not None:
        return result[0] if result else None
    else:
        return None
