import asyncio
from app.core.celery import celery_app
from app.core.logging import logger
from app.infrastructure.email.sender import send_email


@celery_app.task(name="send_proposal_notification", bind=True, max_retries=3)
def send_proposal_notification(self, job_title: str, client_email: str, freelancer_name: str):
    """
    Уведомляет клиента что freelancer подал proposal на его вакансию.
    Вызывается из submit_proposal use case.
    """
    subject = f"Новый отклик на вашу вакансию: {job_title}"
    body = (
        f"Здравствуйте!\n\n"
        f"Фрилансер {freelancer_name} подал заявку на вашу вакансию «{job_title}».\n\n"
        f"Войдите в платформу чтобы просмотреть заявку.\n\n"
        f"С уважением,\nFreelance Platform"
    )
    try:
        asyncio.run(send_email(to=client_email, subject=subject, body=body))
        logger.info(f"Proposal notification sent to {client_email}")
    except Exception as exc:
        logger.error(f"Proposal notification failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="send_contract_notification", bind=True, max_retries=3)
def send_contract_notification(self, job_title: str, freelancer_email: str, client_name: str):
    """
    Уведомляет freelancer что его proposal принят и контракт создан.
    Вызывается из update_proposal_status use case.
    """
    subject = f"Ваша заявка принята: {job_title}"
    body = (
        f"Здравствуйте!\n\n"
        f"Клиент {client_name} принял вашу заявку на вакансию «{job_title}».\n"
        f"Контракт успешно создан.\n\n"
        f"Войдите в платформу чтобы просмотреть детали контракта.\n\n"
        f"С уважением,\nFreelance Platform"
    )
    try:
        asyncio.run(send_email(to=freelancer_email, subject=subject, body=body))
        logger.info(f"Contract notification sent to {freelancer_email}")
    except Exception as exc:
        logger.error(f"Contract notification failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
