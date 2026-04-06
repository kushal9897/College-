from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum, Count, Q
import csv
from datetime import datetime
from .models import FeeStructure, StudentFee, Payment


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['program', 'fee_type', 'amount_display', 'academic_year', 'semester', 'is_active']
    list_filter = ['program', 'fee_type', 'academic_year', 'is_active']
    search_fields = ['program__title', 'fee_type', 'academic_year']
    list_editable = ['is_active']
    
    def amount_display(self, obj):
        return f"₹{obj.amount:,.2f}"
    amount_display.short_description = 'Amount'


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'fee_type', 'amount_display', 'paid_display', 'balance_display', 'status_badge', 'due_date']
    list_filter = ['status', 'fee_structure__fee_type', 'due_date']
    search_fields = ['student__student__username', 'student__student__first_name', 'student__student__last_name']
    readonly_fields = ['paid_amount', 'assigned_date']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student', 'fee_structure')
        }),
        ('Fee Details', {
            'fields': ('amount', 'paid_amount', 'status', 'due_date')
        }),
        ('Additional Info', {
            'fields': ('assigned_date', 'remarks')
        }),
    )
    
    def student_name(self, obj):
        return obj.student.student.get_full_name
    student_name.short_description = 'Student Name'
    
    def fee_type(self, obj):
        return obj.fee_structure.fee_type
    fee_type.short_description = 'Fee Type'
    
    def amount_display(self, obj):
        return f"₹{obj.amount:,.2f}"
    amount_display.short_description = 'Amount'
    
    def paid_display(self, obj):
        return f"₹{obj.paid_amount:,.2f}"
    paid_display.short_description = 'Paid'
    
    def balance_display(self, obj):
        balance = obj.balance_amount
        color = 'green' if balance == 0 else 'red' if obj.is_overdue else 'orange'
        return format_html(
            '<span style="color: {}; font-weight: bold;">₹{:,.2f}</span>',
            color, balance
        )
    balance_display.short_description = 'Balance'
    
    def status_badge(self, obj):
        colors = {
            'Paid': '#10b981',
            'Pending': '#f59e0b',
            'Partial': '#3b82f6',
            'Overdue': '#ef4444',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            colors.get(obj.status, '#6b7280'), obj.status
        )
    status_badge.short_description = 'Status'
    
    actions = ['export_to_excel']
    
    def export_to_excel(self, request, queryset):
        """Export selected fees to Excel CSV format"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="student_fees_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Student ID', 'Student Name', 'Program', 'Fee Type', 
            'Amount', 'Paid Amount', 'Balance', 'Status', 'Due Date', 
            'Academic Year', 'Remarks'
        ])
        
        for fee in queryset:
            writer.writerow([
                fee.student.student.username,
                fee.student.student.get_full_name,
                fee.student.department.title if fee.student.department else '',
                fee.fee_structure.fee_type,
                f'{fee.amount:.2f}',
                f'{fee.paid_amount:.2f}',
                f'{fee.balance_amount:.2f}',
                fee.status,
                fee.due_date.strftime('%Y-%m-%d'),
                fee.fee_structure.academic_year,
                fee.remarks or ''
            ])
        
        return response
    export_to_excel.short_description = "Export to Excel (CSV)"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fee-dashboard/', self.admin_site.admin_view(self.fee_dashboard), name='fee-dashboard'),
        ]
        return custom_urls + urls
    
    def fee_dashboard(self, request):
        """Custom dashboard view for fee statistics"""
        total_fees = StudentFee.objects.aggregate(
            total=Sum('amount'),
            total_paid=Sum('paid_amount')
        )
        
        stats = {
            'total_students': StudentFee.objects.values('student').distinct().count(),
            'total_fees': total_fees['total'] or 0,
            'total_collected': total_fees['total_paid'] or 0,
            'total_pending': (total_fees['total'] or 0) - (total_fees['total_paid'] or 0),
            'paid_count': StudentFee.objects.filter(status='Paid').count(),
            'pending_count': StudentFee.objects.filter(status='Pending').count(),
            'partial_count': StudentFee.objects.filter(status='Partial').count(),
            'overdue_count': StudentFee.objects.filter(status='Overdue').count(),
        }
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Fee Dashboard',
            'stats': stats,
        }
        return render(request, 'admin/fee_dashboard.html', context)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'student_name', 'fee_type', 'amount_display', 'payment_method', 'payment_date', 'transaction_id']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['receipt_number', 'transaction_id', 'student_fee__student__student__username']
    readonly_fields = ['receipt_number', 'transaction_id', 'created_at']
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('student_fee', 'amount', 'payment_method')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'receipt_number', 'payment_date', 'received_by')
        }),
        ('Additional Info', {
            'fields': ('remarks', 'created_at')
        }),
    )
    
    def student_name(self, obj):
        return obj.student_fee.student.student.get_full_name
    student_name.short_description = 'Student'
    
    def fee_type(self, obj):
        return obj.student_fee.fee_structure.fee_type
    fee_type.short_description = 'Fee Type'
    
    def amount_display(self, obj):
        return f"₹{obj.amount:,.2f}"
    amount_display.short_description = 'Amount'
    
    actions = ['export_payments_to_excel']
    
    def export_payments_to_excel(self, request, queryset):
        """Export payment records to Excel CSV format"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="payments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Receipt Number', 'Transaction ID', 'Student Name', 'Fee Type',
            'Amount', 'Payment Method', 'Payment Date', 'Received By', 'Remarks'
        ])
        
        for payment in queryset:
            writer.writerow([
                payment.receipt_number,
                payment.transaction_id,
                payment.student_fee.student.student.get_full_name,
                payment.student_fee.fee_structure.fee_type,
                f'{payment.amount:.2f}',
                payment.payment_method,
                payment.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
                payment.received_by or '',
                payment.remarks or ''
            ])
        
        return response
    export_payments_to_excel.short_description = "Export Payments to Excel (CSV)"
