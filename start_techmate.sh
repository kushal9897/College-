#!/bin/bash

# TechMate - Smart Learning Platform Startup Script
# Final Year College Project

echo "🎓 Starting TechMate - Smart Learning Platform..."
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
if ! python -c "import django" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --noinput

# Collect static files (optional, uncomment if needed)
# echo "📁 Collecting static files..."
# python manage.py collectstatic --noinput

echo ""
echo "✅ TechMate is ready!"
echo "================================================"
echo "🌐 Server will start at: http://127.0.0.1:8000/"
echo "📊 Admin Panel: http://127.0.0.1:8000/admin/"
echo ""
echo "Press CTRL+C to stop the server"
echo "================================================"
echo ""

# Start the development server
python manage.py runserver
