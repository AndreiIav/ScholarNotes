import json
from datetime import datetime, timezone


class TestPostProjectNotes:
    def test_post_project_notes_happy_path(
        self, test_app, add_project_data, delete_project_table_data
    ):
        test_request_payload = {
            "note_name": "test_name",
            "note_author": "test_author",
            "note_publication_details": "test_publication_details",
            "note_publication_year": 1889,
            "note_comments": "test_comments",
            "note_tags": [],
        }
        test_project_id = 1

        response = test_app.post(
            f"projects/{test_project_id}/notes/", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 200
        assert response.json()["note_id"]
        assert response.json()["project_id"] == test_project_id
        assert response.json()["note_name"] == "test_name"
        assert response.json()["note_author"] == "test_author"
        assert response.json()["note_publication_details"] == "test_publication_details"
        assert response.json()["note_publication_year"] == 1889
        assert response.json()["note_comments"] == "test_comments"
        assert response.json()["note_tags"] == []
        assert response.json()["created_at"]

        created_at = response.json()["created_at"]
        # create a datetime object from the "created_at" string
        created_at_datetime = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        # make it UTC "aware"
        created_at_datetime = created_at_datetime.replace(tzinfo=timezone.utc)
        # get the difference between the current UTC aware datetime and the one
        # retrieved from the response
        seconds_diff = datetime.now(timezone.utc) - created_at_datetime
        # it shouldn't be more than one second
        assert seconds_diff.seconds <= 1

    def test_post_project_notes_cannot_post_if_project_does_not_exist(self, test_app):
        test_request_payload = {
            "note_name": "test_name",
            "note_author": "test_author",
            "note_publication_details": "test_publication_details",
            "note_publication_year": 1889,
            "note_comments": "test_comments",
            "note_tags": [],
        }

        response = test_app.post(
            "projects/1/notes/", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Project id not found"

    def test_post_project_notes_cannot_add_existing_note_name_for_same_project(
        self, test_app, add_project_notes_data, delete_project_notes_data
    ):
        test_request_payload = {
            "note_name": "note_1",
            "note_author": "test_author",
            "note_publication_details": "test_publication_details",
            "note_publication_year": 1889,
            "note_comments": "test_comments",
            "note_tags": [],
        }

        response = test_app.post(
            "projects/1/notes/", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            f"Note '{test_request_payload['note_name']}' already exists for"
            " project 'project_1'. Please select a unique note"
            " name for this project."
        )

    def test_post_project_notes_handles_received_inexistent_tags(
        selft,
        test_app,
        add_project_notes_data,
        delete_project_notes_data,
        delete_tags_data,
    ):
        test_request_payload = {
            "note_name": "test_name",
            "note_author": "test_author",
            "note_publication_details": "test_publication_details",
            "note_publication_year": 1889,
            "note_comments": "test_comments",
            "note_tags": ["tag_1", "tag_2"],
        }

        response = test_app.post(
            "projects/1/notes/", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 200
        assert len(response.json()["note_tags"]) == 2
        for tag in test_request_payload["note_tags"]:
            assert tag in response.json()["note_tags"]

    def test_post_project_notes_handles_received_already_existent_tags(
        selft,
        test_app,
        add_project_notes_data,
        add_tags_data,
        delete_project_notes_data,
        delete_tags_data,
    ):
        test_request_payload = {
            "note_name": "test_name",
            "note_author": "test_author",
            "note_publication_details": "test_publication_details",
            "note_publication_year": 1889,
            "note_comments": "test_comments",
            "note_tags": ["tag_1", "tag_2"],
        }

        response = test_app.post(
            "projects/1/notes/", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 200
        assert len(response.json()["note_tags"]) == 2
        for tag in test_request_payload["note_tags"]:
            assert tag in response.json()["note_tags"]

    def test_post_project_notes_handles_received_inexistent_and_existent_tags(
        selft,
        test_app,
        add_project_notes_data,
        add_tags_data,
        delete_project_notes_data,
        delete_tags_data,
    ):
        test_request_payload = {
            "note_name": "test_name",
            "note_author": "test_author",
            "note_publication_details": "test_publication_details",
            "note_publication_year": 1889,
            "note_comments": "test_comments",
            "note_tags": ["tag_1", "tag_2", "tag_3", "tag_4"],
        }

        response = test_app.post(
            "projects/1/notes/", data=json.dumps(test_request_payload)
        )

        assert response.status_code == 200
        assert len(response.json()["note_tags"]) == 4
        for tag in test_request_payload["note_tags"]:
            assert tag in response.json()["note_tags"]
