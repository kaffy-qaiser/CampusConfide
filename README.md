# Campus Confide

---

Campus Confide is a whistle-blower application designed to help report any unethical actions conducted by students, teaching assistants, or professors within a university campus. The application ensures anonymity and security for the users, providing a safe platform to report misconduct.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- Anonymous reporting of unethical actions
- Secure storage of reports
- Google OAuth integration for user creation
- Continuous testing through GitHub
- Deployed on Heroku with cloud storage on AWS S3
- Utilizes PostgreSQL for database management

## Tech Stack

- **Backend:** Django, Python
- **Database:** PostgreSQL
- **Cloud Storage:** AWS S3
- **Hosting:** Heroku
- **Authentication:** Google OAuth
- **Development Methodology:** Agile

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/kaffy-qaiser/CampusConfide.git
   cd CampusConfide
   ```

2. **Create a virtual environment and activate it:**

   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the PostgreSQL database:**

   Create a new PostgreSQL database and update the `DATABASES` settings in `settings.py` with your database credentials.

5. **Set up AWS S3 for media storage:**

   Configure your AWS S3 bucket and update the `settings.py` with your AWS credentials and bucket name.

6. **Run the database migrations:**

   ```bash
   python manage.py migrate
   ```

7. **Create a superuser to access the Django admin:**

   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server:**

   ```bash
   python manage.py runserver
   ```

## Usage

1. **Access the application:**

   Open your web browser and navigate to `http://127.0.0.1:8000`.

2. **Report an Incident:**

   Follow the prompts on the website to anonymously report any unethical actions.

3. **Admin Access:**

   Log in to the Django admin panel at `http://127.0.0.1:8000/admin` using the superuser credentials to manage reports.

## Contributing

We welcome contributions from the community. If you would like to contribute, please follow these steps:

1. **Fork the repository**
2. **Create a new branch** (`git checkout -b feature-branch`)
3. **Commit your changes** (`git commit -am 'Add new feature'`)
4. **Push to the branch** (`git push origin feature-branch`)
5. **Create a new Pull Request**

Please ensure your code adheres to our coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
---

