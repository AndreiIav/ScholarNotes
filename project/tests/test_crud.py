import json

import pytest
import sqlalchemy.exc


def test_add_project(test_app):
    payload = {"name": "test_name", "comment": "test_comment"}

    res = test_app.post("/projects", data=json.dumps(payload))

    assert res.status_code == 201
    assert res.json()["name"] == "test_name"
    assert res.json()["comment"] == "test_comment"


def test_add_same_project_name_raises_error(test_app):
    payload = {"name": "test_name_1", "comment": "test_comment_1"}

    with pytest.raises(sqlalchemy.exc.IntegrityError) as e:
        test_app.post("/projects", data=json.dumps(payload))
        test_app.post("/projects", data=json.dumps(payload))

    assert "duplicate key value violates unique constraint" in str(e.value)
