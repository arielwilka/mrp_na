#Structure Project
project_master/
├── backend/                # Django Root
│   ├── core/               # Settings, WSGI
│   ├── vin_record/         # App Modul VIN
│   │   ├── models.py
│   │   ├── api/            # Serializers & Viewsets
│   │   └── signals.py      # Business logic triggers
│   ├── static/             # Hasil build Vite (collected)
│   ├── templates/          # Template HTML entry point
│   └── manage.py
├── frontend/               # Vite Root
│   ├── src/
│   │   ├── modules/
│   │   │   └── vin_record/ # Vue Components khusus VIN
│   ├── vite.config.js
│   └── package.json
└── requirements.txt

#START DJANGO PROJECT
# Membuat project django bernama 'core' di dalam folder saat ini (.)
django-admin startproject core .

# Membuat aplikasi modul pertama 'vin_record'
python manage.py startapp vin_record
# Create Posgres DB
CREATE DATABASE production_master_db;
