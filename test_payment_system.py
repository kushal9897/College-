#!/usr/bin/env python
"""
TechMate Payment System QA Test
Comprehensive testing as Senior QA Engineer
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SMS.settings')
django.setup()

from fees.models import StudentFee, Payment, FeeStructure
from accounts.models import Student
from django.contrib.auth import get_user_model
from django.conf import settings
import sys

User = get_user_model()

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")

def test_result(name, passed, message=""):
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} | {name}")
    if message:
        print(f"       {message}")
    return passed

print_header("TECHMATE PAYMENT SYSTEM QA TEST")
print("Testing as Senior QA Engineer")

all_passed = True

# Test 1: Check imports
print_header("1. DEPENDENCY CHECK")
try:
    import razorpay
    all_passed &= test_result("Razorpay SDK installed", True)
except ImportError as e:
    all_passed &= test_result("Razorpay SDK installed", False, str(e))

try:
    from reportlab.lib.pagesizes import A4
    all_passed &= test_result("ReportLab installed", True)
except ImportError as e:
    all_passed &= test_result("ReportLab installed", False, str(e))

# Test 2: Settings configuration
print_header("2. SETTINGS CONFIGURATION")
all_passed &= test_result("RAZORPAY_KEY_ID configured", 
    bool(getattr(settings, 'RAZORPAY_KEY_ID', None)),
    settings.RAZORPAY_KEY_ID if hasattr(settings, 'RAZORPAY_KEY_ID') else "Not set")

all_passed &= test_result("RAZORPAY_KEY_SECRET configured", 
    bool(getattr(settings, 'RAZORPAY_KEY_SECRET', None)))

all_passed &= test_result("RAZORPAY_ENABLED", 
    getattr(settings, 'RAZORPAY_ENABLED', False))

# Test 3: Database
print_header("3. DATABASE CHECK")
student_count = Student.objects.count()
all_passed &= test_result("Students exist", student_count > 0, f"{student_count} students")

fee_count = StudentFee.objects.count()
all_passed &= test_result("Fees exist", fee_count > 0, f"{fee_count} fees")

pending_fees = StudentFee.objects.exclude(status='Paid').count()
all_passed &= test_result("Pending fees exist", pending_fees > 0, f"{pending_fees} pending")

payment_count = Payment.objects.count()
all_passed &= test_result("Payments exist", payment_count >= 0, f"{payment_count} payments")

# Test 4: URL Configuration
print_header("4. URL ROUTING CHECK")
from django.urls import resolve, reverse
from django.urls.exceptions import NoReverseMatch

urls_to_test = [
    'student_fees',
    'initiate_payment',
    'payment_method_selection',
    'online_payment_gateway',
    'razorpay_callback',
    'payment_success',
]

for url_name in urls_to_test:
    try:
        if url_name in ['initiate_payment', 'payment_method_selection', 'online_payment_gateway']:
            url = reverse(url_name, kwargs={'fee_id': 1})
        else:
            url = reverse(url_name)
        all_passed &= test_result(f"URL: {url_name}", True, url)
    except NoReverseMatch as e:
        all_passed &= test_result(f"URL: {url_name}", False, str(e))

# Test 5: Test student account
print_header("5. TEST ACCOUNT CHECK")
try:
    test_user = User.objects.get(username='student001')
    all_passed &= test_result("Test student exists", True, "student001")
    
    student = Student.objects.get(student=test_user)
    all_passed &= test_result("Student profile exists", True)
    
    student_fees = StudentFee.objects.filter(student=student)
    all_passed &= test_result("Student has fees", student_fees.exists(), 
        f"{student_fees.count()} fees assigned")
    
    pending = student_fees.exclude(status='Paid')
    all_passed &= test_result("Student has pending fees", pending.exists(),
        f"{pending.count()} pending fees")
    
except User.DoesNotExist:
    all_passed &= test_result("Test student exists", False, "student001 not found")
except Student.DoesNotExist:
    all_passed &= test_result("Student profile exists", False, "Profile not found")

# Test 6: Razorpay Client
print_header("6. RAZORPAY CONNECTION CHECK")
try:
    import razorpay
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    all_passed &= test_result("Razorpay client initialized", True)
    
    # Try to create a test order
    try:
        test_order = client.order.create({
            'amount': 100,  # ₹1 in paise
            'currency': 'INR',
            'receipt': 'TEST_RECEIPT',
        })
        all_passed &= test_result("Razorpay order creation", True, 
            f"Order ID: {test_order['id']}")
    except Exception as e:
        all_passed &= test_result("Razorpay order creation", False, str(e))
        
except Exception as e:
    all_passed &= test_result("Razorpay client initialized", False, str(e))

# Test 7: Template files
print_header("7. TEMPLATE FILES CHECK")
import os
templates_to_check = [
    'templates/fees/student_fees.html',
    'templates/fees/payment_initiate.html',
    'templates/fees/payment_method.html',
    'templates/fees/razorpay_gateway.html',
    'templates/fees/payment_success.html',
]

for template in templates_to_check:
    path = os.path.join('/Users/kushalagrawal/prj/LMS-django-', template)
    exists = os.path.exists(path)
    all_passed &= test_result(f"Template: {template.split('/')[-1]}", exists)

# Final Summary
print_header("FINAL QA RESULTS")
if all_passed:
    print("✅ ALL TESTS PASSED - System is ready for use")
    sys.exit(0)
else:
    print("❌ SOME TESTS FAILED - Please review errors above")
    sys.exit(1)
