import asyncio

from mergify_algos.github.clients import GitHubRestClient, GitHubGraphQLClient


# -----------------------------------------------------------------------------
# Algo shared utils
def _transform_user_starred_repositories(dict, exclude_repos=None):
    """Swap keys and items.
    Turn the dict {"user": ["repos"]} to dict {"repo": ["users"]}
    """
    results = {}

    if exclude_repos is None:
        exclude_repos = []

    # blong: Here can we use pandas or numpy to speed-up CPU process
    # Do we want to add the dependency
    for user in dict:
        for repo in dict[user]:
            if repo in exclude_repos:
                continue

            results.setdefault(repo, [])

            # Flip repo and user
            results[repo].append(user)

    return results


def _compute_and_order_neighbours(repo_user_map, users_threshold=2):
    """Format & sort the dict {"repo": ["users"]}"""
    results = []

    # Recover only repository with more than `users_threshold` in-common users
    for r, users in repo_user_map.items():
        if len(users) < users_threshold:
            continue

        results.append(
            {"repo": r, "stargazers_count": len(users), "stargazers": list(users)}
        )

    # Sort
    sorted_results = sorted(results, key=lambda x: x["stargazers_count"], reverse=True)
    return results, sorted_results


# -----------------------------------------------------------------------------
# Algo using GitHub Rest API
def find_neighbour_repos(
    owner: str, repo: str, token: str, limit_pages: int = 2, threshold: int = 2
):
    """Find repositories that share stargazers with the given repository.
    Brut synchronize implementation...

    1- Construct stargazers dictionary
    1.a Fetch repository's stargazers
    1.b For each stargazer, fetch its starred repository.
    Because fetching information from GitHub API will eventually take lots of
    time, we have limit_pages parameters.
    TODO: Should we limit the number of stargazers?
    2- Swap dictionary
    3- Compute neighbours count and order results

    :param owner: GitHub repo's owner.
    :param repo: GitHub repo's name.
    :param token: GitHub access token.
    :param limit_pages: Limit the number of page the algo use to fetch data.
    :param threshold: Only return repository with more than 'n' common user
    :returns neighbour_repos: Sorted List of repository neighbour of {owner}/{repo}
    """
    # Init data structure used by neighbour algorithm and Github client
    user_repo_map = {}
    gh_client = GitHubRestClient(token=token)

    # Fetch repository's stargazers
    repo_stargazers = gh_client.fetch_stargazers(
        owner=owner,
        repo=repo,
        limit_pages=limit_pages,
    )

    # For each stargazer, fetch user's starred repositories
    for stargazer in repo_stargazers:
        # Sorting by desc `updated` attribute to have active repositories first
        _stargazer_starred_repos = gh_client.fetch_user_starred_repos(
            user=stargazer,
            params={"sort": "updated", "direction": "desc"},
            limit_pages=limit_pages,
        )
        user_repo_map[stargazer] = _stargazer_starred_repos

    # Revert the user_repo_map dictionary to be "repo" listing in-common "users"
    repo_user_map = _transform_user_starred_repositories(
        user_repo_map, exclude_repos=[f"{owner}/{repo}"]
    )

    # Compute neighbours and sort result
    results, sorted_results = _compute_and_order_neighbours(
        repo_user_map, users_threshold=threshold
    )

    return results, sorted_results


async def afind_neighbour_repos(
    owner: str, repo: str, token: str, limit_pages: int = 2, threshold: int = 2
):
    """Aysnc implementation of `find_neighbour_repos`

    :param owner: GitHub repo's owner.
    :param repo: GitHub repo's name.
    :param token: GitHub access token.
    :param limit_pages: Limit the number of page the algo use to fetch data.
    :param threshold: Only return repository with more than 'n' common user
    :returns neighbour_repos: Sorted List of repository neighbour of {owner}/{repo}

    Simple Async implementation to speed up fetching user's starred repositories

    Idea to improve/speed up algorithm:
    Start fetch first 100 stargezers, when complete start fetch user's starred
    repositories, then second 100 stargezers, when complete add async tasks
    to fetch newly added user's starred repositories. Ect...
    using asyncio.as_completed
    """
    # Init data structure used by neighbour algorithm and Github Client
    gh_client = GitHubRestClient(token=token)

    # Fetch repository's stargazers
    repo_stargazers = gh_client.fetch_stargazers(
        owner=owner,
        repo=repo,
        limit_pages=limit_pages,
    )

    # Fetch stargazers' starred repositories concurrently
    # Batch process 25 stargazers at a time. When doing all stargazers at once
    # We reach httpx TimeOut.
    index = 0
    batch = 25
    max_index = len(repo_stargazers)
    user_repo_map = {}
    while index <= max_index:
        end_index = min(index + batch, max_index)
        tmp_stargazers = repo_stargazers[index:end_index]
        coroutines = (
            gh_client.afetch_user_starred_repos(stargazer)
            for stargazer in tmp_stargazers
        )
        tmp_results = await asyncio.gather(*coroutines)
        tmp_dict = dict(zip(tmp_stargazers, tmp_results))
        user_repo_map.update(tmp_dict)
        index = end_index + 1

    # Fetch stargazers' starred repositories concurrently
    # coroutines = (
    #     gh_client.afetch_user_starred_repos(stargazer) for stargazer in repo_stargazers
    # )
    # results = await asyncio.gather(*coroutines)

    # Map the results
    # user_repo_map = dict(zip(repo_stargazers, results))

    # Revert the user_repo_map dictionary to be "repo" listing in-common "users"
    repo_user_map = _transform_user_starred_repositories(
        user_repo_map, exclude_repos=[f"{owner}/{repo}"]
    )

    # Compute neighbours and sort result
    results, sorted_results = _compute_and_order_neighbours(
        repo_user_map, users_threshold=threshold
    )

    return results, sorted_results


# -----------------------------------------------------------------------------
# Algo using GitHub GraphQL API
def find_graphql_neighbour_repos(owner: str, repo: str, token: str, threshold: int = 2):
    # Init data structure used by neighbour algorithm and Github Client
    gh_client = GitHubGraphQLClient(token=token)

    # Fetch repository's stargazers and their related first starred repositories
    user_repo_map = gh_client.fetch_stargazers_with_starred_repos(
        owner=owner, repo=repo
    )

    # Revert the user_repo_map dictionary to be "repo" listing in-common "users"
    repo_user_map = _transform_user_starred_repositories(
        user_repo_map, exclude_repos=[f"{owner}/{repo}"]
    )

    # Compute neighbours and sort result
    results, sorted_results = _compute_and_order_neighbours(
        repo_user_map, users_threshold=threshold
    )

    return results, sorted_results
