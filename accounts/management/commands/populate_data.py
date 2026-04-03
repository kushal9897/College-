"""
Django Management Command to Populate TechMate Database
Creates sample users, courses, and enrollments for demonstration
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from course.models import Program, Course, CourseAllocation
from result.models import TakenCourse
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample data for TechMate LMS'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting TechMate data population...'))
        
        # Sample data
        first_names = [
            'Aarav', 'Vivaan', 'Aditya', 'Arjun', 'Sai', 'Krishna', 'Ishaan', 'Reyansh', 'Ayaan', 'Shaurya',
            'Aadhya', 'Ananya', 'Diya', 'Isha', 'Kavya', 'Saanvi', 'Sara', 'Priya', 'Nisha', 'Riya',
            'Rahul', 'Rohan', 'Karan', 'Aryan', 'Varun', 'Yash', 'Kunal', 'Nikhil', 'Aakash', 'Ankur',
            'Sneha', 'Pooja', 'Neha', 'Simran', 'Shruti', 'Megha', 'Divya', 'Anjali', 'Kritika', 'Tanya',
            'Amit', 'Sumit', 'Rohit', 'Mohit', 'Ajay', 'Vijay', 'Suresh', 'Mahesh', 'Ramesh', 'Dinesh',
            'Priyanka', 'Deepika', 'Swati', 'Pallavi', 'Sonali', 'Madhuri', 'Vidya', 'Rekha', 'Sonal', 'Komal',
            'Dev', 'Om', 'Harsh', 'Pranav', 'Ansh', 'Krish', 'Vihaan', 'Shivansh', 'Atharv', 'Aayan',
            'Aarohi', 'Myra', 'Aanya', 'Pari', 'Navya', 'Kiara', 'Shanaya', 'Reet', 'Anvi', 'Siya',
            'Kabir', 'Dhruv', 'Arnav', 'Advait', 'Rudra', 'Vedant', 'Ayush', 'Laksh', 'Aayansh', 'Darsh',
            'Ahana', 'Avni', 'Ira', 'Tvisha', 'Zara', 'Sia', 'Mira', 'Tara', 'Riana', 'Niyati'
        ]
        
        last_names = [
            'Sharma', 'Patel', 'Kumar', 'Singh', 'Gupta', 'Verma', 'Reddy', 'Agarwal', 'Joshi', 'Mehta',
            'Desai', 'Shah', 'Kapoor', 'Chopra', 'Malhotra', 'Nair', 'Iyer', 'Mishra', 'Pandey', 'Rao',
            'Jain', 'Bansal', 'Saxena', 'Arora', 'Bhatia', 'Sinha', 'Das', 'Ghosh', 'Mukherjee', 'Choudhary',
            'Thakur', 'Rajput', 'Yadav', 'Chauhan', 'Bhatt', 'Trivedi', 'Kulkarni', 'Deshpande', 'Patil', 'Naik'
        ]
        
        lecturer_titles = ['Dr.', 'Prof.', 'Mr.', 'Ms.', 'Mrs.']
        
        departments = ['Computer Science', 'Information Technology', 'Electronics', 'Mechanical', 'Civil']
        
        course_data = [
            ('Data Structures', 'CS301', 4),
            ('Algorithms', 'CS302', 4),
            ('Database Systems', 'CS303', 3),
            ('Operating Systems', 'CS304', 4),
            ('Computer Networks', 'CS305', 3),
            ('Software Engineering', 'CS306', 3),
            ('Web Development', 'CS307', 4),
            ('Machine Learning', 'CS308', 4),
            ('Artificial Intelligence', 'CS309', 4),
            ('Cloud Computing', 'CS310', 3),
            ('Cybersecurity', 'CS311', 3),
            ('Mobile App Development', 'CS312', 3),
            ('DevOps', 'CS313', 3),
            ('Blockchain', 'CS314', 3),
            ('IoT', 'CS315', 3),
        ]
        
        # Create Programs
        self.stdout.write('Creating programs...')
        programs = []
        for dept in departments:
            prog, created = Program.objects.get_or_create(
                title=f'B.Tech {dept}',
                defaults={'summary': f'Bachelor of Technology in {dept}'}
            )
            programs.append(prog)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created program: {prog.title}'))
        
        # Create 10 Lecturers
        self.stdout.write('\nCreating 10 lecturers...')
        lecturers = []
        lecturer_creds = []
        
        for i in range(10):
            title = random.choice(lecturer_titles)
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            username = f'lecturer{i+1}'
            email = f'{username}@techmate.edu'
            password = f'Teach@{1000+i}'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'{title} {fname}',
                    'last_name': lname,
                    'is_lecturer': True,
                    'phone': f'+91-98765{43210+i}',
                    'address': f'{i+1}, Faculty Block, TechMate Campus',
                }
            )
            
            if created:
                user.set_password(password)
                user.save()
                lecturers.append(user)
                lecturer_creds.append({
                    'username': username,
                    'password': password,
                    'email': email,
                    'name': f'{title} {fname} {lname}'
                })
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {user.get_full_name} ({username})'))
        
        # Create Courses and allocate to lecturers
        self.stdout.write('\nCreating courses...')
        courses = []
        for i, (title, code, credit) in enumerate(course_data):
            program = programs[i % len(programs)]
            level = random.choice(['100', '200', '300', '400'])
            
            course, created = Course.objects.get_or_create(
                title=title,
                code=code,
                defaults={
                    'credit': credit,
                    'program': program,
                    'level': level,
                    'summary': f'Comprehensive course in {title}',
                }
            )
            courses.append(course)
            
            if created and lecturers:
                # Allocate course to a random lecturer
                lecturer = random.choice(lecturers)
                allocation, _ = CourseAllocation.objects.get_or_create(
                    lecturer=lecturer
                )
                allocation.courses.add(course)
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {title} ({code}) - Assigned to {lecturer.get_full_name}'))
        
        # Create 100 Students
        self.stdout.write('\nCreating 100 students...')
        from accounts.models import Student
        students = []
        student_creds = []
        
        for i in range(100):
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            username = f'student{i+1:03d}'
            email = f'{username}@techmate.edu'
            password = f'Student@{2024+i}'
            
            # Generate student ID
            year = random.choice(['21', '22', '23', '24'])
            dept_code = random.choice(['CS', 'IT', 'EC', 'ME', 'CE'])
            student_id = f'TM{year}{dept_code}{i+1:03d}'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': fname,
                    'last_name': lname,
                    'is_student': True,
                    'phone': f'+91-{7000000000 + i}',
                    'address': f'Hostel Block {chr(65 + (i % 10))}, Room {100 + i}',
                }
            )
            
            if created:
                user.set_password(password)
                user.save()
                
                # Create Student profile
                program = random.choice(programs)
                level_choice = random.choice(['100', '200', '300', '400'])
                student_profile, _ = Student.objects.get_or_create(
                    student=user,
                    defaults={
                        'level': level_choice,
                        'department': program,
                    }
                )
                
                students.append(user)
                student_creds.append({
                    'username': username,
                    'password': password,
                    'email': email,
                    'name': f'{fname} {lname}',
                    'student_id': student_id,
                    'program': program.title
                })
                
                # Enroll in 4-6 random courses
                num_courses = random.randint(4, 6)
                enrolled_courses = random.sample(courses, num_courses)
                for course in enrolled_courses:
                    TakenCourse.objects.get_or_create(
                        student=student_profile,
                        course=course,
                        defaults={
                            'assignment': random.randint(10, 20),
                            'mid_exam': random.randint(15, 30),
                            'quiz': random.randint(5, 10),
                            'attendance': random.randint(5, 10),
                            'final_exam': random.randint(30, 40),
                        }
                    )
                
                if (i + 1) % 20 == 0:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created {i + 1} students...'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully created {len(students)} students'))
        
        # Save credentials to file
        self.save_credentials(lecturer_creds, student_creds)
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('✅ TechMate Database Population Complete!'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f'  Programs: {len(programs)}')
        self.stdout.write(f'  Lecturers: {len(lecturers)}')
        self.stdout.write(f'  Courses: {len(courses)}')
        self.stdout.write(f'  Students: {len(students)}')
        self.stdout.write(self.style.SUCCESS('\n📄 Credentials saved to: CREDENTIALS_LIST.md'))
        self.stdout.write(self.style.SUCCESS('='*70))
    
    def save_credentials(self, lecturer_creds, student_creds):
        """Save all credentials to a markdown file"""
        with open('CREDENTIALS_LIST.md', 'w') as f:
            f.write('# TechMate LMS - User Credentials\n')
            f.write('## Complete List of Usernames & Passwords\n\n')
            f.write(f'**Generated:** {timezone.now().strftime("%B %d, %Y at %I:%M %p")}\n\n')
            f.write('---\n\n')
            
            # Admin
            f.write('## 🔑 Administrator Account\n\n')
            f.write('| Username | Password | Email | Role |\n')
            f.write('|----------|----------|-------|------|\n')
            f.write('| admin | H@rdw0rk | admin@lms.com | Super Admin |\n\n')
            f.write('**Admin Panel:** http://127.0.0.1:8000/admin/\n\n')
            f.write('---\n\n')
            
            # Lecturers
            f.write('## 👨‍🏫 Lecturers (10)\n\n')
            f.write('| # | Username | Password | Email | Full Name |\n')
            f.write('|---|----------|----------|-------|------------|\n')
            for i, cred in enumerate(lecturer_creds, 1):
                f.write(f'| {i} | {cred["username"]} | {cred["password"]} | {cred["email"]} | {cred["name"]} |\n')
            f.write('\n---\n\n')
            
            # Students
            f.write('## 🎓 Students (100)\n\n')
            f.write('| # | Username | Password | Student ID | Full Name | Program | Email |\n')
            f.write('|---|----------|----------|------------|-----------|---------|-------|\n')
            for i, cred in enumerate(student_creds, 1):
                f.write(f'| {i} | {cred["username"]} | {cred["password"]} | {cred["student_id"]} | {cred["name"]} | {cred["program"]} | {cred["email"]} |\n')
            
            f.write('\n---\n\n')
            f.write('## 📊 Quick Stats\n\n')
            f.write(f'- **Total Users:** {1 + len(lecturer_creds) + len(student_creds)}\n')
            f.write(f'- **Administrators:** 1\n')
            f.write(f'- **Lecturers:** {len(lecturer_creds)}\n')
            f.write(f'- **Students:** {len(student_creds)}\n')
            f.write('\n---\n\n')
            f.write('## 🔐 Password Pattern\n\n')
            f.write('- **Admin:** `H@rdw0rk`\n')
            f.write('- **Lecturers:** `Teach@1000` to `Teach@1009`\n')
            f.write('- **Students:** `Student@2024` to `Student@2123`\n')
            f.write('\n---\n\n')
            f.write('## 📝 Notes\n\n')
            f.write('- All users are active and ready to login\n')
            f.write('- Students are enrolled in 4-6 random courses each\n')
            f.write('- Courses are allocated to lecturers\n')
            f.write('- Sample grades have been assigned\n')
            f.write('- Phone numbers and addresses are auto-generated\n')
            f.write('\n**⚠️ Keep this file secure - Contains sensitive credentials**\n')
