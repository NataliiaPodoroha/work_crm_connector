import json
import redis
import config

redis_client = redis.StrictRedis.from_url(config.REDIS_URL)


def get_processed_responses(job_id):
    data = redis_client.get(f"processed_responses_{job_id}")
    return json.loads(data) if data else []


def filter_already_processed_responses(responses, job_id):
    already_processed_responses = get_processed_responses(job_id)
    return [
        response
        for response in responses
        if response["id"] not in already_processed_responses
    ]


def update_processed_responses_ids(responses, job_id):
    already_processed_responses = get_processed_responses(job_id)
    processed_responses_ids = [response["id"] for response in responses]
    all_processed_responses = set(already_processed_responses + processed_responses_ids)

    redis_client.set(
        f"processed_responses_{job_id}",
        json.dumps(list(all_processed_responses)),
    )
