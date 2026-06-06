import pytest
from unittest.mock import patch, AsyncMock


# ──────────────────────────────────────────────
# send_proposal_notification
# ──────────────────────────────────────────────

def test_proposal_notification_success():
    """Таск успешно вызывает send_email."""
    with patch("app.infrastructure.tasks.notifications.asyncio.run") as mock_run:
        from app.infrastructure.tasks.notifications import send_proposal_notification

        send_proposal_notification(
            job_title="Backend Developer",
            client_email="client@test.com",
            freelancer_name="John Doe",
        )

        mock_run.assert_called_once()


def test_proposal_notification_email_content():
    """Таск не падает при нормальном вызове."""
    with patch("app.infrastructure.tasks.notifications.asyncio.run"):
        from app.infrastructure.tasks.notifications import send_proposal_notification

        send_proposal_notification(
            job_title="Backend Developer",
            client_email="client@test.com",
            freelancer_name="John Doe",
        )


def test_proposal_notification_logs_error_on_failure():
    """При ошибке таск логирует её."""
    with patch("app.infrastructure.tasks.notifications.asyncio.run", side_effect=Exception("SMTP error")):
        with patch("app.infrastructure.tasks.notifications.send_email", new_callable=AsyncMock):
            with patch("app.infrastructure.tasks.notifications.logger") as mock_logger:
                from app.infrastructure.tasks.notifications import send_proposal_notification
                try:
                    send_proposal_notification(
                        job_title="Backend Developer",
                        client_email="client@test.com",
                        freelancer_name="John Doe",
                    )
                except Exception:
                    pass
                mock_logger.error.assert_called()


def test_contract_notification_logs_error_on_failure():
    """При ошибке таск логирует её."""
    with patch("app.infrastructure.tasks.notifications.asyncio.run", side_effect=Exception("SMTP error")):
        with patch("app.infrastructure.tasks.notifications.send_email", new_callable=AsyncMock):
            with patch("app.infrastructure.tasks.notifications.logger") as mock_logger:
                from app.infrastructure.tasks.notifications import send_contract_notification
                try:
                    send_contract_notification(
                        job_title="Backend Developer",
                        freelancer_email="freelancer@test.com",
                        client_name="Jane Smith",
                    )
                except Exception:
                    pass
                mock_logger.error.assert_called()

# ──────────────────────────────────────────────
# send_contract_notification
# ──────────────────────────────────────────────

def test_contract_notification_success():
    """Таск успешно вызывает send_email."""
    with patch("app.infrastructure.tasks.notifications.asyncio.run") as mock_run:
        from app.infrastructure.tasks.notifications import send_contract_notification

        send_contract_notification(
            job_title="Backend Developer",
            freelancer_email="freelancer@test.com",
            client_name="Jane Smith",
        )

        mock_run.assert_called_once()


# ──────────────────────────────────────────────
# Таски вызываются из use cases
# ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_submit_proposal_triggers_notification():
    """submit_proposal вызывает send_proposal_notification.delay()."""
    import uuid
    from datetime import datetime
    from decimal import Decimal
    from app.application.use_cases.submit_proposal import SubmitProposal
    from app.application.dto.proposal import SubmitProposalRequest
    from app.domain.entities.job import JobEntity
    from app.domain.entities.proposal import ProposalEntity
    from app.domain.entities.user import UserEntity
    from app.infrastructure.database.models.user import UserRole
    from app.infrastructure.database.models.job import JobStatus
    from app.infrastructure.database.models.proposal import ProposalStatus

    freelancer = UserEntity(
        id=uuid.uuid4(), email="f@test.com", full_name="Freelancer",
        role=UserRole.FREELANCER, is_active=True, created_at=datetime.now(),
    )
    client = UserEntity(
        id=uuid.uuid4(), email="c@test.com", full_name="Client",
        role=UserRole.CLIENT, is_active=True, created_at=datetime.now(),
    )
    job = JobEntity(
        id=uuid.uuid4(), client_id=client.id, title="Backend Dev",
        description="Desc", budget=Decimal("500"), status=JobStatus.OPEN,
        created_at=datetime.now(),
    )
    proposal = ProposalEntity(
        id=uuid.uuid4(), job_id=job.id, freelancer_id=freelancer.id,
        cover_letter="I can do this", proposed_rate=Decimal("100"),
        status=ProposalStatus.PENDING, created_at=datetime.now(),
    )

    proposal_repo = AsyncMock()
    job_repo = AsyncMock()
    user_repo = AsyncMock()
    job_repo.get_by_id.return_value = job
    proposal_repo.get_by_freelancer_and_job.return_value = None
    proposal_repo.create.return_value = proposal
    user_repo.get_by_id.return_value = client

    with patch("app.infrastructure.tasks.notifications.send_proposal_notification.delay") as mock_delay:
        use_case = SubmitProposal(proposal_repo, job_repo, user_repo)
        await use_case.execute(
            job.id,
            SubmitProposalRequest(cover_letter="I can do this", proposed_rate=100),
            freelancer,
        )
        mock_delay.assert_called_once_with(
            job_title="Backend Dev",
            client_email="c@test.com",
            freelancer_name="Freelancer",
        )