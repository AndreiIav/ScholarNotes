import json


def test_post_project(test_app_with_db):
    payload = {"name": "test_name", "comment": "test_comment"}

    res = test_app_with_db.post("/projects", data=json.dumps(payload))

    assert res.status_code == 201
    assert res.json()["name"] == "test_name"
    assert res.json()["comment"] == "test_comment"
    assert len(res.json()) == 2
