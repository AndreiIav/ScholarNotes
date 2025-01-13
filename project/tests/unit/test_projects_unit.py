from datetime import datetime

from app.api.routers import projects


def test_get_all_projects(test_app, monkeypatch):
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


def test_post_project():
    pass
