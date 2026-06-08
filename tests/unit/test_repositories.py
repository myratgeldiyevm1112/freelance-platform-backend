import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.infrastructure.repositories.skill_repository import SkillRepository
from app.infrastructure.repositories.dispute_repository import DisputeRepository
from app.infrastructure.database.models.skill import Skill, UserSkill  # реальные классы
from app.domain.exceptions import NotFoundError
from app.infrastructure.database.models.dispute import DisputeStatus


# ─── Helpers ────────────────────────────────────────────────────────────────

def make_skill_model(name="python"):
    m = MagicMock(spec=Skill)
    m.id = uuid.uuid4()
    m.name = name
    m.created_at = datetime.now()
    return m


def make_user_skill_model(user_id, skill_id):
    m = MagicMock(spec=UserSkill)
    m.id = uuid.uuid4()
    m.user_id = user_id
    m.skill_id = skill_id
    m.created_at = datetime.now()
    return m


def make_dispute_model(status=DisputeStatus.OPEN):
    m = MagicMock()
    m.id = uuid.uuid4()
    m.contract_id = uuid.uuid4()
    m.opened_by = uuid.uuid4()
    m.reason = "Payment issue"
    m.status = status
    m.resolution_note = None
    m.resolved_by = None
    m.created_at = datetime.now()
    m.updated_at = datetime.now()
    return m


def make_session():
    s = AsyncMock()
    s.execute = AsyncMock()
    s.add = MagicMock()
    s.flush = AsyncMock()
    s.commit = AsyncMock()
    s.refresh = AsyncMock()
    s.delete = AsyncMock()
    return s


def scalar_result(value):
    r = MagicMock()
    r.scalar_one_or_none.return_value = value
    return r


def scalars_result(values):
    r = MagicMock()
    r.scalars.return_value.all.return_value = values
    return r


# ─── SkillRepository ─────────────────────────────────────────────────────────

class TestSkillRepository:

    @pytest.mark.asyncio
    async def test_get_or_create_skill_existing(self):
        skill = make_skill_model("python")
        session = make_session()
        session.execute.return_value = scalar_result(skill)

        repo = SkillRepository(session)
        result = await repo.get_or_create_skill("Python")

        assert result.name == "python"
        session.add.assert_not_called()
        session.flush.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_or_create_skill_normalizes_name(self):
        skill = make_skill_model("python")
        session = make_session()
        session.execute.return_value = scalar_result(skill)

        repo = SkillRepository(session)
        result = await repo.get_or_create_skill("  PYTHON  ")

        assert result.name == "python"

    @pytest.mark.asyncio
    async def test_get_or_create_skill_creates_new(self):
        """Если скилл не существует — создаётся новый через реальный Skill()."""
        session = make_session()
        session.execute.return_value = scalar_result(None)

        # Не патчим Skill — пусть репозиторий создаёт реальный объект.
        # session.add будет вызван с реальным инстансом Skill.
        repo = SkillRepository(session)
        result = await repo.get_or_create_skill("django")

        # add вызван один раз с экземпляром Skill
        session.add.assert_called_once()
        added_obj = session.add.call_args[0][0]
        assert isinstance(added_obj, Skill)
        assert added_obj.name == "django"
        session.flush.assert_called_once()
        assert result.name == "django"

    @pytest.mark.asyncio
    async def test_add_skills_to_user_new_skill(self):
        """Добавление нового скилла пользователю."""
        user_id = uuid.uuid4()
        skill = make_skill_model("fastapi")
        session = make_session()

        session.execute.side_effect = [
            scalar_result(skill),   # get_or_create — скилл найден
            scalar_result(None),    # user_skill не существует
        ]

        repo = SkillRepository(session)
        result = await repo.add_skills_to_user(user_id, ["fastapi"])

        assert len(result) == 1
        assert result[0].skill_name == "fastapi"

        session.add.assert_called_once()
        added_obj = session.add.call_args[0][0]
        assert isinstance(added_obj, UserSkill)
        assert added_obj.user_id == user_id
        assert added_obj.skill_id == skill.id

    @pytest.mark.asyncio
    async def test_add_skills_to_user_skip_duplicate(self):
        user_id = uuid.uuid4()
        skill = make_skill_model("python")
        existing_us = make_user_skill_model(user_id, skill.id)
        session = make_session()

        session.execute.side_effect = [
            scalar_result(skill),
            scalar_result(existing_us),
        ]

        repo = SkillRepository(session)
        result = await repo.add_skills_to_user(user_id, ["python"])

        assert result == []
        session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_skills_returns_list(self):
        user_id = uuid.uuid4()
        skill = make_skill_model("react")
        us = make_user_skill_model(user_id, skill.id)
        session = make_session()

        mock_result = MagicMock()
        mock_result.all.return_value = [(us, skill)]
        session.execute.return_value = mock_result

        repo = SkillRepository(session)
        result = await repo.get_user_skills(user_id)

        assert len(result) == 1
        assert result[0].skill_name == "react"

    @pytest.mark.asyncio
    async def test_get_user_skills_empty(self):
        session = make_session()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        session.execute.return_value = mock_result

        repo = SkillRepository(session)
        result = await repo.get_user_skills(uuid.uuid4())

        assert result == []

    @pytest.mark.asyncio
    async def test_remove_user_skill_success(self):
        user_id = uuid.uuid4()
        skill_id = uuid.uuid4()
        us = make_user_skill_model(user_id, skill_id)
        session = make_session()
        session.execute.return_value = scalar_result(us)

        repo = SkillRepository(session)
        await repo.remove_user_skill(user_id, skill_id)

        session.delete.assert_called_once_with(us)
        session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_user_skill_not_found(self):
        session = make_session()
        session.execute.return_value = scalar_result(None)

        repo = SkillRepository(session)
        await repo.remove_user_skill(uuid.uuid4(), uuid.uuid4())

        session.delete.assert_not_called()


