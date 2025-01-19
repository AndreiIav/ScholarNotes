import json
from datetime import datetime

from app.api.routers import projects


class TestPostProject:
    def test_post_project_with_correct_payload(self, test_app_without_db, monkeypatch):
        test_request_payload = {"name": "test_name", "comment": "test_comment"}
        test_response_payload = {
            "id": 1,
            "name": "test_name",
            "comment": "test_comment",
            "created_at": datetime(2024, 12, 1).isoformat(),
        }

        async def mock_get_project_by_name(project_name, db_session):
            return None

        async def mock_post_project(payload, db_session):
            return test_response_payload

        monkeypatch.setattr(projects, "get_project_by_name", mock_get_project_by_name)
        monkeypatch.setattr(projects, "post_project", mock_post_project)

        response = test_app_without_db.post(
            "/projects", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 201
        assert response.json() == test_response_payload

    def test_post_project_with_incorrect_payload(self, test_app_without_db):
        response = test_app_without_db.post("/projects", data=json.dumps({}))

        assert response.status_code == 422

    def test_cannot_add_a_project_with_already_existing_name(
        self, test_app_without_db, monkeypatch
    ):
        project_name = "test_name_1"

        async def mock_get_project_by_name(project_name, db_session):
            return project_name

        monkeypatch.setattr(projects, "get_project_by_name", mock_get_project_by_name)
        payload = {"name": project_name, "comment": "test_comment_1"}

        response = test_app_without_db.post("/projects", data=json.dumps(payload))

        assert response.status_code == 400
        assert (
            f"Project name '{payload['name']}' already exists. Please select a"
            " unique project name and try again." == response.json()["detail"]
        )


class TestGetAllProjects:
    def test_get_all_projects(self, test_app_without_db, monkeypatch):
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

        response = test_app_without_db.get("/projects/")

        assert response.status_code == 200
        assert response.json() == test_data


class TestGetProject:
    def test_get_project(self, test_app_without_db, monkeypatch):
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

        response = test_app_without_db.get(f"/projects/{test_id}/")

        assert response.status_code == 200
        assert response.json() == test_data

    def test_get_not_existent_project(
        self,
        test_app_without_db,
        monkeypatch,
    ):
        async def mock_get_project_by_id(fake_db_session, fake_project_id):
            return None

        monkeypatch.setattr(projects, "get_project_by_id", mock_get_project_by_id)

        response = test_app_without_db.get("/projects/999/")

        assert response.status_code == 404
        assert response.json()["detail"] == "Project id not found."


class TestPatchProject:
    def test_patch_project(self, test_app_without_db, monkeypatch):
        test_request_payload = {"name": "updated_name", "comment": "updated_comment"}

        class DummyProject:
            id = 1
            name = "test_name"
            comment = "test_comment"
            created_at = datetime(2024, 12, 1).isoformat()

        async def mock_get_project_by_id(fake_db_session, fake_project_id):
            dummy_project = DummyProject()
            return dummy_project

        monkeypatch.setattr(projects, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_project_by_name(fake_db_session, fake_project_id):
            return None

        monkeypatch.setattr(projects, "get_project_by_name", mock_get_project_by_name)

        async def mock_update_project(project_id, payload, db_session):
            updated_dummy_project = DummyProject()
            updated_dummy_project.name = test_request_payload["name"]
            updated_dummy_project.comment = test_request_payload["comment"]
            return updated_dummy_project

        monkeypatch.setattr(projects, "update_project", mock_update_project)

        res = test_app_without_db.patch(
            "/projects/1/", data=json.dumps(test_request_payload)
        )

        assert res.status_code == 200
        assert res.json()["id"] == 1
        assert res.json()["name"] == test_request_payload["name"]
        assert res.json()["comment"] == test_request_payload["comment"]

    def test_patch_project_cannot_update_not_existing_project(
        self, test_app_without_db, monkeypatch
    ):
        async def mock_get_project_by_id(fake_db_session, fake_project_id):
            return None

        monkeypatch.setattr(projects, "get_project_by_id", mock_get_project_by_id)

        test_request_payload = {
            "name": "name",
            "comment": "comment",
        }

        response = test_app_without_db.patch(
            "/projects/1/", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Project id not found."

    def test_patch_project_cannot_update_name_to_an_already_existing_one(
        self, test_app_without_db, monkeypatch
    ):
        payload_request = {
            "name": "updated_name",
            "comment": "updated_comment",
        }

        class DummyProject:
            id = 1
            name = "test_name"
            comment = "test_comment"
            created_at = datetime(2024, 12, 1).isoformat()

        async def mock_get_project_by_id(db_session, project_id):
            dummy_project = DummyProject()
            return dummy_project

        monkeypatch.setattr(projects, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_project_by_name(name, db_session):
            return True

        monkeypatch.setattr(projects, "get_project_by_name", mock_get_project_by_name)

        response = test_app_without_db.patch(
            "/projects/1/", data=json.dumps(payload_request)
        )

        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == f"Project name '{payload_request['name']}' already "
            "exists. Please select a unique project name and try again."
        )


class TestDeleteProject:
    def test_delete_project_deletes_project(self, test_app_without_db, monkeypatch):
        class DummyProject:
            id = 1
            name = "test_name"
            comment = "test_comment"
            created_at = datetime(2024, 12, 1).isoformat()

        async def mock_get_project_by_id(db_session, project_id):
            return True

        monkeypatch.setattr(projects, "get_project_by_id", mock_get_project_by_id)

        async def mock_remove_project(project_id, db_session):
            dummy_project = DummyProject()
            return dummy_project

        monkeypatch.setattr(projects, "remove_project", mock_remove_project)

        response = test_app_without_db.delete("/projects/1/")

        assert response.status_code == 200
        assert response.json()["name"] == "test_name"
        assert response.json()["comment"] == "test_comment"

    def test_delete_project_cannot_delete_not_existent_project(
        self, test_app_without_db, monkeypatch
    ):
        async def mock_get_project_by_id(db_session, project_id):
            return None

        monkeypatch.setattr(projects, "get_project_by_id", mock_get_project_by_id)

        response = test_app_without_db.delete("/projects/1/")

        assert response.status_code == 404
        assert response.json()["detail"] == "Project id not found."
