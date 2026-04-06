"""
Payment Processing Views for TechMate Fee Payment System
Complete payment flow like real college websites
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import uuid
import random
import razorpay
import json
from .models import StudentFee, Payment
from accounts.models import Student

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def initiate_payment(request, fee_id):
    """Step 1: Payment initiation - Select fee to pay"""
    if not request.user.is_student:
        messages.error(request, "Access denied. This page is only for students.")
        return redirect('home')
    
    try:
        student = Student.objects.get(student=request.user)
        fee = get_object_or_404(StudentFee, id=fee_id, student=student)
        
        # Check if already paid
        if fee.status == 'Paid':
            messages.info(request, "This fee has already been paid in full.")
            return redirect('student_fees')
        
        context = {
            'fee': fee,
            'balance': fee.balance_amount,
        }
        return render(request, 'fees/payment_initiate.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('home')


@login_required
def payment_method_selection(request, fee_id):
    """Step 2: Choose payment method (Online/Offline)"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    try:
        student = Student.objects.get(student=request.user)
        fee = get_object_or_404(StudentFee, id=fee_id, student=student)
        
        if fee.status == 'Paid':
            messages.info(request, "This fee has already been paid.")
            return redirect('student_fees')
        
        if request.method == 'POST':
            payment_mode = request.POST.get('payment_mode')
            amount = Decimal(request.POST.get('amount', fee.balance_amount))
            
            # Validate amount
            if amount <= 0:
                messages.error(request, "Please enter a valid amount.")
                return redirect('payment_method_selection', fee_id=fee_id)
            
            if amount > fee.balance_amount:
                messages.error(request, "Payment amount cannot exceed balance due.")
                return redirect('payment_method_selection', fee_id=fee_id)
            
            # Store payment details in session
            request.session['pending_payment'] = {
                'fee_id': fee_id,
                'amount': str(amount),
                'payment_mode': payment_mode,
            }
            
            if payment_mode == 'online':
                return redirect('online_payment_gateway', fee_id=fee_id)
            else:
                return redirect('offline_payment_form', fee_id=fee_id)
        
        context = {
            'fee': fee,
            'balance': fee.balance_amount,
        }
        return render(request, 'fees/payment_method.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('home')


@login_required
def online_payment_gateway(request, fee_id):
    """Step 3a: Online Payment Gateway (Razorpay Integration or Mock)"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    pending_payment = request.session.get('pending_payment')
    if not pending_payment or pending_payment['fee_id'] != fee_id:
        messages.error(request, "Invalid payment session.")
        return redirect('student_fees')
    
    try:
        student = Student.objects.get(student=request.user)
        fee = get_object_or_404(StudentFee, id=fee_id, student=student)
        amount = Decimal(pending_payment['amount'])
        
        # Check if Razorpay is enabled
        if settings.RAZORPAY_ENABLED:
            # Real Razorpay integration
            amount_paise = int(amount * 100)
            
            razorpay_order = razorpay_client.order.create({
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': f'FEE_{fee_id}_{timezone.now().strftime("%Y%m%d%H%M%S")}',
                'notes': {
                    'student_id': student.student.username,
                    'student_name': student.student.get_full_name,
                    'fee_type': fee.fee_structure.fee_type,
                    'fee_id': fee_id,
                }
            })
            
            request.session['razorpay_order'] = {
                'order_id': razorpay_order['id'],
                'amount': amount_paise,
                'fee_id': fee_id,
            }
            
            context = {
                'fee': fee,
                'amount': amount,
                'amount_paise': amount_paise,
                'student': student,
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
                'currency': 'INR',
            }
            return render(request, 'fees/razorpay_gateway.html', context)
        else:
            # Mock payment gateway for testing
            if request.method == 'POST':
                payment_method = request.POST.get('payment_method', 'UPI')
                
                # Simulate payment processing (80% success rate)
                success = random.choice([True, True, True, True, False])
                transaction_ref = f"MOCK{timezone.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
                
                if success:
                    # Create payment record
                    payment = Payment.objects.create(
                        student_fee=fee,
                        amount=amount,
                        payment_method=payment_method,
                        transaction_id=transaction_ref,
                        payment_date=timezone.now(),
                        received_by='Mock Payment Gateway',
                        remarks=f'Test payment via {payment_method}'
                    )
                    
                    # Clear session
                    if 'pending_payment' in request.session:
                        del request.session['pending_payment']
                    
                    # Store success details
                    request.session['payment_success'] = {
                        'payment_id': payment.id,
                        'transaction_ref': transaction_ref,
                        'amount': str(amount),
                        'method': payment_method,
                    }
                    
                    return redirect('payment_success')
                else:
                    # Payment failed
                    request.session['payment_failure'] = {
                        'transaction_ref': transaction_ref,
                        'amount': str(amount),
                        'reason': 'Payment declined. Please try again.',
                    }
                    return redirect('payment_failed')
            
            # Show mock gateway page
            context = {
                'fee': fee,
                'amount': amount,
                'student': student,
                'mock_mode': True,
            }
            return render(request, 'fees/online_gateway.html', context)
        
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('student_fees')


@login_required
def offline_payment_form(request, fee_id):
    """Step 3b: Offline Payment Request Form"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    pending_payment = request.session.get('pending_payment')
    if not pending_payment or pending_payment['fee_id'] != fee_id:
        messages.error(request, "Invalid payment session.")
        return redirect('student_fees')
    
    try:
        student = Student.objects.get(student=request.user)
        fee = get_object_or_404(StudentFee, id=fee_id, student=student)
        amount = Decimal(pending_payment['amount'])
        
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method')  # Cash, Cheque
            remarks = request.POST.get('remarks', '')
            
            # For offline payments, create a pending payment record
            # In a real system, this would be verified by admin
            payment = Payment.objects.create(
                student_fee=fee,
                amount=amount,
                payment_method=payment_method,
                payment_date=timezone.now(),
                received_by='Pending Verification',
                remarks=f'Offline payment request via {payment_method}. {remarks}'
            )
            
            # Clear session
            del request.session['pending_payment']
            
            # Store success details
            request.session['offline_payment_submitted'] = {
                'payment_id': payment.id,
                'receipt_number': payment.receipt_number,
                'amount': str(amount),
                'method': payment_method,
            }
            
            return redirect('offline_payment_submitted')
        
        context = {
            'fee': fee,
            'amount': amount,
            'student': student,
        }
        return render(request, 'fees/offline_payment.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('home')


@login_required
def payment_success(request):
    """Payment Success Confirmation Page"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    payment_data = request.session.get('payment_success')
    if not payment_data:
        messages.error(request, "No payment information found.")
        return redirect('student_fees')
    
    try:
        payment = Payment.objects.get(id=payment_data['payment_id'])
        
        context = {
            'payment': payment,
            'transaction_ref': payment_data['transaction_ref'],
        }
        
        # Clear session data after displaying
        if 'payment_success' in request.session:
            del request.session['payment_success']
        
        return render(request, 'fees/payment_success.html', context)
        
    except Payment.DoesNotExist:
        messages.error(request, "Payment record not found.")
        return redirect('student_fees')


@login_required
def payment_failed(request):
    """Payment Failure Page"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    failure_data = request.session.get('payment_failure')
    if not failure_data:
        messages.error(request, "No payment information found.")
        return redirect('student_fees')
    
    context = {
        'transaction_ref': failure_data['transaction_ref'],
        'amount': failure_data['amount'],
        'reason': failure_data['reason'],
    }
    
    # Clear session data
    if 'payment_failure' in request.session:
        del request.session['payment_failure']
    
    return render(request, 'fees/payment_failed.html', context)


@login_required
def offline_payment_submitted(request):
    """Offline Payment Submission Confirmation"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    submission_data = request.session.get('offline_payment_submitted')
    if not submission_data:
        messages.error(request, "No submission information found.")
        return redirect('student_fees')
    
    try:
        payment = Payment.objects.get(id=submission_data['payment_id'])
        
        context = {
            'payment': payment,
        }
        
        # Clear session data
        if 'offline_payment_submitted' in request.session:
            del request.session['offline_payment_submitted']
        
        return render(request, 'fees/offline_submitted.html', context)
        
    except Payment.DoesNotExist:
        messages.error(request, "Payment record not found.")
        return redirect('student_fees')


@login_required
@require_POST
def cancel_payment(request, fee_id):
    """Cancel payment process"""
    if 'pending_payment' in request.session:
        del request.session['pending_payment']
    
    messages.info(request, "Payment cancelled.")
    return redirect('student_fees')
