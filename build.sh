#!/usr/bin/env bash
# Exit on error
set -o errexit

# Cài đặt dependencies
pip install -r requirements.txt

# Thu thập static files
python manage.py collectstatic --no-input

# Chạy migrations
python manage.py migrate