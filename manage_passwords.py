#!/usr/bin/env python
"""
TechMate Password Management Tool
Quick script to view and reset passwords
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SMS.settings')
django.setup()

from accounts.models import User
import sys

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def show_all_credentials():
    """Display all user credentials"""
    print_header("TECHMATE LMS - ALL ACCOUNT CREDENTIALS")
    
    # Admin
    print("🔑 ADMIN ACCOUNT")
    print("Username: admin")
    print("Password: H@rdw0rk")
    print("URL: http://127.0.0.1:8000/admin/\n")
    
    # Lecturers
    print("👨‍🏫 LECTURER ACCOUNTS (10)")
    print("Pattern: lecturerX / Teach@100X\n")
    for i in range(1, 11):
        print(f"  lecturer{i:<12} → Teach@100{i}")
    
    # Students
    print("\n🎓 STUDENT ACCOUNTS (100)")
    print("Pattern: studentXXX / Student@20XX\n")
    print("Quick Test Accounts:")
    for i in range(1, 6):
        username = f"student{i:03d}"
        password = f"Student@{2000+i}"
        print(f"  {username:<12} → {password}")
    print(f"\n  ... and 95 more following same pattern (student006-student100)")
    
    print("\n" + "="*70)
    print("Total: 111 accounts (1 admin + 10 lecturers + 100 students)")
    print("="*70)

def reset_to_original():
    """Reset all passwords to original values"""
    print_header("RESETTING ALL PASSWORDS TO ORIGINAL")
    
    count = 0
    
    # Reset admin
    try:
        admin = User.objects.get(username='admin')
        admin.set_password('H@rdw0rk')
        admin.save()
        print("✓ admin → H@rdw0rk")
        count += 1
    except User.DoesNotExist:
        print("✗ admin not found")
    
    # Reset lecturers
    print("\nResetting lecturers...")
    for i in range(1, 11):
        try:
            user = User.objects.get(username=f'lecturer{i}')
            password = f'Teach@100{i}'
            user.set_password(password)
            user.save()
            print(f"✓ lecturer{i} → {password}")
            count += 1
        except User.DoesNotExist:
            print(f"✗ lecturer{i} not found")
    
    # Reset students
    print("\nResetting students...")
    for i in range(1, 101):
        try:
            username = f'student{i:03d}'
            password = f'Student@{2000+i}'
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            if i <= 5 or i % 20 == 0:  # Show first 5 and every 20th
                print(f"✓ {username} → {password}")
            count += 1
        except User.DoesNotExist:
            print(f"✗ {username} not found")
    
    print(f"\n{'='*70}")
    print(f"✅ Successfully reset {count} passwords to original values")
    print(f"{'='*70}")

def change_single_password(username, new_password):
    """Change password for a single user"""
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        print(f"✅ Password changed for '{username}'")
        print(f"   New password: {new_password}")
        return True
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found")
        return False

def reset_all_students(password):
    """Reset all student passwords to the same value"""
    print(f"Resetting all student passwords to: {password}")
    count = 0
    for i in range(1, 101):
        try:
            username = f'student{i:03d}'
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            count += 1
        except User.DoesNotExist:
            pass
    print(f"✅ Reset {count} student passwords")

def reset_all_lecturers(password):
    """Reset all lecturer passwords to the same value"""
    print(f"Resetting all lecturer passwords to: {password}")
    count = 0
    for i in range(1, 11):
        try:
            user = User.objects.get(username=f'lecturer{i}')
            user.set_password(password)
            user.save()
            count += 1
        except User.DoesNotExist:
            pass
    print(f"✅ Reset {count} lecturer passwords")

def show_menu():
    """Display interactive menu"""
    while True:
        print_header("TECHMATE PASSWORD MANAGEMENT")
        print("1. Show all credentials")
        print("2. Reset all passwords to original")
        print("3. Change single user password")
        print("4. Reset all student passwords")
        print("5. Reset all lecturer passwords")
        print("6. Exit")
        print()
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == '1':
            show_all_credentials()
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            confirm = input("Reset ALL passwords to original? (yes/no): ").strip().lower()
            if confirm == 'yes':
                reset_to_original()
            else:
                print("Cancelled")
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            username = input("Enter username: ").strip()
            password = input("Enter new password: ").strip()
            if username and password:
                change_single_password(username, password)
            else:
                print("Invalid input")
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            password = input("Enter new password for all students: ").strip()
            if password:
                confirm = input(f"Reset all 100 students to '{password}'? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    reset_all_students(password)
                else:
                    print("Cancelled")
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            password = input("Enter new password for all lecturers: ").strip()
            if password:
                confirm = input(f"Reset all 10 lecturers to '{password}'? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    reset_all_lecturers(password)
                else:
                    print("Cancelled")
            input("\nPress Enter to continue...")
        
        elif choice == '6':
            print("\n👋 Goodbye!")
            sys.exit(0)
        
        else:
            print("Invalid choice")
            input("\nPress Enter to continue...")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1]
        
        if command == 'show':
            show_all_credentials()
        
        elif command == 'reset':
            reset_to_original()
        
        elif command == 'change' and len(sys.argv) >= 4:
            username = sys.argv[2]
            password = sys.argv[3]
            change_single_password(username, password)
        
        else:
            print("Usage:")
            print("  python manage_passwords.py show              - Show all credentials")
            print("  python manage_passwords.py reset             - Reset to original")
            print("  python manage_passwords.py change USER PASS  - Change single password")
            print("  python manage_passwords.py                   - Interactive menu")
    else:
        # Interactive menu mode
        show_menu()