# ─── DisputeRepository ───────────────────────────────────────────────────────

class TestDisputeRepository:

    @pytest.mark.asyncio
    async def test_create_dispute(self):
        contract_id = uuid.uuid4()
        opened_by = uuid.uuid4()
        dispute_model = make_dispute_model()
        dispute_model.contract_id = contract_id
        dispute_model.opened_by = opened_by

        session = make_session()
        session.refresh.side_effect = lambda d: None

        with patch("app.infrastructure.repositories.dispute_repository.Dispute") as MockDispute:
            MockDispute.return_value = dispute_model
            repo = DisputeRepository(session)
            result = await repo.create(contract_id, opened_by, "Payment issue")

        session.add.assert_called_once_with(dispute_model)
        session.commit.assert_called_once()
        session.refresh.assert_called_once_with(dispute_model)
        assert result.contract_id == contract_id

    @pytest.mark.asyncio
    async def test_get_by_id_found(self):
        dispute = make_dispute_model()
        session = make_session()
        session.execute.return_value = scalar_result(dispute)

        repo = DisputeRepository(session)
        result = await repo.get_by_id(dispute.id)

        assert result is not None
        assert result.id == dispute.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        session = make_session()
        session.execute.return_value = scalar_result(None)

        repo = DisputeRepository(session)
        result = await repo.get_by_id(uuid.uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_returns_list(self):
        disputes = [make_dispute_model(), make_dispute_model()]
        session = make_session()
        session.execute.return_value = scalars_result(disputes)

        repo = DisputeRepository(session)
        result = await repo.get_all(limit=10, offset=0)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_all_empty(self):
        session = make_session()
        session.execute.return_value = scalars_result([])

        repo = DisputeRepository(session)
        result = await repo.get_all()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_by_contract_id(self):
        contract_id = uuid.uuid4()
        d1 = make_dispute_model()
        d1.contract_id = contract_id
        session = make_session()
        session.execute.return_value = scalars_result([d1])

        repo = DisputeRepository(session)
        result = await repo.get_by_contract_id(contract_id)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_resolve_dispute_success(self):
        admin_id = uuid.uuid4()
        dispute = make_dispute_model(status=DisputeStatus.OPEN)
        session = make_session()
        session.execute.return_value = scalar_result(dispute)

        repo = DisputeRepository(session)
        result = await repo.resolve(
            dispute_id=dispute.id,
            status=DisputeStatus.RESOLVED_REFUND,
            resolved_by=admin_id,
            resolution_note="Refunded",
        )

        assert dispute.status == DisputeStatus.RESOLVED_REFUND
        assert dispute.resolved_by == admin_id
        assert dispute.resolution_note == "Refunded"
        session.commit.assert_called_once()
        session.refresh.assert_called_once_with(dispute)

    @pytest.mark.asyncio
    async def test_resolve_dispute_not_found(self):
        session = make_session()
        session.execute.return_value = scalar_result(None)

        repo = DisputeRepository(session)

        with pytest.raises(NotFoundError):
            await repo.resolve(
                dispute_id=uuid.uuid4(),
                status=DisputeStatus.RESOLVED_RELEASE,
                resolved_by=uuid.uuid4(),
            )

    @pytest.mark.asyncio
    async def test_resolve_dispute_without_note(self):
        admin_id = uuid.uuid4()
        dispute = make_dispute_model()
        session = make_session()
        session.execute.return_value = scalar_result(dispute)

        repo = DisputeRepository(session)
        await repo.resolve(
            dispute_id=dispute.id,
            status=DisputeStatus.RESOLVED_RELEASE,
            resolved_by=admin_id,
            resolution_note=None,
        )

        assert dispute.resolution_note is None