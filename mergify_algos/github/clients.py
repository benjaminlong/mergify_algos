import httpx
import re
import requests
import urllib.parse

from fastapi import HTTPException

# REQUESTS_TIMEOUT = (3.10, 20.0)
# HTTPX_TIMEOUT is causing issue when performing many concurrent HTTP requests.
# Because Requests are all process at once (no batch) and many will reach timeout.
# HTTPX_TIMEOUT = httpx.Timeout(10)
# HTTPX_TIMEOUT = httpx.Timeout(10, connect=60.0)

GITHUB_API_URL = "https://api.github.com"
GITHUB_NEXT_PATTERN = re.compile(r"(?<=<)([\S]*)(?=>; rel=\"Next\")", re.IGNORECASE)

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


class GitHubRestClient:

    def __init__(self, token: str = None):
        self._token = token

    def _build_headers(self, extra_headers: dict = None):
        """Private function to build GitHub headers"""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self._token is not None:
            headers["Authorization"] = f"Bearer {self._token}"

        if extra_headers:
            headers.update(extra_headers)

        return headers

    def _build_params(self, extra_params: dict = None):
        """Private function to build GitHub params.
        It encodes a dict into a URL query string

        :param extra_params: Extra parameters
        :return str: A URL query string
        """
        # Default GitHub pagination per_age params is 100
        _params = {"per_page": 100}

        if extra_params is not None:
            _params.update(extra_params)

        return urllib.parse.urlencode(_params)

    def _get_next_url(self, response):
        """Return next_url from Response
        TODO: Doc
        """
        # Gather next paginated url if available
        link_header = response.headers.get("link", False)
        # page_remaining = link_header.find('rel="next"') != -1 if link_header else False
        if not link_header:
            return None

        _results = re.findall(GITHUB_NEXT_PATTERN, link_header)
        return _results[0]

    def _get_paginated_data(self, url, limit_pages=2):
        """Fetch Data from a paginated API.

        :param url: Request url to fetch data from
        :param limit_pages: Limit the number of page used to fetch data.
        :returns: data
        """
        _data, page, next_url = [], 1, url

        while next_url:
            # Fetching one page
            response = requests.get(next_url, headers=self._build_headers())

            # blong: Here we should handle retries with expo waiting time...
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail=response.json()
                )

            # parsed_data = _parse_data(response.json())
            _data += response.json()

            # Check if we reach limit_pages and if response has a next_url
            # blong: TODO: can be improve to avoid if/else?
            if page < limit_pages:
                next_url = self._get_next_url(response)
                page += 1
            else:
                next_url = None

        return _data

    def fetch_stargazers(self, owner, repo, params=None, limit_pages=2):
        """Fetch stargazers from GitHub paginated API.

        :param owner: Github repository's owner name
        :param repo: GitHub repository's name
        :param params: [optional] Extra params added to the urls (Default: None)
        :param limit_pages: Limit the number of page used to fetch data.
        :returns: List of GitHub users' name (login)
        """
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/stargazers?{self._build_params(params)}"
        data = self._get_paginated_data(url, limit_pages=limit_pages)

        return [user["login"] for user in data]

    def fetch_user_starred_repos(self, user, params=None, limit_pages=2):
        """Fetch given user's starred repositories from GitHub paginated API

        :param user: GitHub user's login string
        :param params: [optional] Extra params added to the urls (Default: None)
        :param limit_pages: Limit the number of page used to fetch data.

        :returns: List of GitHub repository's name
        """
        url = f"{GITHUB_API_URL}/users/{user}/starred?{self._build_params(params)}"
        data = self._get_paginated_data(url, limit_pages=limit_pages)

        # blong: here full-name returns "{owner}/{repo}"
        # name returns "{repo}"
        return [_repo["full_name"] for _repo in data]

    # -------------------------------------------------------------------------
    # Asynchronize implementation
    async def _aget_paginated_data(self, url, limit_pages=2):
        """Async Get Paginated Data
        TODO: Doc
        """
        _data, page, next_url = [], 1, url

        async with httpx.AsyncClient() as client:
            while next_url:
                response = await client.get(next_url, headers=self._build_headers())
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, detail=response.json()
                    )

                # parsed_data = _parse_data(response.json())
                _data += response.json()

                # Check if, we reach limit_pages and if response has a next_url
                # blong: TODO: can be improve to avoid if/else?
                if page < limit_pages:
                    next_url = self._get_next_url(response)
                    page += 1
                else:
                    next_url = None

        return _data

    async def afetch_user_starred_repos(self, user, params=None, limit_pages=2):
        """Async Fetch user starred repositories
        TODO: Doc
        """
        url = f"{GITHUB_API_URL}/users/{user}/starred?{self._build_params(params)}"
        data = await self._aget_paginated_data(url, limit_pages=limit_pages)

        return [_repo["full_name"] for _repo in data]


# -----------------------------------------------------------------------------
# Exploring GraphQL...
# See: https://docs.github.com/en/graphql/overview/explorer
# When it work, it's fast, however, GraphQL often return error when testing
# on large repository with many stargazers.
# GraphQL limit: https://docs.github.com/en/graphql/overview/rate-limits-and-node-limits-for-the-graphql-api
# - Clients must supply a first or last argument on any connection
# - max 500,000 total nodes.
repo_stargazer_with_starred_repositories_query = """
query($owner: String!, $name: String!, $after: String) {
  repository(owner: $owner, name: $name) {
    name
    nameWithOwner
    stargazers(first: 50, after: $after) {
      edges {
        node {
          login
          starredRepositories(first: 50, orderBy: {field: STARRED_AT, direction: DESC}) {
            totalCount
            nodes {
              nameWithOwner
            }
            pageInfo {
              endCursor
              startCursor
              hasNextPage
            }
          }
        }
      }
    }
  }
}
"""


class GitHubGraphQLClient:
    def __init__(self, token: str = None):
        self._token = token

    def _build_headers(self, extra_headers: dict = None):
        headers = {}
        if self._token is not None:
            headers["Authorization"] = f"Bearer {self._token}"

        return headers

    def _parse_data(self, data):
        results = {}
        if "errors" in data:
            raise HTTPException(status_code=500, detail=data["errors"])

        stargazers_data = data["data"]["repository"]["stargazers"]
        for edge in stargazers_data["edges"]:
            starred_repos = edge["node"]["starredRepositories"]["nodes"]
            results[edge["node"]["login"]] = [x["nameWithOwner"] for x in starred_repos]

        return results

    def fetch_stargazers_with_starred_repos(self, owner, repo, limit_pages=2):
        response = requests.post(
            GITHUB_GRAPHQL_URL,
            headers=self._build_headers(),
            json={
                "query": repo_stargazer_with_starred_repositories_query,
                "variables": {
                    "owner": owner,
                    "name": repo,
                },
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )

        return self._parse_data(response.json())
