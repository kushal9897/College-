# 🔐 TechMate LMS - Admin Password Management Guide

**Server:** http://127.0.0.1:8000/  
**Admin Panel:** http://127.0.0.1:8000/admin/

---

## 📋 ALL ACCOUNT CREDENTIALS

### 🔑 **Admin Account**
```
Username: admin
Password: H@rdw0rk
URL: http://127.0.0.1:8000/admin/
```

### 👨‍🏫 **Lecturer Accounts** (10 Total)
Pattern: `lecturerX` / `Teach@100X`

```
Username: lecturer1    Password: Teach@1001
Username: lecturer2    Password: Teach@1002
Username: lecturer3    Password: Teach@1003
Username: lecturer4    Password: Teach@1004
Username: lecturer5    Password: Teach@1005
Username: lecturer6    Password: Teach@1006
Username: lecturer7    Password: Teach@1007
Username: lecturer8    Password: Teach@1008
Username: lecturer9    Password: Teach@1009
Username: lecturer10   Password: Teach@1010
```

### 🎓 **Student Accounts** (100 Total)
Pattern: `studentXXX` / `Student@20XX`

**Quick Test Accounts:**
```
Username: student001   Password: Student@2001
Username: student002   Password: Student@2002
Username: student003   Password: Student@2003
Username: student004   Password: Student@2004
Username: student005   Password: Student@2005
```

**All Students Follow Pattern:**
- student001 → student100
- Password: Student@20XX (where XX matches student number)

---

## 🛠️ HOW TO CHANGE PASSWORDS IN ADMIN

### **Method 1: Change Individual User Password**

#### **Step-by-Step:**

1. **Login to Admin**
   - Go to: http://127.0.0.1:8000/admin/
   - Username: `admin`
   - Password: `H@rdw0rk`

2. **Navigate to Users**
   - Click **"Users"** in the left sidebar
   - Or go directly to: http://127.0.0.1:8000/admin/accounts/user/

3. **Select User**
   - Click on any username (e.g., `student001`)
   - You'll see the user edit page

4. **Change Password**
   - Scroll to the **Password** field
   - Click the link: **"change password form"**
   - Or look for the link next to password field

5. **Set New Password**
   - Enter new password in both fields
   - Click **"Change Password"**
   - Password is now updated!

---

### **Method 2: Bulk Password Reset**

#### **Quick Password Reset for Testing:**

1. **Open Django Shell**
   ```bash
   cd /Users/kushalagrawal/prj/LMS-django-
   source venv/bin/activate
   python manage.py shell
   ```

2. **Reset All Student Passwords to "Test@123"**
   ```python
   from accounts.models import User
   
   # Reset all students
   students = User.objects.filter(is_student=True)
   for student in students:
       student.set_password('Test@123')
       student.save()
   print(f"Reset {students.count()} student passwords to: Test@123")
   ```

3. **Reset All Lecturer Passwords**
   ```python
   lecturers = User.objects.filter(is_lecturer=True)
   for lecturer in lecturers:
       lecturer.set_password('Lecturer@123')
       lecturer.save()
   print(f"Reset {lecturers.count()} lecturer passwords to: Lecturer@123")
   ```

4. **Reset Specific User**
   ```python
   user = User.objects.get(username='student001')
   user.set_password('NewPassword@123')
   user.save()
   print(f"Password reset for: {user.username}")
   ```

---

### **Method 3: Create Password Reset Management Command**

I can create a custom Django command for you to easily reset passwords.

**Usage would be:**
```bash
python manage.py reset_passwords --type students --password "NewPass@123"
python manage.py reset_passwords --type lecturers --password "Teach@456"
python manage.py reset_passwords --username student001 --password "Custom@789"
```

Would you like me to create this command?

---

## 📊 VIEW ALL PASSWORDS IN ADMIN

### **Option 1: Export User List with Credentials**

Since passwords are hashed, you can't view them directly. Instead:

1. **Keep CREDENTIALS_LIST.md file** (already created)
   - Location: `/Users/kushalagrawal/prj/LMS-django-/CREDENTIALS_LIST.md`
   - Contains all original passwords

2. **View in Terminal:**
   ```bash
   cat CREDENTIALS_LIST.md
   ```

### **Option 2: Display in Admin Panel**

Create a custom admin action to show credentials:

1. Go to admin panel
2. Select users
3. Actions → "View Credentials"
4. See username and reset info

---

## 🔄 RESET TO ORIGINAL PASSWORDS

To reset all passwords back to original:

```bash
cd /Users/kushalagrawal/prj/LMS-django-
source venv/bin/activate
python manage.py shell
```

Then run:
```python
from accounts.models import User

# Reset admin
admin = User.objects.get(username='admin')
admin.set_password('H@rdw0rk')
admin.save()
print("Admin password reset to: H@rdw0rk")

# Reset lecturers (pattern: Teach@100X)
for i in range(1, 11):
    try:
        user = User.objects.get(username=f'lecturer{i}')
        user.set_password(f'Teach@100{i}')
        user.save()
        print(f"lecturer{i} → Teach@100{i}")
    except:
        pass

# Reset students (pattern: Student@20XX)
for i in range(1, 101):
    try:
        username = f'student{i:03d}'
        user = User.objects.get(username=username)
        user.set_password(f'Student@{2000+i}')
        user.save()
        print(f"{username} → Student@{2000+i}")
    except:
        pass

print("\n✅ All passwords reset to original!")
```

---

## 📱 QUICK ADMIN ACTIONS

### **In Admin Panel (http://127.0.0.1:8000/admin/):**

1. **View All Users:**
   - Admin → Users
   - See 111 total users (1 admin + 10 lecturers + 100 students)

2. **Filter Users:**
   - Filter by: Student, Lecturer, Active, Staff
   - Search by username, email, name

3. **Change Individual Password:**
   - Click user → Change password form
   - Enter new password twice
   - Save

4. **View User Details:**
   - Click username
   - See full profile, groups, permissions
   - Edit any field

---

## 🎯 RECOMMENDED FOR PRESENTATION

### **Use These Test Accounts:**

**Admin Demo:**
```
admin / H@rdw0rk
```

**Student Demo:**
```
student001 / Student@2001  (Has fees to pay)
student002 / Student@2002  (Different program)
```

**Lecturer Demo:**
```
lecturer1 / Teach@1001
```

---

## 💡 PRO TIPS

1. **Keep Original Passwords Simple for Demo**
   - Current pattern is easy to remember
   - Student: Student@20XX
   - Lecturer: Teach@100X

2. **Reset Passwords After Presentation**
   - Use the shell command above
   - Takes 30 seconds

3. **Create Test Account with Known Password**
   - For quick demos: test@123 / test@123
   - Add via admin panel

4. **Password Requirements:**
   - Must be at least 8 characters
   - Should contain letters and numbers
   - Current passwords all meet requirements

---

## 🔐 SECURITY NOTES

- All passwords are hashed in database (secure)
- Can't view original passwords in admin
- Only way to "view" is to reset them
- Keep CREDENTIALS_LIST.md file safe
- Don't commit passwords to Git

---

## ✅ CURRENT STATUS

**Server Running:** ✅ http://127.0.0.1:8000/  
**Razorpay Enabled:** ✅ Real keys configured  
**Payment System:** ✅ Working with live Razorpay  
**All Accounts:** ✅ 111 users ready  
**Passwords:** ✅ As documented above  

---

## 🚀 READY FOR TESTING

1. **Login as any account** using credentials above
2. **Test payment** with student001
3. **Admin panel** with admin account
4. **Change any password** using methods above

**Need to reset passwords? Just run the shell commands!**
