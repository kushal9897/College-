# 🚀 TechMate Quick Start Guide

## How to Run TechMate in One Command

### ⚡ Super Quick Start

```bash
cd /Users/kushalagrawal/prj/LMS-django-
./start_techmate.sh
```

That's it! The script handles everything automatically.

---

## 📝 What the Script Does

The `start_techmate.sh` script automatically:

1. ✅ Checks if virtual environment exists
2. ✅ Activates the virtual environment
3. ✅ Verifies all dependencies are installed
4. ✅ Runs database migrations
5. ✅ Starts the Django development server

---

## 🎯 Step-by-Step Instructions

### First Time Setup

1. **Navigate to project directory:**
   ```bash
   cd /Users/kushalagrawal/prj/LMS-django-
   ```

2. **Make the script executable (one-time only):**
   ```bash
   chmod +x start_techmate.sh
   ```

3. **Run the script:**
   ```bash
   ./start_techmate.sh
   ```

### Every Time After That

Just run:
```bash
./start_techmate.sh
```

---

## 🌐 Accessing TechMate

Once the server starts, you'll see:

```
✅ TechMate is ready!
================================================
🌐 Server will start at: http://127.0.0.1:8000/
📊 Admin Panel: http://127.0.0.1:8000/admin/
```

**Main URLs:**
- **Homepage:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **Login:** http://127.0.0.1:8000/accounts/login/

---

## 🛑 Stopping the Server

Press `CTRL + C` in the terminal where the server is running.

---

## 🔧 Troubleshooting

### Problem: "Port already in use"

**Solution:**
```bash
# Kill any process using port 8000
lsof -ti:8000 | xargs kill -9

# Then run the script again
./start_techmate.sh
```

### Problem: "Permission denied"

**Solution:**
```bash
chmod +x start_techmate.sh
```

### Problem: "Virtual environment not found"

**Solution:**
The script will create it automatically. Just run:
```bash
./start_techmate.sh
```

### Problem: Missing dependencies

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 👤 Admin Account

**Username:** `admin`  
**Email:** `admin@lms.com`

To reset password:
```bash
source venv/bin/activate
python manage.py changepassword admin
```

To create a new superuser:
```bash
source venv/bin/activate
python manage.py createsuperuser
```

---

## 📦 Manual Commands (Alternative)

If you prefer running commands manually:

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

---

## 🎨 Project Features

✨ **TechMate** includes:
- Modern purple-indigo gradient design
- Responsive layout
- User role management (Admin, Lecturer, Student)
- Course management
- Quiz system
- Grade tracking
- News & Events
- Analytics dashboard

---

## 📱 For Your College Project Demo

### Presentation Tips:

1. **Start the server before demo:**
   ```bash
   ./start_techmate.sh
   ```

2. **Show the login page** - Modern design with gradient background

3. **Login as admin** - Demonstrate full access

4. **Show key features:**
   - Dashboard with analytics
   - Student management
   - Course allocation
   - Quiz system
   - Grade results

5. **Highlight the modern design:**
   - Purple-indigo theme
   - Smooth animations
   - Professional typography
   - Responsive design

---

## 📊 Database Commands

```bash
# Run migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Open Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser
```

---

## 🔄 Development Workflow

1. **Start developing:**
   ```bash
   ./start_techmate.sh
   ```

2. **Make changes to code**
   - Django auto-reloads on file changes
   - No need to restart server for Python changes
   - CSS/JS changes may need browser refresh

3. **Stop server when done:**
   - Press `CTRL + C`

---

## 📁 Important Files

```
LMS-django-/
├── start_techmate.sh          ← Quick start script
├── README_TECHMATE.md         ← Full project documentation
├── QUICK_START_GUIDE.md       ← This file
├── manage.py                  ← Django management
├── requirements.txt           ← Dependencies
├── .env                       ← Configuration (keep private)
└── static/css/
    └── techmate-theme.css     ← Custom theme
```

---

## 🎓 Final Year Project Checklist

- [✓] Modern, professional design
- [✓] Complete LMS functionality
- [✓] User authentication system
- [✓] Database integration
- [✓] Responsive design
- [✓] Documentation (README)
- [✓] Quick start script
- [ ] Screenshots for report
- [ ] Testing documentation
- [ ] Deployment guide (if required)

---

## 💡 Pro Tips

1. **Take screenshots** while server is running for your project report
2. **Document any customizations** you make
3. **Test all user roles** (Admin, Lecturer, Student)
4. **Prepare demo data** before presentation
5. **Keep the .env file secure** - don't share passwords

---

## 🆘 Getting Help

If you encounter issues:

1. Check the terminal output for error messages
2. Review `README_TECHMATE.md` for detailed documentation
3. Verify PostgreSQL is running: `pg_isready`
4. Check Python version: `python --version` (should be 3.8+)

---

## 🎉 You're All Set!

TechMate is ready to impress for your final year project!

**Quick reminder:**
```bash
cd /Users/kushalagrawal/prj/LMS-django-
./start_techmate.sh
```

Good luck with your project! 🚀
