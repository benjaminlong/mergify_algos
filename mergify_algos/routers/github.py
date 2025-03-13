from fastapi import APIRouter

from mergify_algos import github
from mergify_algos.config import settings
from mergify_algos.utils import display_secret


router = APIRouter(
    prefix="/github",
    tags=["github"],
    # dependencies=[Depends(get_github_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/repos/{owner}/{repo}")
async def compute_starneighbours(
    owner: str,
    repo: str,
    limit_pages: int = 2,
    threshold: int = 1,
    use_async: bool = True,
    gh_token: str = None,
):
    """Compute Star neighbours API. Using Github Rest API.

    WARNING: Computation eventually take lots of time. Do we use a background task
    and provide a different API to get the results when available ?
    Which means we need a db to save requested computation and results.

    :param owner: Github's repository owner
    :param repo: Github's repository name
    :param limit_pages: Only Fetch 'n' page from GitHub paginated API. Limit
    the results but speed up the process.
    :param use_async: True use async algorithm, False use sequential algorithm.
    :param threshold: Only return repository with more than 'n' common user
    :param gh_token: Override App Github Token
    :return: List of GitHub Repository
    """
    # If no gh_token provided, try to use the App GitHub token from the settings
    if gh_token is None:
        gh_token = settings.github_token

    if use_async:
        results, sorted_results = await github.afind_neighbour_repos(
            owner=owner,
            repo=repo,
            token=gh_token,
            limit_pages=limit_pages,
            threshold=threshold,
        )
    else:
        results, sorted_results = github.find_neighbour_repos(
            owner=owner,
            repo=repo,
            token=gh_token,
            limit_pages=limit_pages,
            threshold=threshold,
        )

    return {
        "algo-info": {
            "github-repo": f"{owner}/{repo}",
            "use_async": use_async,
            "limit_pages": limit_pages,
            "threshold": threshold,
            "gh_token": display_secret(gh_token),
        },
        "results": sorted_results,
    }


@router.get("/repos/{owner}/{repo}/graphql")
async def graphql_starneighbours(
    owner: str, repo: str, threshold: int = 1, gh_token: str = None
):
    """Compute Star neighbours API. Using GitHub GraphQL API.

    Testing GitHub GraphQL API to speed-up process.
    Still a Work-In-Progress, on large scale repository, we reach errors.

    :param owner: Github's repository owner
    :param repo: Github's repository name
    :param threshold: Only return repository with more than 'n' common user
    :param gh_token: Override App Github Token
    :return: List of GitHub Repository
    """
    # If no gh_token provided, try to use the App GitHub token from the settings
    if gh_token is None:
        gh_token = settings.github_token

    results, sorted_results = github.find_graphql_neighbour_repos(
        owner=owner, repo=repo, token=gh_token, threshold=threshold
    )

    return {
        "algo-info": {
            "github-repo": f"{owner}/{repo}",
            "limit_pages": 1,
            "threshold": threshold,
            "gh_token": display_secret(gh_token),
        },
        "results": sorted_results,
    }
