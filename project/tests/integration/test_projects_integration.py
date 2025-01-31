import json


class TestPostProject:
    def test_add_new_project(self, test_app, delete_project_table_data):
        payload = {"name": "test_name", "comment": "test_comment"}

        res = test_app.post("/projects", data=json.dumps(payload))

        assert res.status_code == 201
        assert res.json()["id"]
        assert res.json()["name"] == "test_name"
        assert res.json()["comment"] == "test_comment"
        assert res.json()["created_at"]


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
        test_project_id = 1
        response = test_app.get(f"/projects/{test_project_id}/")

        assert response.status_code == 200

        assert response.json()["id"] == test_project_id
        assert response.json()["name"] == "test_name"
        assert response.json()["comment"] == "test_comment"
        assert response.json()["created_at"]


class TestPatchProject:
    def test_patch_project_happy_path(
        self, test_app, add_project_data, delete_project_table_data
    ):
        test_project_id = 1
        payload_request_data = {
            "name": "updated_test_name",
            "comment": "updated_test_comment",
        }

        response = test_app.patch(
            f"/projects/{test_project_id}/", data=json.dumps(payload_request_data)
        )

        assert response.status_code == 200
        assert response.json()["id"] == test_project_id
        assert response.json()["name"] == payload_request_data["name"]
        assert response.json()["comment"] == payload_request_data["comment"]
        assert response.json()["created_at"]


class TestDeleteProject:
    def test_delete_project_deletes_project(
        self, test_app, add_project_data, delete_project_table_data
    ):
        delete_project_response = test_app.delete("/projects/1/")
        get_deleted_project_response = test_app.get("/projects/1/")

        assert delete_project_response.status_code == 200
        assert delete_project_response.json()["message"] == "Project deleted"

        assert get_deleted_project_response.status_code == 404
        assert get_deleted_project_response.json()["detail"] == "Project id not found."

    def test_delete_project_does_not_delete_not_existent_project(self, test_app):
        response = test_app.delete("/projects/999/")

        assert response.status_code == 404
        assert response.json()["detail"] == "Project id not found."
