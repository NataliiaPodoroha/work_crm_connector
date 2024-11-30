import magic
from requests.utils import parse_header_links
from utils.cv_file_generator import create_cv_document


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
