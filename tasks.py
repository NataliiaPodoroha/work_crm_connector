from datetime import datetime
from celery import shared_task

import config
from clients.work import WorkClient
from clients.crm import CRMClient, COVER_CUSTOM_FIELD_UUID, CardStatus
from utils.cv_file_generator import GENERATED_CV_FILE_NAME
from utils.redis import (
    filter_already_processed_responses,
    update_processed_responses_ids,
)
from utils.work import (
    attach_cv_from_workua,
    attach_cv_from_text,
)


@shared_task
def process_work_responses():
    work_client = WorkClient(
        url=config.WORK_API_URL,
        username=config.WORK_API_USERNAME,
        password=config.WORK_API_PASSWORD,
        user_agent=config.USER_AGENT,
    )
    crm_client = CRMClient(
        url=config.CRM_API_URL,
        api_key=config.CRM_API_KEY,
    )

    all_jobs = work_client.get_all_jobs()
    active_jobs = [job for job in all_jobs["items"] if job["active"] == 1]

    cards = crm_client.get_all_cards(pipeline_id=config.PIPELINE_ID)

    for job in active_jobs:
        responses = fetch_job_responses(work_client, job)
        responses = filter_already_processed_responses(responses, job["id"])

        # TODO add logging for processed responses

        for response in responses:
            process_response(work_client, crm_client, response, job, cards)

        update_processed_responses_ids(responses, job["id"])


def fetch_job_responses(work_client, job):
    all_responses = []
    job_publish_date = datetime.fromisoformat(job["date"])
    before_id = None

    while True:
        result = work_client.get_job_responses(job_id=job["id"], before_id=before_id)
        responses = result.get("items")
        if not responses:
            break

        all_responses.extend(responses)
        last_response_date = datetime.fromisoformat(responses[-1]["date"])

        if last_response_date < job_publish_date:
            all_responses = [
                response
                for response in all_responses
                if datetime.fromisoformat(response["date"]) >= job_publish_date
            ]
            break

        before_id = responses[-1]["id"]

    return all_responses


def process_response(work_client, crm_client, response, job, cards):
    phone = response.get("phone")
    card = next(
        (card for card in cards if card.get("contact", {}).get("phone") == phone), None
    )

    if not card:
        name = response.get("fio")
        email = response.get("email")
        cover = response.get("cover")

        card = crm_client.create_card(
            full_name=name,
            email=email,
            phone=phone,
            source="Work.ua",
            job_title=job["name"],
            cover=cover,
        )

    else:
        update_card(crm_client, card, response)

    attach_cv(work_client, crm_client, card, job["id"], response)


def update_card(crm_client, card, response):
    fields_to_update = {"status_id": CardStatus.LEAD}

    contact = card.get("contact", {})
    if not contact.get("email") and response.get("email"):
        fields_to_update["contact[email]"] = response["email"]
    if not contact.get("full_name") and response.get("fio"):
        fields_to_update["contact[full_name]"] = response["fio"]

    custom_fields = card.get("custom_fields", [])
    if not any(
        field for field in custom_fields if field.get("uuid") == COVER_CUSTOM_FIELD_UUID
    ):
        if response.get("cover"):
            fields_to_update["custom_fields"] = [
                {"uuid": COVER_CUSTOM_FIELD_UUID, "value": response["cover"]}
            ]

    crm_client.update_card(card["id"], fields_to_update)


def attach_cv(work_client, crm_client, card, job_id, response):
    with_file = response.get("with_file") == 1

    original_file_name = None
    if with_file:
        original_file_name = response.get("file_name")

    card_attachments = crm_client.get_attached_files(card["id"])
    card_attachments_names = [
        attachment["original_file_name"] for attachment in card_attachments
    ]

    if (
        original_file_name in card_attachments_names
        or GENERATED_CV_FILE_NAME in card_attachments_names
    ):
        return

    if with_file:
        attach_cv_from_workua(work_client, crm_client, card, job_id, response["id"])
    elif response.get("text"):
        attach_cv_from_text(crm_client, card, response["text"])
