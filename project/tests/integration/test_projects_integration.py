import json
from datetime import datetime, timezone


class TestPostProject:
    def test_add_new_project(self, test_app, delete_project_table_data):
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

    def test_cannot_add_a_project_with_already_existing_name(
        self, test_app, delete_project_table_data
    ):
        payload = {"name": "test_name_1", "comment": "test_comment_1"}

        test_app.post("/projects", data=json.dumps(payload))
        response = test_app.post("/projects", data=json.dumps(payload))

        assert response.status_code == 400
        assert (
            f"Project name '{payload['name']}' already exists. Please select a"
            " unique project name and try again." == response.json()["detail"]
        )


class TestGetAllProjects:
    def test_get_projects(self, test_app, add_project_data, delete_project_table_data):
        response = test_app.get("/projects")

        assert response.status_code == 200
        assert len(response.json()) == 2

        assert response.json()[0]["id"]
        assert response.json()[0]["name"] == "test_name"
        assert response.json()[0]["comment"] == "test_comment"
        assert response.json()[0]["created_at"]

        assert response.json()[1]["id"]
        assert response.json()[1]["name"] == "test_name_2"
        assert response.json()[1]["comment"] == "test_comment_2"
        assert response.json()[1]["created_at"]


class TestGetProject:
    def test_get_project(self, test_app, add_project_data, delete_project_table_data):
        response = test_app.get("/projects/test_name")

        assert response.status_code == 200

        assert response.json()["id"]
        assert response.json()["name"] == "test_name"
        assert response.json()["comment"] == "test_comment"
        assert response.json()["created_at"]

    def test_get_not_existent_project(self, test_app):
        project_name = "inexistent_name"

        response = test_app.get(f"/projects/{project_name}")

        assert response.status_code == 404
        assert response.json()["detail"] == f"Project {project_name} does not exists."
