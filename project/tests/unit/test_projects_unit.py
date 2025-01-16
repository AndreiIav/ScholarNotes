import json
from datetime import datetime

from app.api.routers import projects
from app.models import Project


class TestPostProject:
    def test_post_project_with_correct_payload(self, test_app, monkeypatch):
        test_request_payload = {"name": "test_name", "comment": "test_comment"}
        test_response_payload = {
            "id": 1,
            "name": "test_name",
            "comment": "test_comment",
            "created_at": datetime(2024, 12, 1).isoformat(),
        }

        async def mock_post_project(fake_payload, fake_db_session):
            return test_response_payload

        monkeypatch.setattr(projects, "post_project", mock_post_project)

        response = test_app.post("/projects", data=json.dumps(test_request_payload))

        assert response.status_code == 201
        assert response.json() == test_response_payload

    def test_post_project_with_incorrect_payload(self, test_app):
        response = test_app.post("/projects", data=json.dumps({}))

        assert response.status_code == 422

    def test_cannot_add_a_project_with_already_existing_name(
        self, test_app, monkeypatch
    ):
        project_name = "test_name_1"

        async def mock_check_if_project_name_exists(project_name, db_session):
            return project_name

        monkeypatch.setattr(
            projects, "check_if_project_name_exists", mock_check_if_project_name_exists
        )
        payload = {"name": project_name, "comment": "test_comment_1"}

        response = test_app.post("/projects", data=json.dumps(payload))

        assert response.status_code == 400
        assert (
            f"Project name '{payload['name']}' already exists. Please select a"
            " unique project name and try again." == response.json()["detail"]
        )


class TestGetAllProjects:
    def test_get_all_projects(self, test_app, monkeypatch):
        test_data = [
            {
                "id": 1,
                "name": "test_name",
                "comment": "test_comment",
                "created_at": datetime(2024, 12, 1).isoformat(),
            },
            {
                "id": 2,
                "name": "test_name_2",
                "comment": "test_comment_2",
                "created_at": datetime(2024, 1, 1).isoformat(),
            },
        ]

        async def mock_get_projects(db_session):
            return test_data

        monkeypatch.setattr(projects, "get_all_projects", mock_get_projects)

        response = test_app.get("/projects/")

        assert response.status_code == 200
        assert response.json() == test_data


class TestGetProject:
    def test_get_project(self, test_app, monkeypatch):
        test_id = 1
        test_data = {
            "id": test_id,
            "name": "test_name",
            "comment": "test_comment",
            "created_at": datetime(2024, 12, 1).isoformat(),
        }

        async def mock_get_project_by_id(fake_db_session, fake_project_id):
            return test_data

        monkeypatch.setattr(projects, "get_project_by_id", mock_get_project_by_id)

        response = test_app.get(f"/projects/{test_id}")

        assert response.status_code == 200
        assert response.json() == test_data

    def test_get_not_existent_project(
        self,
        test_app,
        monkeypatch,
    ):
        async def mock_get_project_by_id(fake_db_session, fake_project_id):
            return None

        monkeypatch.setattr(projects, "get_project_by_id", mock_get_project_by_id)

        response = test_app.get("/projects/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Project id not found."


class TestPatchProject:
    def test_patch_project_cannot_update_not_existing_project(
        self, test_app, monkeypatch
    ):
        async def mock_get_project_by_id(fake_db_session, fake_project_id):
            return None

        monkeypatch.setattr(projects, "get_project_by_id", mock_get_project_by_id)

        test_request_payload = {
            "name": "name",
            "comment": "comment",
        }

        response = test_app.patch("/projects/1", data=json.dumps(test_request_payload))

        assert response.status_code == 404
        assert response.json()["detail"] == "Project id not found."

    def test_patch_project_cannot_update_name_to_an_already_existing_one(
        self, test_app, monkeypatch
    ):
        project = Project(name="test_project", comment="test_comment")

        async def mock_get_project_by_id(db_session, project_id):
            return project

        monkeypatch.setattr(projects, "get_project_by_id", mock_get_project_by_id)

        async def mock_check_if_project_name_exists(name, db_session):
            return True

        monkeypatch.setattr(
            projects, "check_if_project_name_exists", mock_check_if_project_name_exists
        )

        payload_request = {
            "name": "another_name",
            "comment": "another_comment",
        }

        response = test_app.patch("/projects/1", data=json.dumps(payload_request))

        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == f"Project name '{payload_request['name']}' already "
            "exists. Please select a unique project name and try again."
        )
