import pytest
import time

from mergify_algos.github.neighbours import (
    find_neighbour_repos,
    afind_neighbour_repos,
    _transform_user_starred_repositories,
    _compute_and_order_neighbours,
)


@pytest.mark.parametrize(
    "owner,repo,expected_length",
    [
        ("benjaminlong", "django_hotwired", 0),
        ("Mergifyio", "mergify-cli", None),
    ],
)
def test_find_neighbour_repos(owner, repo, expected_length, github_token):
    print(f"Performing Sync find_neighbour_repos for {owner}/{repo}")
    timer_start = time.perf_counter()

    response, sorted_response = find_neighbour_repos(
        owner=owner, repo=repo, token=github_token
    )

    timer_end = time.perf_counter()
    print(f"Performed in... {timer_end - timer_start:0.4f} sec")

    assert isinstance(response, list)
    assert isinstance(sorted_response, list)

    if expected_length:
        assert len(response) == len(sorted_response) == expected_length


@pytest.mark.parametrize(
    "owner,repo,expected_length",
    [
        ("benjaminlong", "django_hotwired", 0),
        ("Mergifyio", "mergify-cli", 187),
    ],
)
@pytest.mark.asyncio
async def test_afind_neighbour_repos(owner, repo, expected_length, github_token):
    print(f"Performing Async find_neighbour_repos for {owner}/{repo}")
    timer_start = time.perf_counter()
    response, sorted_response = await afind_neighbour_repos(
        owner=owner, repo=repo, token=github_token
    )
    timer_end = time.perf_counter()
    print(f"Performed in... {timer_end - timer_start:0.4f}sec")

    assert isinstance(response, list)
    assert isinstance(sorted_response, list)

    if expected_length:
        assert len(response) == len(sorted_response) == expected_length


def test__transform_user_starred_repositories():
    user_repo_dict = {
        "user1": ["repo1", "repo2", "repo5"],
        "user2": ["repo2", "repo3"],
        "user3": ["repo2", "repo3", "repo4"],
        "user4": ["repo1", "repo4"],
    }
    result_dict = _transform_user_starred_repositories(user_repo_dict)

    assert result_dict
    assert result_dict == {
        "repo1": ["user1", "user4"],
        "repo2": ["user1", "user2", "user3"],
        "repo3": ["user2", "user3"],
        "repo4": ["user3", "user4"],
        "repo5": ["user1"],
    }


def test__compute_and_order_neighbours():
    result_dict = {
        "repo1": ["user1", "user4"],
        "repo2": ["user1", "user2", "user3"],
        "repo3": ["user2", "user3"],
        "repo4": ["user3", "user4"],
        "repo5": ["user1"],
    }

    result_dict, sorted_result_dict = _compute_and_order_neighbours(result_dict)
    assert sorted_result_dict == [
        {
            "repo": "repo2",
            "stargazers_count": 3,
            "stargazers": ["user1", "user2", "user3"],
        },
        {"repo": "repo1", "stargazers_count": 2, "stargazers": ["user1", "user4"]},
        {"repo": "repo3", "stargazers_count": 2, "stargazers": ["user2", "user3"]},
        {"repo": "repo4", "stargazers_count": 2, "stargazers": ["user3", "user4"]},
    ]
