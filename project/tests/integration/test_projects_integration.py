import json
from datetime import datetime, timezone


def test_add_new_project(test_app):
    payload = {"name": "test_name", "comment": "test_comment"}

    res = test_app.post("/projects", data=json.dumps(payload))

    assert res.status_code == 201
    assert res.json()["id"]
    assert res.json()["name"] == "test_name"
    assert res.json()["comment"] == "test_comment"
    assert res.json()["created_at"]

    created_at = res.json()["created_at"]
    # create a datetime object from the "created_at" string
    created_at_datetime = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
    # make it UTC "aware"
    created_at_datetime = created_at_datetime.replace(tzinfo=timezone.utc)
    # get the difference between the current UTC aware datetime and the one
    # retrieved from the response
    seconds_diff = datetime.now(timezone.utc) - created_at_datetime
    # it shouldn't be more than one second
    assert seconds_diff.seconds <= 1


def test_cannot_add_a_project_with_already_existing_name(test_app):
    payload = {"name": "test_name_1", "comment": "test_comment_1"}

    test_app.post("/projects", data=json.dumps(payload))
    response = test_app.post("/projects", data=json.dumps(payload))

    assert response.status_code == 400
    assert (
        f"Project name '{payload['name']}' already exists. Please select a"
        " unique project name and try again." == response.json()["detail"]
    )
