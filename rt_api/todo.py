def live(self, page=1, count=20):
    path = "live/"
    url = os.path.join(END_POINT, path)
    params = {
        "page": page,
        "count": count
    }
    data = self.__get_data(url, params=params)
    # TODO


def search(self, query, filter=[]):
    """

    Args:
        query (str):
        filter:  (Default value = []).

    Returns:
        Filter should be a list of types to return.

    """
    # TODO create a SearchResult model?
    url = os.path.join(END_POINT, "search/?q={0}".format(query))
    data = self.__get_data(url)
    results = {}
    if models.Episode in filter:
        try:
            episodes = data[0]["episodes"]
            results["episodes"] = []
            for episode_data in episodes:
                results["episodes"].append(models.Episode(episode_data, self))
        except KeyError:
            # No episodes in search result
            pass
    try:
        data[1]["groups"]
    except KeyError:
        # No groups in search result
        pass
    return results
