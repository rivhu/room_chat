#!/bin/bash
echo "=============================="
echo "  ChatRooms - Quick Setup"
echo "=============================="

echo ""
echo "1. Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "2. Installing dependencies..."
pip install -r requirements.txt

echo "3. Running migrations..."
python manage.py migrate

echo "4. Creating default rooms..."
python manage.py shell -c "
from django.contrib.auth.models import User
from chat.models import Room
if not Room.objects.filter(name='general').exists():
    Room.objects.create(name='general', description='General chat for everyone')
if not Room.objects.filter(name='random').exists():
    Room.objects.create(name='random', description='Random topics and fun stuff')
print('Default rooms created.')
"

echo ""
echo "=============================="
echo "  Setup complete!"
echo "  Run: daphne -b 0.0.0.0 -p 8000 chatproject.asgi:application"
echo "  Then open: http://127.0.0.1:8000"
echo "=============================="
