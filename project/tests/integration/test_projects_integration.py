import json


def test_add_project(test_app):
    payload = {"name": "test_name", "comment": "test_comment"}

    res = test_app.post("/projects", data=json.dumps(payload))

    assert res.status_code == 201
    assert res.json()["name"] == "test_name"
    assert res.json()["comment"] == "test_comment"


def test_cannot_add_same_project_name(test_app):
    payload = {"name": "test_name_1", "comment": "test_comment_1"}

    test_app.post("/projects", data=json.dumps(payload))
    response = test_app.post("/projects", data=json.dumps(payload))

    assert response.status_code == 400
    assert (
        f"Project name '{payload['name']}' already exists. Please select a"
        " unique project name and try again." == response.json()["detail"]
    )
