import json
from datetime import datetime

from app.api.routers import project_notes


class TestPostProjectNotes:
    def test_post_project_notes_happy_path(self, test_app_without_db, monkeypatch):
        test_request_payload = {
            "note_name": "test_name",
            "note_author": "test_author",
            "note_publication_details": "test_publication_details",
            "note_publication_year": 1889,
            "note_comments": "test_comments",
            "note_tags": ["tag_1", "tag_2"],
        }
        test_project_id = 1

        async def mock_get_project_by_id(session, project_id):
            return True

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_note_by_name_and_project(note_name, project_id, db_session):
            return False

        monkeypatch.setattr(
            project_notes,
            "get_note_by_name_and_project",
            mock_get_note_by_name_and_project,
        )

        async def mock_get_tags_to_be_inserted(tags, db_session):
            return ["tag_1", "tag_2"]

        monkeypatch.setattr(
            project_notes, "get_tags_to_be_inserted", mock_get_tags_to_be_inserted
        )

        async def mock_insert_tags(tags, db_session):
            return None

        monkeypatch.setattr(project_notes, "insert_tags", mock_insert_tags)

        async def mock_insert_note(payload, project_id, db_session):
            class Tag1:
                name = test_request_payload["note_tags"][0]

            class Tag2:
                name = test_request_payload["note_tags"][1]

            tag_1, tag_2 = Tag1(), Tag2()
            all_tags = [tag_1, tag_2]

            class Note:
                id = 1
                project_id = test_project_id
                name = test_request_payload["note_name"]
                author = test_request_payload["note_author"]
                publication_details = test_request_payload["note_publication_details"]
                publication_year = test_request_payload["note_publication_year"]
                comments = test_request_payload["note_comments"]
                created_at = datetime(2024, 12, 1).isoformat()
                tags = all_tags

            res = Note()
            return res

        monkeypatch.setattr(project_notes, "insert_note", mock_insert_note)

        response = test_app_without_db.post(
            f"/projects/{test_project_id}/notes/", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 200
        assert response.json()["note_id"] == 1
        assert response.json()["project_id"] == test_project_id
        assert response.json()["note_name"] == test_request_payload["note_name"]
        assert response.json()["note_author"] == test_request_payload["note_author"]
        assert (
            response.json()["note_publication_details"]
            == test_request_payload["note_publication_details"]
        )
        assert (
            response.json()["note_publication_year"]
            == test_request_payload["note_publication_year"]
        )
        assert response.json()["note_comments"] == test_request_payload["note_comments"]
        assert response.json()["created_at"] == datetime(2024, 12, 1).isoformat()
        assert response.json()["note_tags"] == test_request_payload["note_tags"]

    def test_post_project_notes_cannot_post_if_project_does_not_exists(
        self, test_app_without_db, monkeypatch
    ):
        test_request_payload = {
            "note_name": "test_name",
            "note_author": "test_author",
            "note_publication_details": "test_publication_details",
            "note_publication_year": 1889,
            "note_comments": "test_comments",
            "note_tags": ["tag_1", "tag_2"],
        }
        test_project_id = 1

        async def mock_get_project_by_id(session, project_id):
            return False

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        response = test_app_without_db.post(
            f"/projects/{test_project_id}/notes/", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Project id not found"

    def test_post_project_notes_cannot_add_existing_note_name_for_same_project(
        self, test_app_without_db, monkeypatch
    ):
        test_request_payload = {
            "note_name": "test_name",
            "note_author": "test_author",
            "note_publication_details": "test_publication_details",
            "note_publication_year": 1889,
            "note_comments": "test_comments",
            "note_tags": ["tag_1", "tag_2"],
        }
        test_project_id = 1
        test_project_name = "test_project_name"

        async def mock_get_project_by_id(session, project_id):
            return True

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_note_by_name_and_project(note_name, project_id, db_session):
            class DbRow:
                project_name = test_project_name

            db_row = DbRow()
            return db_row

        monkeypatch.setattr(
            project_notes,
            "get_note_by_name_and_project",
            mock_get_note_by_name_and_project,
        )

        response = test_app_without_db.post(
            f"/projects/{test_project_id}/notes/", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            f"Note '{test_request_payload['note_name']}' already exists for"
            f" project '{test_project_name}'. Please select a unique note"
            " name for this project."
        )
