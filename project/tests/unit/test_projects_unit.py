import json
from datetime import datetime

from app.api.routers import projects


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
        test_data = {
            "id": 1,
            "name": "test_name",
            "comment": "test_comment",
            "created_at": datetime(2024, 12, 1).isoformat(),
        }

        async def mock_get_project_by_name(fake_db_session, fake_project_name):
            return test_data

        monkeypatch.setattr(projects, "get_project_by_name", mock_get_project_by_name)

        response = test_app.get("/projects/test_name")

        assert response.status_code == 200
        assert response.json() == test_data

    def test_get_not_existent_project(
        self,
        test_app,
        monkeypatch,
    ):
        async def mock_get_project_by_name(fake_db_session, fake_project_name):
            return None

        monkeypatch.setattr(projects, "get_project_by_name", mock_get_project_by_name)
        project_name = "test_name"

        response = test_app.get(f"/projects/{project_name}")

        assert response.status_code == 404
        assert response.json()["detail"] == f"Project {project_name} does not exists."
