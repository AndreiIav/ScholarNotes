import json
from datetime import datetime
from unittest.mock import ANY, AsyncMock

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

        mock_insert_missing_tags = AsyncMock()

        monkeypatch.setattr(
            project_notes, "insert_missing_tags", mock_insert_missing_tags
        )

        async def mock_insert_note(payload, project_id, db_session):
            class MockTag:
                def __init__(self, name):
                    self.name = name

            tag_1 = MockTag(name="tag_1")
            tag_2 = MockTag(name="tag_2")

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

        # assert that function with no return value was called correctly
        mock_insert_missing_tags.assert_called_once_with(
            tags=test_request_payload["note_tags"], db_session=ANY
        )

        # assert response
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


class TestGetAllProjectNotes:
    def test_get_all_project_notes_happy_flow(self, test_app_without_db, monkeypatch):
        async def mock_get_project_by_id(session, project_id):
            return True

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_all_notes_for_project(project_id, db_session):
            class MockTag:
                def __init__(self, name):
                    self.name = name

            tag_1 = MockTag(name="tag_1")
            tag_2 = MockTag(name="tag_2")

            class MockProjectNotes:
                def __init__(
                    self,
                    id,
                    project_id,
                    name,
                    author,
                    publication_details,
                    publication_year,
                    comments,
                    created_at,
                    tags,
                ):
                    self.id = id
                    self.project_id = project_id
                    self.name = name
                    self.author = author
                    self.publication_details = publication_details
                    self.publication_year = publication_year
                    self.comments = comments
                    self.created_at = created_at
                    self.tags = tags

            note_1 = MockProjectNotes(
                id=1,
                project_id=1,
                name="name_1",
                author="author_1",
                publication_details="details_1",
                publication_year=2000,
                comments="comm_1",
                created_at=datetime(2024, 12, 1).isoformat(),
                tags=[],
            )
            note_2 = MockProjectNotes(
                id=2,
                project_id=1,
                name="name_2",
                author="author_2",
                publication_details="details_2",
                publication_year=2001,
                comments="comm_2",
                created_at=datetime(2024, 12, 1).isoformat(),
                tags=[tag_1, tag_2],
            )

            return [note_1, note_2]

        monkeypatch.setattr(
            project_notes, "get_all_notes_for_project", mock_get_all_notes_for_project
        )

        response = test_app_without_db.get("projects/1/notes/")

        assert response.status_code == 200
        assert response.json() == [
            {
                "note_id": 1,
                "project_id": 1,
                "note_name": "name_1",
                "note_author": "author_1",
                "note_publication_details": "details_1",
                "note_publication_year": 2000,
                "note_comments": "comm_1",
                "created_at": datetime(2024, 12, 1).isoformat(),
                "note_tags": [],
            },
            {
                "note_id": 2,
                "project_id": 1,
                "note_name": "name_2",
                "note_author": "author_2",
                "note_publication_details": "details_2",
                "note_publication_year": 2001,
                "note_comments": "comm_2",
                "created_at": datetime(2024, 12, 1).isoformat(),
                "note_tags": ["tag_1", "tag_2"],
            },
        ]

    def test_get_all_project_notes_cannot_get_data_for_inexistent_project(
        self, test_app_without_db, monkeypatch
    ):
        async def mock_get_project_by_id(session, project_id):
            return False

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        response = test_app_without_db.get("/projects/1/notes/")

        assert response.status_code == 404
        assert response.json()["detail"] == "Project id not found"


