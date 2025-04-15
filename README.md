# Voting System

A Django-based web application for creating and managing polls and voting.

## Features

- User authentication (register, login, logout)
- Create and manage polls
- Vote on polls
- View poll results with visual representations
- Admin interface for managing users and polls
- Department management

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd voting-system
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:
```
pip install -r requirements.txt
```

4. Run migrations:
```
python manage.py migrate
```

5. Start the development server:
```
python manage.py runserver
```

6. Access the application at http://127.0.0.1:8000/

## Default Admin User

When you start the application for the first time, a default admin user will be created:
- Username: admin
- Password: adminpassword123

It's recommended to change the password after the first login.

## Usage

### User Registration
- Navigate to the "Sign Up" page to create a new account.
- Verify your account via the link sent to your email (if email verification is enabled).

### Creating Polls
- Log in to your account.
- Click on "Create Poll" in the navigation menu.
- Fill in the poll details and add choices.
- Submit the form to create your poll.

### Voting
- Browse the list of available polls on the homepage.
- Click on a poll to view its details.
- Select your preferred option and click "Vote".

### Admin Features
- Log in with an admin account.
- Access the admin panel via the dropdown menu.
- Manage users, polls, and departments.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 