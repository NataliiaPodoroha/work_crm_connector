import requests
from requests.auth import HTTPBasicAuth


MAX_RESPONSES_LIMIT = 50
SORT_DESC = 0


class WorkClientException(Exception):
    pass


class WorkClient:
    def __init__(self, url: str, username: str, password: str, user_agent: str):
        self.url = url
        self.auth = HTTPBasicAuth(username, password)
        self.user_agent = user_agent

    def _make_request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.url}{endpoint}"
        headers = {"User-Agent": self.user_agent}
        try:
            response = requests.request(
                method=method, url=url, headers=headers, auth=self.auth, **kwargs
            )

            if not response.ok:
                raise WorkClientException("Error while making request to work.ua API")

            return response

        except requests.RequestException:
            raise WorkClientException(
                "Error while making request to work.ua API: network error"
            )

    def get_all_jobs(self):
        response = self._make_request("GET", "jobs/my")
        return response.json()

    def get_job_responses(self, job_id, before_id=None):
        params = {"limit": MAX_RESPONSES_LIMIT, "sort": SORT_DESC}
        if before_id:
            params["before_id"] = before_id

        response = self._make_request("GET", f"jobs/{job_id}/responses", params=params)
        return response.json()

    def download_cv(self, job_id, response_id):
        endpoint = f"response_files/{job_id}/{response_id}"
        return self._make_request("GET", endpoint)