class TestGetProjectNote:
    def test_get_project_note_happy_path(self, test_app_without_db, monkeypatch):
        async def mock_get_project_by_id(db_session, project_id):
            return True

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_note_by_id(note_id, db_session):
            class MockTag:
                def __init__(self, name):
                    self.name = name

            tag_1 = MockTag(name="tag_1")
            tag_2 = MockTag(name="tag_2")

            class MockProjectNotes:
                def __init__(
                    self,
                    id,
                    project_id,
                    name,
                    author,
                    publication_details,
                    publication_year,
                    comments,
                    created_at,
                    tags,
                ):
                    self.id = id
                    self.project_id = project_id
                    self.name = name
                    self.author = author
                    self.publication_details = publication_details
                    self.publication_year = publication_year
                    self.comments = comments
                    self.created_at = created_at
                    self.tags = tags

            note_1 = MockProjectNotes(
                id=1,
                project_id=1,
                name="name_1",
                author="author_1",
                publication_details="details_1",
                publication_year=2000,
                comments="comm_1",
                created_at=datetime(2024, 12, 1).isoformat(),
                tags=[tag_1, tag_2],
            )

            return note_1

        monkeypatch.setattr(project_notes, "get_note_by_id", mock_get_note_by_id)

        response = test_app_without_db.get("/projects/1/notes/1")

        assert response.status_code == 200

    def test_get_project_note_cannot_get_note_for_not_existent_project(
        self, test_app_without_db, monkeypatch
    ):
        async def mock_get_project_by_id(db_session, project_id):
            return False

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        response = test_app_without_db.get("/projects/1/notes/1")

        assert response.status_code == 404
        assert response.json()["detail"] == "Project id not found"

    def test_get_project_note_cannot_get_note_for_not_existent_note(
        self, test_app_without_db, monkeypatch
    ):
        async def mock_get_project_by_id(db_session, project_id):
            return True

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_note_by_id(note_id, db_session):
            return False

        monkeypatch.setattr(project_notes, "get_note_by_id", mock_get_note_by_id)

        response = test_app_without_db.get("/projects/1/notes/1")

        assert response.status_code == 404
        assert response.json()["detail"] == "Note id not found"

    def test_get_project_note_cannot_get_note_if_it_is_not_on_project(
        self, test_app_without_db, monkeypatch
    ):
        async def mock_get_project_by_id(db_session, project_id):
            return True

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_note_by_id(note_id, db_session):
            class MockNote:
                project_id = 999

            mock_note = MockNote()
            return mock_note

        monkeypatch.setattr(project_notes, "get_note_by_id", mock_get_note_by_id)

        response = test_app_without_db.get("/projects/1/notes/1")

        assert response.status_code == 404
        assert (
            response.json()["detail"] == "The note id cannot be found for this project."
        )


