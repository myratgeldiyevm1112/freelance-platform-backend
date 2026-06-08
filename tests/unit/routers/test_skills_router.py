import uuid
import pytest
from unittest.mock import AsyncMock, patch
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.user import UserRole
from datetime import datetime

# Фиктивный текущий пользователь для прохождения Depends(get_current_user)
mock_user = UserEntity(
    id=uuid.uuid4(),
    email="skills_tester@example.com",
    full_name="Skills Tester",
    role=UserRole.FREELANCER,
    is_active=True,
    created_at=datetime.now()
)

@pytest.fixture
def override_dependencies():
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: AsyncMock()
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
@patch("app.api.v1.routers.skills.AddUserSkills")
async def test_add_skills_router_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = {
        "skills": [
            {"id": str(uuid.uuid4()), "skill_id": str(uuid.uuid4()), "skill_name": "python"},
            {"id": str(uuid.uuid4()), "skill_id": str(uuid.uuid4()), "skill_name": "fastapi"}
        ]
    }
    mock_use_case_class.return_value = mock_use_case

    # Act
    response = await client.post(
        "/api/v1/users/me/skills",
        json={"skills": ["python", "fastapi"]}
    )

    # Assert
    assert response.status_code == 200
    assert len(response.json()["skills"]) == 2
    mock_use_case_class.return_value.execute.assert_called_once()

@pytest.mark.asyncio
@patch("app.api.v1.routers.skills.GetUserSkills")
async def test_get_skills_router_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = {
        "skills": [{"id": str(uuid.uuid4()), "skill_id": str(uuid.uuid4()), "skill_name": "python"}]
    }
    mock_use_case_class.return_value = mock_use_case

    # Act
    response = await client.get("/api/v1/users/me/skills")

    # Assert
    assert response.status_code == 200
    assert response.json()["skills"][0]["skill_name"] == "python"
    mock_use_case_class.return_value.execute.assert_called_once_with(mock_user.id)

@pytest.mark.asyncio
@patch("app.api.v1.routers.skills.RemoveUserSkill")
async def test_remove_skill_router_success(mock_use_case_class, override_dependencies, client):
    # Arrange
    mock_use_case = AsyncMock()
    mock_use_case.execute.return_value = None
    mock_use_case_class.return_value = mock_use_case
    skill_uuid = uuid.uuid4()

    # Act
    response = await client.delete(f"/api/v1/users/me/skills/{skill_uuid}")

    # Assert
    assert response.status_code == 204
    mock_use_case_class.return_value.execute.assert_called_once_with(mock_user.id, skill_uuid)