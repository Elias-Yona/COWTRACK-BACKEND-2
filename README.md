# SETUP

- The backend for Cowtrack

- To install dependencies:

```bash
poetry run python manage.py migrate
```

- To create JWT auth and refresh tokens

```bash
http POST https://localhost:8000/auth/jwt/create/ username=[your_username] password=[your_passwrd]
```

- To use the JWT access token in requests:

```bash
http GET  https://localhost:8000/users/customers "Authorization:Bearer [your_access_token]"
```

- To run the server in development:

```bash
poetry run python manage.py runserver --settings=cowtrack.settings.local
```