class TestPatchProjectNote:
    def test_patch_note_happy_path(self, test_app_without_db, monkeypatch):
        test_request_payload = {
            "name": "updated_test_note_name",
            "author": "updated_test_author",
            "publication_details": "updated_test_publication_details",
            "publication_year": 1889,
            "comments": "test_comments",
            "tags": ["tag_1", "tag_2"],
        }

        async def mock_get_project_by_id(db_session, project_id):
            return True

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_note_by_id(note_id, db_session):
            class MockTag:
                def __init__(self, name):
                    self.name = name

            tag_3 = MockTag(name="tag_3")
            tag_4 = MockTag(name="tag_4")

            class MockNote:
                id = 1
                project_id = 1
                name = "test_note_name"
                tags = [tag_3, tag_4]

            mock_note = MockNote()
            return mock_note

        monkeypatch.setattr(project_notes, "get_note_by_id", mock_get_note_by_id)

        async def mock_get_note_by_name_and_project(note_name, project_id, db_session):
            return None

        monkeypatch.setattr(
            project_notes,
            "get_note_by_name_and_project",
            mock_get_note_by_name_and_project,
        )

        mock_handle_note_tags_update = AsyncMock()
        monkeypatch.setattr(
            project_notes, "handle_note_tags_update", mock_handle_note_tags_update
        )

        async def mock_update_note(payload, note_id, db_session):
            class MockTag:
                def __init__(self, name):
                    self.name = name

            tag_1 = MockTag(name="tag_1")
            tag_2 = MockTag(name="tag_2")

            class MockNote:
                id = 1
                project_id = 1
                name = test_request_payload["name"]
                author = test_request_payload["author"]
                publication_details = test_request_payload["publication_details"]
                publication_year = test_request_payload["publication_year"]
                comments = test_request_payload["comments"]
                created_at = datetime(2024, 12, 1).isoformat()
                tags = [tag_1, tag_2]

            mock_note = MockNote()
            return mock_note

        monkeypatch.setattr(project_notes, "update_note", mock_update_note)

        response = test_app_without_db.patch(
            "/projects/1/notes/1", data=json.dumps(test_request_payload)
        )

        # assert that function with no return value was called
        mock_handle_note_tags_update.assert_called_once()

        # assert response
        assert response.status_code == 200
        assert response.json()["note_id"] == 1
        assert response.json()["project_id"] == 1
        assert response.json()["note_name"] == test_request_payload["name"]
        assert response.json()["note_author"] == test_request_payload["author"]
        assert (
            response.json()["note_publication_details"]
            == test_request_payload["publication_details"]
        )
        assert (
            response.json()["note_publication_year"]
            == test_request_payload["publication_year"]
        )
        assert response.json()["note_comments"] == test_request_payload["comments"]
        assert response.json()["created_at"] == datetime(2024, 12, 1).isoformat()
        assert response.json()["note_tags"] == test_request_payload["tags"]

    def test_patch_note_only_tags_received_happy_path(
        self, test_app_without_db, monkeypatch
    ):
        test_request_payload = {
            "tags": ["tag_1", "tag_2"],
        }

        async def mock_get_project_by_id(db_session, project_id):
            return True

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_note_by_id(note_id, db_session):
            class MockTag:
                def __init__(self, name):
                    self.name = name

            tag_3 = MockTag(name="tag_3")
            tag_4 = MockTag(name="tag_4")

            class MockNote:
                id = 1
                project_id = 1
                name = "test_name"
                author = "test_author"
                publication_details = "test_publication_details"
                publication_year = 1900
                comments = "test_comments"
                created_at = datetime(2024, 12, 1).isoformat()
                tags = [tag_3, tag_4]

            mock_note = MockNote()
            return mock_note

        monkeypatch.setattr(project_notes, "get_note_by_id", mock_get_note_by_id)

        async def mock_get_note_by_name_and_project(note_name, project_id, db_session):
            return None

        monkeypatch.setattr(
            project_notes,
            "get_note_by_name_and_project",
            mock_get_note_by_name_and_project,
        )

        mock_handle_note_tags_update = AsyncMock()
        monkeypatch.setattr(
            project_notes, "handle_note_tags_update", mock_handle_note_tags_update
        )

        response = test_app_without_db.patch(
            "/projects/1/notes/1", data=json.dumps(test_request_payload)
        )

        # assert that function with no return value was called
        mock_handle_note_tags_update.assert_called_once()

        # assert response
        assert response.status_code == 200
        assert response.json()["note_id"] == 1
        assert response.json()["project_id"] == 1
        assert response.json()["note_name"] == "test_name"
        assert response.json()["note_author"] == "test_author"
        assert response.json()["note_publication_details"] == "test_publication_details"
        assert response.json()["note_publication_year"] == 1900
        assert response.json()["note_comments"] == "test_comments"
        assert response.json()["created_at"] == datetime(2024, 12, 1).isoformat()
        assert response.json()["note_tags"] == ["tag_3", "tag_4"]

    def test_patch_note_not_patching_if_project_does_not_exist(
        self, test_app_without_db, monkeypatch
    ):
        test_request_payload = {
            "name": "test_name",
        }

        async def mock_get_project_by_id(db_session, project_id):
            return False

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        response = test_app_without_db.patch(
            "projects/1/notes/1", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Project id not found"

    def test_patch_note_not_patching_if_note_does_not_exist(
        self, test_app_without_db, monkeypatch
    ):
        test_request_payload = {
            "name": "test_name",
        }

        async def mock_get_project_by_id(db_session, project_id):
            return True

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_note_by_id(note_id, db_session):
            return False

        monkeypatch.setattr(project_notes, "get_note_by_id", mock_get_note_by_id)

        response = test_app_without_db.patch(
            "projects/1/notes/1", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Note id not found"

    def test_patch_note_not_patching_if_note_does_not_belong_to_project(
        self, test_app_without_db, monkeypatch
    ):
        test_request_payload = {
            "name": "test_name",
        }

        async def mock_get_project_by_id(db_session, project_id):
            return True

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_note_by_id(note_id, db_session):
            class MockNote:
                project_id = 1

            mock_note = MockNote()
            return mock_note

        monkeypatch.setattr(project_notes, "get_note_by_id", mock_get_note_by_id)

        response = test_app_without_db.patch(
            "projects/999/notes/1", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 404
        assert (
            response.json()["detail"] == "The note id cannot be found for this project."
        )

    def test_patch_note_not_patching_note_name_if_it_already_exists_on_the_project(
        self, test_app_without_db, monkeypatch
    ):
        test_request_payload = {
            "name": "test_name",
        }

        async def mock_get_project_by_id(db_session, project_id):
            class MockProject:
                name = "project_1"

            mock_project = MockProject()
            return mock_project

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_note_by_id(note_id, db_session):
            class MockNote:
                project_id = 1
                name = "abc"

            mock_note = MockNote()
            return mock_note

        monkeypatch.setattr(project_notes, "get_note_by_id", mock_get_note_by_id)

        async def mock_get_note_by_name_and_project(note_name, project_id, db_session):
            return True

        monkeypatch.setattr(
            project_notes,
            "get_note_by_name_and_project",
            mock_get_note_by_name_and_project,
        )

        response = test_app_without_db.patch(
            "projects/1/notes/1", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Note name 'test_name' already exists on "
            "'project_1' project. Please select a unique note name and "
            "try again."
        )


class TestDeleteProjectNote:
    def test_delete_project_note_happy_path(self, test_app_without_db, monkeypatch):
        async def mock_get_project_by_id(db_session, project_id):
            return True

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_note_by_id(note_id, db_session):
            class MockNote:
                id = 1
                project_id = 1

            mock_note = MockNote()
            return mock_note

        monkeypatch.setattr(project_notes, "get_note_by_id", mock_get_note_by_id)

        mock_delete_note = AsyncMock()
        monkeypatch.setattr(project_notes, "delete_note", mock_delete_note)

        response = test_app_without_db.delete("/projects/1/notes/1")

        # assert function without return value was called correctly
        mock_delete_note.assert_called_once_with(note_id=1, db_session=ANY)

        # assert response
        assert response.status_code == 200
        assert response.json()["message"] == "Note deleted"

    def test_delete_note_does_not_delete_if_project_does_not_exist(
        self, test_app_without_db, monkeypatch
    ):
        async def mock_get_project_by_id(db_session, project_id):
            return False

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        response = test_app_without_db.delete("/projects/1/notes/1")

        assert response.status_code == 404
        assert response.json()["detail"] == "Project id not found"

    def test_delete_note_does_not_delete_if_it_does_not_exist(
        self, test_app_without_db, monkeypatch
    ):
        async def mock_get_project_by_id(db_session, project_id):
            return True

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_note_by_id(note_id, db_session):
            return False

        monkeypatch.setattr(project_notes, "get_note_by_id", mock_get_note_by_id)

        response = test_app_without_db.delete("/projects/1/notes/1")

        assert response.status_code == 404
        assert response.json()["detail"] == "Note id not found"

    def test_delete_note_does_not_delete_if_note_does_not_belong_to_project(
        self, test_app_without_db, monkeypatch
    ):
        async def mock_get_project_by_id(db_session, project_id):
            return True

        monkeypatch.setattr(project_notes, "get_project_by_id", mock_get_project_by_id)

        async def mock_get_note_by_id(note_id, db_session):
            class MockNote:
                project_id = 1

            mock_note = MockNote()
            return mock_note

        monkeypatch.setattr(project_notes, "get_note_by_id", mock_get_note_by_id)

        response = test_app_without_db.delete("/projects/2/notes/999")

        assert response.status_code == 404
        assert (
            response.json()["detail"] == "The note id cannot be found for this project."
        )
