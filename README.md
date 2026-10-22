# AutoRia Clone API

AutoRia Clone is a REST API for a car marketplace built with Python, Django and Django REST Framework.

The application allows users to create car listings, search for vehicles, manage accounts, purchase a simulated Premium subscription and view listing analytics.

The project includes automatic listing moderation, currency conversion using PrivatBank exchange rates, role-based permissions and Docker containerization.

## Technologies

- Python 3.13
- Django 6.1
- Django REST Framework
- MySQL 8.4
- SQLite for local development
- JWT Authentication
- SimpleJWT
- django-filter
- PrivatBank API
- Docker
- Docker Compose
- Gunicorn
- Postman

## Project Structure

```text
auto-ria-django-kr/
├── analytics/
├── cars/
├── config/
├── currency/
├── listings/
├── users/
├── manage.py
├── requirements.txt
├── requirements-docker.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.docker.example
├── AutoRia.postman_collection.json
└── README.md
```

## Features

### Authentication and Users

- User registration
- JWT login and token refresh
- User profile endpoint
- Role-based permissions
- User blocking and unblocking
- Administrator-only manager creation

### User Roles

The application supports four roles:

1. Buyer — views available car listings.
2. Seller — creates and manages personal listings.
3. Manager — reviews suspicious listings and blocks users.
4. Administrator — manages the platform and its users.

Django Groups and custom permissions are used to separate access rights.

The architecture can be extended with additional roles for car dealerships.

### Account Types

Basic:
- Default account type
- One non-inactive car listing
- No access to Premium analytics

Premium:
- Unlimited car listings
- Listing view statistics
- Regional average car price
- Ukrainian average car price

Premium activation is implemented as a mock purchase.

No real payment is processed.

### Car Catalog

The application supports:

- Car brands
- Car models
- Filtering models by brand
- Requests for missing brands
- Requests for missing models
- Manager review of catalog requests

### Car Listings

Sellers can create, edit and delete car listings.

Listing information includes:

- Brand
- Model
- Title
- Description
- Manufacturing year
- Mileage
- Price
- Currency
- Region
- Moderation status
- Optional contact email provided by the seller
- Original listing price and initial exchange-rate snapshots

Only active listings appear in the public catalog. Buyers can email sellers when a contact email was provided.

### Filtering and Search

The API supports filtering by:

- Brand
- Model
- Region
- Currency
- Minimum and maximum price
- Minimum and maximum year
- Minimum and maximum mileage

Full-text-style search is available for listing titles, descriptions, brands and models.

Sorting is supported by price, year, mileage and creation date.

### Automatic Moderation

Every created listing is checked against forbidden words.

Possible statuses:

- active
- needs_edit
- inactive

If forbidden words are found, the seller can edit the listing.

After three unsuccessful editing attempts, the listing becomes inactive.

A manager notification is generated when a listing fails moderation three times.

For local development, emails are printed in the server console.

### Currency Conversion

Supported currencies:

- USD
- EUR
- UAH

Exchange rates are obtained from the public PrivatBank API.

The API stores current USD and EUR exchange rates.

Converted listing prices are returned in all three currencies.

The response also includes exchange rate information used for conversion. New listings store the original price, original currency, and the initial USD/UAH and EUR/UAH rate snapshots.

Exchange rate history is stored in the database.

The currency scheduler checks for daily updates automatically.

### Premium Analytics

Premium sellers can access:

- Total listing views
- Views during the last 24 hours
- Views during the last 7 days
- Views during the last 30 days
- Average price of similar cars in the seller's region
- Average price of similar cars in Ukraine

Average prices are calculated for active listings with the same brand and model.

Prices are converted to UAH before calculating averages.

Repeated requests may count as separate views.

## Running with Docker

### Requirements

- Docker Desktop
- Docker Compose

### Step 1. Clone the Repository

```bash
git clone https://github.com/kkosinovaa/auto-ria-django-kr.git
cd auto-ria-django-kr
```

Replace YOUR_REPOSITORY_URL with the actual GitHub repository URL.

### Step 2. Configure Environment

```bash
cp .env.docker.example .env.docker
```

The example configuration is intended for local development.

Do not commit .env.docker to Git.

### Step 3. Build Docker Image

```bash
docker build -t autoria-backend .
```

### Step 4. Start Containers

```bash
docker compose up -d
```

Docker Compose starts:

- MySQL database
- Django migrations
- Django REST API
- Currency update scheduler

### Step 5. Check Containers

```bash
docker compose ps -a
```

### Step 6. Create Demo Data

```bash
docker compose run --rm web python manage.py seed_demo
```

### Step 7. Open API

http://127.0.0.1:8890/api/listings/

The Docker API uses port 8890.

### Stop Containers

```bash
docker compose down
```

Database data is stored in a Docker volume.

Do not use docker compose down -v unless you intentionally want to delete the Docker database.

## Running Locally

### Step 1. Create Virtual Environment

```bash
python -m venv .venv
```

