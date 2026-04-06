"""
Razorpay Payment Verification and Callback Handlers
"""

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
import razorpay
import json
from decimal import Decimal
from .models import StudentFee, Payment
from accounts.models import Student

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def razorpay_payment_callback(request):
    """Handle Razorpay payment response"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Get payment details from Razorpay
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            
            # Get order details from session
            razorpay_order = request.session.get('razorpay_order')
            if not razorpay_order:
                messages.error(request, "Invalid payment session.")
                return redirect('student_fees')
            
            # Verify payment signature
            try:
                razorpay_client.utility.verify_payment_signature({
                    'razorpay_order_id': order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature
                })
                payment_verified = True
            except razorpay.errors.SignatureVerificationError:
                payment_verified = False
            
            if payment_verified:
                # Fetch payment details from Razorpay
                payment_details = razorpay_client.payment.fetch(payment_id)
                
                # Get student and fee
                student = Student.objects.get(student=request.user)
                fee_id = razorpay_order['fee_id']
                fee = StudentFee.objects.get(id=fee_id, student=student)
                
                # Convert amount from paise to rupees
                amount = Decimal(razorpay_order['amount']) / 100
                
                # Determine payment method from Razorpay
                method = payment_details.get('method', 'online').upper()
                if method == 'CARD':
                    payment_method = 'Card'
                elif method == 'UPI':
                    payment_method = 'UPI'
                elif method == 'NETBANKING':
                    payment_method = 'Net Banking'
                elif method == 'WALLET':
                    payment_method = 'Wallet'
                else:
                    payment_method = 'Online'
                
                # Create payment record
                payment = Payment.objects.create(
                    student_fee=fee,
                    amount=amount,
                    payment_method=payment_method,
                    transaction_id=payment_id,
                    payment_date=timezone.now(),
                    received_by='Razorpay Payment Gateway',
                    remarks=f'Razorpay Order: {order_id}'
                )
                
                # Clear session data
                if 'pending_payment' in request.session:
                    del request.session['pending_payment']
                if 'razorpay_order' in request.session:
                    del request.session['razorpay_order']
                
                # Store success details
                request.session['payment_success'] = {
                    'payment_id': payment.id,
                    'transaction_ref': payment_id,
                    'amount': str(amount),
                    'method': payment_method,
                }
                
                return redirect('payment_success')
            else:
                # Payment verification failed
                request.session['payment_failure'] = {
                    'transaction_ref': payment_id,
                    'amount': str(Decimal(razorpay_order['amount']) / 100),
                    'reason': 'Payment verification failed. Please contact support if amount was deducted.',
                }
                return redirect('payment_failed')
                
        except Exception as e:
            messages.error(request, f"Payment processing error: {str(e)}")
            return redirect('student_fees')
    
    return redirect('student_fees')


@csrf_exempt
def razorpay_webhook(request):
    """Handle Razorpay webhooks for payment status updates"""
    if request.method == 'POST':
        try:
            # Get webhook signature
            webhook_signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE')
            webhook_body = request.body.decode('utf-8')
            
            # Verify webhook signature (optional but recommended)
            # razorpay_client.utility.verify_webhook_signature(webhook_body, webhook_signature, settings.RAZORPAY_WEBHOOK_SECRET)
            
            # Parse webhook data
            data = json.loads(webhook_body)
            event = data.get('event')
            
            if event == 'payment.captured':
                # Payment was successful
                payment_entity = data['payload']['payment']['entity']
                payment_id = payment_entity['id']
                
                # You can add additional processing here
                # For now, we'll just return success
                return JsonResponse({'status': 'ok'})
            
            elif event == 'payment.failed':
                # Payment failed
                return JsonResponse({'status': 'ok'})
            
            return JsonResponse({'status': 'ok'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'invalid method'}, status=405)
