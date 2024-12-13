import datetime

from app.api.routers import projects


def test_get_project(test_app, monkeypatch):
    test_data = [
        {
            "id": 1,
            "name": "test_name",
            "comment": "test_comment",
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        },
        {
            "id": 2,
            "name": "test_name_2",
            "comment": "test_comment_2",
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        },
    ]

    async def mock_get_project(db_session):
        return test_data

    monkeypatch.setattr(projects, "get_all_projects", mock_get_project)

    response = test_app.get("/projects/")

    assert response.status_code == 200
