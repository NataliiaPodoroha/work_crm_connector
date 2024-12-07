import magic
from collections import defaultdict
from datetime import datetime
from requests.utils import parse_header_links
from utils.cv_file_generator import create_cv_document


def filter_responses_without_phone(responses):
    return [response for response in responses if response.get("phone")]


def filter_duplicate_responses(responses):
    phone_map = defaultdict(list)

    for response in responses:
        phone = response["phone"]
        phone_map[phone].append(response)

    latest_responses = []
    for phone, response_group in phone_map.items():
        latest_response = max(
            response_group, key=lambda r: datetime.fromisoformat(r["date"])
        )
        latest_responses.append(latest_response)

    return latest_responses


def get_file_info(response, default_name="unknown"):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(response.content)

    file_name = default_name

    content_disposition = response.headers.get("Content-Disposition", "")
    content_disposition_params = parse_header_links(content_disposition)

    if content_disposition_params:
        file_name = content_disposition_params[0].get("filename", default_name)

    return file_name, mime_type


def attach_cv_from_workua(work_client, crm_client, card, job_id, response_id):
    cv_response = work_client.download_cv(job_id, response_id)

    file_name, mime_type = get_file_info(cv_response)

    upload_response = crm_client.upload_file(
        file_name=file_name,
        file_content=cv_response.content,
        mime_type=mime_type,
    )
    crm_client.attach_file_to_card(card["id"], upload_response["id"])


def attach_cv_from_text(crm_client, card, text):
    file_stream, file_name = create_cv_document(text)
    mime_type = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    upload_response = crm_client.upload_file(file_name, file_stream, mime_type)
    crm_client.attach_file_to_card(card["id"], upload_response["id"])
