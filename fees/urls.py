from django.urls import path
from . import views
from . import payment_views
from . import razorpay_views

urlpatterns = [
    # Fee viewing and reports
    path('my-fees/', views.student_fees, name='student_fees'),
    path('download-receipt/<int:payment_id>/', views.download_receipt, name='download_receipt'),
    path('download-fee-statement/', views.download_all_fees_pdf, name='download_fee_statement'),
    
    # Payment flow
    path('pay/<int:fee_id>/', payment_views.initiate_payment, name='initiate_payment'),
    path('pay/<int:fee_id>/method/', payment_views.payment_method_selection, name='payment_method_selection'),
    path('pay/<int:fee_id>/online/', payment_views.online_payment_gateway, name='online_payment_gateway'),
    path('pay/<int:fee_id>/offline/', payment_views.offline_payment_form, name='offline_payment_form'),
    path('pay/<int:fee_id>/cancel/', payment_views.cancel_payment, name='cancel_payment'),
    
    # Razorpay integration
    path('razorpay/callback/', razorpay_views.razorpay_payment_callback, name='razorpay_callback'),
    path('razorpay/webhook/', razorpay_views.razorpay_webhook, name='razorpay_webhook'),
    
    # Payment confirmation pages
    path('payment/success/', payment_views.payment_success, name='payment_success'),
    path('payment/failed/', payment_views.payment_failed, name='payment_failed'),
    path('payment/offline-submitted/', payment_views.offline_payment_submitted, name='offline_payment_submitted'),
]
