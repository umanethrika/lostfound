# lostfound
🕵️ Lost & Found Management System

A web application built with Django to streamline reporting and recovering lost items. Users can post items they’ve lost or found, and the system automatically matches similar entries using fuzzy search.

🚀 Features

🔍 Smart Matching – Uses fuzzy string matching (RapidFuzz) to automatically notify users when a found item resembles a lost item.

📷 Image Support – Upload images of items (via Pillow) for better identification.

🔔 Real-Time Notifications – Instant updates without page refresh using AJAX & Bootstrap modals for better UX.

👤 User-Friendly Interface – Clean UI built with Bootstrap, making it easy for both finders and seekers to interact.

🛠️ Tech Stack

Backend: Django 5.2

Database: PostgreSQL (via psycopg2-binary)

Frontend: Bootstrap, AJAX, jQuery

Other Libraries: RapidFuzz (matching), Pillow (images), Widget Tweaks

📦 Installation

Clone the repository:

git clone https://github.com/your-username/lostfound.git
cd lostfound


Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt


Apply migrations:

python manage.py migrate


Run the development server:

python manage.py runserver


Open in browser:

http://127.0.0.1:8000/
