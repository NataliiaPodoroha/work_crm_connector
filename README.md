# Work CRM Connector

**Work CRM Connector** is an integration service that connects Work.ua and KeyCRM to automate job application processing. Using the Work.ua API, it retrieves responses and processes applicant data, while the KeyCRM API ensures seamless creation and updating of CRM cards. The service also notifies administrators via email with a summary of changes after each processing cycle, streamlining recruitment workflows efficiently.

## Key Features

1. **Fetching Responses from Work.ua:**
- Retrieves new responses to the company's job postings on Work.ua.
- Supports filtering by creation date, phone number presence, and duplicate entries.

2. **CRM Integration:**
- Creates new CRM cards for responses that do not match any existing phone numbers.
- Updates existing CRM cards if new information is found in the responses.
- Attaches CV files to CRM cards:
- If a file is included in the response, it is uploaded and attached.
- If no file is included, a `.docx` CV is generated from the response text.

3. **Notifications:**
- Sends a summary report to the admin via email for created/updated cards.
- Supports future extensions for sending notifications to Telegram.

4. **Monitoring:**
- Uses Flower to monitor Celery tasks.

## System Requirements

- Python 3.11+
- Redis
- Docker and Docker Compose (for containerization)
- SMTP server for email notifications

## Project Components

### `tasks.py`
- Contains Celery tasks for processing responses.

### `clients/`
- `work.py`: Handles Work.ua API interactions.
- `crm.py`: Manages CRM API interactions.
- `notification.py`: Sends email notifications.

### `utils/`
- `cv_file_generator.py`: Generates CVs in `.docx` format.
- `redis.py`: Provides utilities for working with Redis.
- `work.py`: Includes utilities for response processing.

### `celery_worker.py`
- Configures the Celery worker.

### `config.py`
- Contains environment variables and general settings.

### Docker and Docker Compose
- Dockerfiles and configurations to run the service, Redis, and Flower.

## How to Use

### Monitor with Flower
- Flower is accessible at [http://localhost:5555](http://localhost:5555).

### Process Responses
- Celery automatically processes job responses every hour.

### Reports
- A summary of created/updated CRM cards is emailed to the admin specified in `.env`.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/NataliiaPodoroha/work_crm_connector.git
   cd work_crm_connector

2. **Setup Environment Variables:**


- Copy `.env.sample` to `.env`:
      ```bash
      cp .env.sample .env
      ```
- Update the `.env` file with your configuration details.
- Note: The `.env` file contains sensitive information. Make sure not to share it publicly.


3. **Install Dependencies:**


- Activate a virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows use `venv\Scripts\activate`
     ```
- Install the required packages:
     ```bash
     pip install -r requirements.txt
     ```
  
4. **Run the Application:**

- Build the Docker image:
     ```bash
     docker compose build
     ```


- Start the services using Docker Compose:
     ```bash
     docker compose up
     ```
