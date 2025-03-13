# Mergify Algo

Backend, using FastAPI for the Mergify's test algorithms

Link: [Stargazer Test Statement](https://mergify.notion.site/Stargazer-4cf5427e34a542f0aee4e829bb6d9035)

> Work Time: ~10h.

## Installation

Currently, tested using Python 3.9

```shell
# Fetch source code from github
git clone ...
cd mergify_algos

# Create python virtual env
python -m venv venv
# Activate virtual env
source venv/bin/activate

# Install Python deps
pip install --upgrade pip
pip install -r requirements/local.txt
```

## Test

To run the unit-tests, use

> If GitHub API Credentials isn't provided. UTs may failed because your IP
> reach API rate limit. Tests use [`.env`configuration file](#configure-env-file)

```shell
pytest [-vv]
```

#### Coverage

```shell
# Check your test coverage
coverage run -m pytest
# Generate an HTML coverage report
coverage html
# Open html index
open htmlcov/index.html
```

## Environment variables

The environment variables are described in this section.

### Github API credentials

Github Credential aren't mandatory.

However, you will quickly reach GitHub API rate limit.

First Go to GitHub to create your GitHub access token.

See:
- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token

#### Configure `.env` file

Create `.env` at the ROOT project directory and set `GITHUB_TOKEN` variable.go

Your `.env` file should look like:
```
GITHUB_TOKEN="ghp_..."
```

#### APIs Query Param

Use query parameter `gh_token` on our APIs using GitHub.

## Running

```shell
fastapi dev mergify_algos/app.py
# or
python -m mergify_algos.app

# Currently only work on PyCharm because PyCharm add content and source root
# directory to PYTHONPATH
python mergify_algos/app.py
```

- Visit the FastAPI endpoints: [http://localhost:8000/](http://localhost:8000/)
- Visit the API docs page to try the endpoints:
[http://localhost:8000/docs](http://localhost:8000/docs)
- Visit the GitHub API Exemple:
  - http://localhost:8000/github/repos/{owner}/{repos}
  - http://localhost:8000/github/repos/Mergifyio/mergify-cli/?limit_pages=1&threshold=3


## TODOs & Improvements

See [TODOS.md](./TODOS.md)
