# METRA Online Tech Store

METRA is a Django-based e-commerce platform for selling tech products online. The platform provides product browsing, cart functionality, user authentication, and checkout processes.

## Features

- User authentication and profile management
- Product catalog with categories
- Advanced product search
- Shopping cart functionality
- Product reviews and ratings
- Responsive design
- Order management system
- Admin dashboard

## Technologies Used

- Django 4.x
- Python 3.13
- JavaScript
- Bootstrap 5
- SQLite (development)
- HTML5/CSS3

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/metra.git
cd metra
```

2. Create virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Apply migrations
```bash
python manage.py migrate
```

4. Create a superuser
```bash
python manage.py createsuperuser
```

5. Run the development server
```bash
python manage.py runserver
```

6. Access the application at http://127.0.0.1:8000/

## Configuration

- Configure settings in `metra_project/settings.py`
- Media files are stored in the `media/` directory
- Static files are stored in the `static/` directory

## License

This project is licensed under the MIT License - see the LICENSE file for details.