### Step 2. Activate Virtual Environment

Windows Git Bash:

```bash
source .venv/Scripts/activate
```

### Step 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4. Apply Migrations

```bash
python manage.py migrate
```

### Step 5. Create Demo Data

```bash
python manage.py seed_demo
```

### Step 6. Start Django

```bash
python manage.py runserver 8888
```

Local API:

http://127.0.0.1:8888/api/listings/

Local development uses SQLite by default.

## Demo Accounts

Demo accounts are created using:

```bash
python manage.py seed_demo
```

Or inside Docker:

```bash
docker compose run --rm web python manage.py seed_demo
```

| Role | Username | Password |
|------|----------|----------|
| Basic Seller | demo_basic | DemoPass123! |
| Premium Seller | demo_premium | DemoPass123! |
| Manager | demo_manager | DemoPass123! |
| Administrator | demo_admin | DemoPass123! |

These credentials are for local demonstration only.

Do not use them in production.

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/users/register/ | Register user |
| POST | /api/auth/login/ | Obtain JWT tokens |
| POST | /api/auth/refresh/ | Refresh access token |
| GET | /api/users/me/ | Current user profile |

### Cars

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/cars/brands/ | List brands |
| GET | /api/cars/models/ | List models |
| POST | /api/cars/requests/ | Request brand or model |
| GET | /api/cars/requests/pending/ | Review catalog requests |

### Listings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/listings/ | Public active listings |
| POST | /api/listings/ | Create listing |
| GET | /api/listings/{id}/ | Listing details |
| PATCH | /api/listings/{id}/ | Update listing |
| DELETE | /api/listings/{id}/ | Delete listing |
| GET | /api/listings/my/ | Current seller listings |

### Premium

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/users/premium/purchase/ | Mock Premium purchase |
| GET | /api/analytics/listings/{id}/ | Premium analytics |

### Currency

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/currency/rates/ | Current exchange rates |

### Manager

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/listings/manager/review/ | Review suspicious listings |
| DELETE | /api/listings/manager/{id}/delete/ | Delete a non-active listing |
| PATCH | /api/users/manager/users/{id}/status/ | Block or unblock user |

### Administrator

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/users/managers/ | Create manager |
| GET | /api/listings/forbidden-words/ | List forbidden words |
| POST | /api/listings/forbidden-words/ | Add forbidden word |

## Example Listing Request

```json
{
  "brand": 1,
  "model": 1,
  "title": "BMW X5 2020",
  "description": "Excellent condition",
  "year": 2020,
  "mileage": 65000,
  "price": "45000.00",
  "currency": "USD",
  "region": "Lviv",
  "contact_email": "seller@example.com"
}
```

## Filtering Examples

All BMW listings:

```text
/api/listings/?brand=1
```

Cars in Lviv:

```text
/api/listings/?region=Lviv
```

Cars manufactured from 2018:

```text
/api/listings/?min_year=2018
```

Cars priced between 10000 and 50000 USD:

```text
/api/listings/?currency=USD&min_price=10000&max_price=50000
```

Search:

```text
/api/listings/?search=BMW
```

Sort by descending price:

```text
/api/listings/?currency=USD&ordering=-price
```

## Update Currency Rates

Manual update:

```bash
python manage.py update_currency_rates
```

Docker:

```bash
docker compose exec web python manage.py update_currency_rates
```

Automatic daily updates are handled by the currency_scheduler service.

The scheduler checks periodically and updates rates if records for the current date are missing.

## Automated Tests

Run all available tests:

```bash
python manage.py test
```

Run listing and user tests:

```bash
python manage.py test listings users
```

The project includes 24 automated tests covering:

- User registration
- Permissions
- Premium activation
- Listing creation
- Basic and Premium limits
- Moderation
- Automatic deactivation
- Currency conversion
- Search
- Filtering
- View statistics
- Premium analytics
- Manager access

The listing and user test suites were successfully executed locally. Three additional tests cover manager deletion restrictions and initial exchange-rate snapshots.

## Postman Collection

File:

AutoRia.postman_collection.json

Import the collection into Postman using:

Import -> Files -> AutoRia.postman_collection.json

The collection uses the following variable:

```text
base_url = http://127.0.0.1:8890
```

For local Django without Docker, change it to:

```text
base_url = http://127.0.0.1:8888
```

Run a login request first.

The collection saves JWT access tokens into variables for authenticated requests.

Some operations change or delete demo data, so review the request before sending it.

## Limitations

- Premium payments are simulated.
- Emails use a console backend during local development.
- The API does not include a complete frontend website.
- The currency scheduler is intended for the Docker demonstration environment.
- The current view counter does not prevent repeated views from the same visitor.
- Additional car dealership functionality can be added through the permission-based architecture.
- The current implementation is intended as an educational project and requires additional production hardening before public deployment.

The Postman Administrator folder includes a Create Manager request.

## Author

Kateryna Kosinova

Computer Science Student

AutoRia Clone — Django REST Framework Control Project
