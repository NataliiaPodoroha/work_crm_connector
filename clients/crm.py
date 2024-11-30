import requests
import config

COVER_CUSTOM_FIELD_UUID = "LD_1042"


class CardStatus:
    LEAD = "29"
    FIRST_CONTACT = "62"
    NO_CONTACT = "60"
    RELEVANT_SALE = "30"
    MIT = "31"
    LEARN = "50"
    INTERVIEW = "38"
    INTERN = "39"
    TEST_PERIOD = "64"
    WORK = "65"
    HIRED = "32"
    NO_ANSWER = "129"


class CRMClientException(Exception):
    pass


class CRMClient:
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key

    def _make_request(self, method: str, endpoint: str, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        url = f"{self.url}{endpoint}"

        try:
            response = requests.request(
                method=method, url=url, headers=headers, **kwargs
            )

            if not response.ok:
                raise CRMClientException("Error while making request to CRM API")
            return response.json()

        except requests.RequestException as e:
            raise CRMClientException(
                "Error while making request to CRM API: network error"
            )

    def get_all_cards(self, pipeline_id: int):
        include_statuses = ",".join(
            [
                CardStatus.LEAD,
                CardStatus.FIRST_CONTACT,
                CardStatus.NO_CONTACT,
                CardStatus.RELEVANT_SALE,
                CardStatus.MIT,
                CardStatus.LEARN,
                CardStatus.INTERVIEW,
                CardStatus.INTERN,
                CardStatus.TEST_PERIOD,
                CardStatus.WORK,
                CardStatus.HIRED,
                CardStatus.NO_ANSWER,
            ]
        )

        params = {
            "filter[pipeline_id]": pipeline_id,
            "filter[status_id]": include_statuses,
            "include": "contact.client,custom_fields",
            "limit": 50,
        }
        all_cards = []
        current_page = 1

        while True:
            params["page"] = current_page
            response = self._make_request("GET", "/pipelines/cards", params=params)
            all_cards.extend(response.get("data", []))
            next_page_url = response.get("next_page_url")
            if not next_page_url:
                break
            current_page += 1

        return all_cards

    def create_card(
        self,
        full_name: str,
        email: str,
        phone: str,
        source: str,
        job_title: str,
        cover: str = None,
    ):

        custom_fields = [{"uuid": "LD_1033", "value": source}]

        if cover:
            custom_fields.append({"uuid": "LD_1042", "value": cover})

        crm_data = {
            "title": f"Work.ua | {job_title}",
            "pipeline_id": config.PIPELINE_ID,
            "source_id": config.SOURCE_ID,
            "contact": {"full_name": full_name, "email": email, "phone": phone},
            "custom_fields": custom_fields,
        }
        return self._make_request("POST", "/pipelines/cards", json=crm_data)

    def update_card(self, card_id: int, updated_fields: dict):
        return self._make_request(
            "PUT", f"/pipelines/cards/{card_id}", json=updated_fields
        )

    def get_attached_files(self, card_id):
        endpoint = f"/storage/attachment/pipelines/{card_id}"
        return self._make_request("GET", endpoint)

    def upload_file(self, file_name, file_content, mime_type):
        endpoint = "/storage/upload"
        files = {"file": (file_name, file_content, mime_type)}
        return self._make_request("POST", endpoint, files=files)

    def attach_file_to_card(self, card_id: int, file_id: str):
        endpoint = f"/pipelines/cards/{card_id}/attachment/{file_id}"
        return self._make_request("POST", endpoint)
