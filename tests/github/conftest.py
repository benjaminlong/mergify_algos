import pytest

from mergify_algos.github import clients
from mergify_algos.config import settings


# ---------------------------------------------------------------------------------------------------------------------
# Fixtures
# blong: Duplicated from test_client.py and conftest.py. But otherwise,
# individual UT doesn't work with PyCharm... Never had this issue.
@pytest.fixture(scope="session")
def github_token():
    return settings.github_token


@pytest.fixture(scope="module")
def github_rest_client(github_token):
    return clients.GitHubRestClient(token=github_token)


@pytest.fixture(scope="module")
def github_graphql_client(github_token):
    return clients.GitHubGraphQLClient(token=github_token)
