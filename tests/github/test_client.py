import pytest


# ---------------------------------------------------------------------------------------------------------------------
# Testing GitHub Rest Client
@pytest.mark.parametrize(
    "owner,repo,params,expected_length",
    [
        ("benjaminlong", "django_hotwired", None, 1),
        ("benjaminlong", "django_hotwired", {"per_page": 2}, 1),
        # ("benjaminlong", "mergify_algos", None, None, 0),
    ],
)
def test_fetch_stargazers(owner, repo, params, expected_length, github_rest_client):
    response = github_rest_client.fetch_stargazers(
        owner=owner, repo=repo, params=params
    )
    assert isinstance(response, list)
    assert len(response) == expected_length


@pytest.mark.parametrize(
    "user,params,expected_length",
    [
        # ("benjaminlong", None, 52),
        ("benjaminlong", {"per_page": 30}, 52),
    ],
)
@pytest.mark.asyncio
async def test_fetch_user_starred_repos(
    user, params, expected_length, github_rest_client
):
    response = await github_rest_client.afetch_user_starred_repos(
        user=user, params=params
    )

    assert response
    assert len(response) == expected_length


# ---------------------------------------------------------------------------------------------------------------------
# Testing GitHub GraphQL Client
@pytest.mark.parametrize(
    "owner,repo,expected_length",
    [
        ("benjaminlong", "django_hotwired", 1),
        ("Mergifyio", "mergify-cli", 10),
    ],
)
def test_graphql_fetch_stargazers(owner, repo, expected_length, github_graphql_client):
    response = github_graphql_client.fetch_stargazers_with_starred_repos(
        owner=owner, repo=repo
    )

    assert isinstance(response, dict)
    assert len(response) == expected_length
