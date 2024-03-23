# paw - Ticket System

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
<a href='https://ko-fi.com/alexottr' target='_blank'><img height='35' style='border:0px;height:24px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com'></a>

🚀 paw is a comprehensive and open source ticket management system designed to streamline issue tracking and resolution processes for organizations. It provides a centralized platform for users to submit, track, and manage tickets or requests, facilitating efficient communication and collaboration among team members.

## Features

- **Ticket Creation and Submission:** Users can create and submit tickets with detailed information about the issue, including title, description, priority, and category and file attachments.

- **Ticket Assignment and Ownership:** Tickets can be assigned to specific individuals or teams responsible for resolution, allowing for clear ownership and accountability.

- **Communication and Collaboration:** Threaded communication enables seamless collaboration among team members, with the ability to add (internal) comments, attachments, and updates to tickets.

- **Security and Access Control:** Secure user authentication, access controls, and audit trails ensure data privacy and compliance with organizational policies and regulations. You can create teams and restrict access of ticket categories to them.

## Installation

### As a Developer

1. Clone the repository:

```bash
git clone https://github.com/aottr/paw.git
```

2. Install dependencies:

```bash
poetry install
```

3. Configure settings:
   Copy `.env.example` to `.env` and update the configuration variables as needed.

4. Run migrations:

```bash
poetry run python manage.py migrate
```

5. Start the development server:

```bash
poetry run python manage.py runserver
```

### Docker / OCI Container

The Project contains a [Dockerfile](Dockerfile) that can be built locally or in a pipeline. I also provide the latest state of the `main` branch as an image

## Usage

- Access the application through `http://localhost:8000`.
- Register an account or log in with existing credentials.
- Start creating and managing tickets based on your role and permissions.

## Contributing

🙌 Contributions are welcome! Please follow the [guidelines](CONTRIBUTING.md).

## License

This project is licensed under the [MIT License](LICENSE).
