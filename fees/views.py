from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.utils import timezone
from django.views.decorators.http import require_POST
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from decimal import Decimal
import uuid
from .models import StudentFee, Payment, PAYMENT_METHOD_CHOICES
from accounts.models import Student


@login_required
def student_fees(request):
    """Display all fees for logged-in student"""
    if not request.user.is_student:
        messages.error(request, "Access denied. This page is only for students.")
        return redirect('home')
    
    try:
        student = Student.objects.get(student=request.user)
        fees = StudentFee.objects.filter(student=student).select_related('fee_structure').order_by('-due_date')
        
        # Calculate totals
        total_amount = sum(fee.amount for fee in fees)
        total_paid = sum(fee.paid_amount for fee in fees)
        total_balance = total_amount - total_paid
        
        # Get payment history
        fee_ids = fees.values_list('id', flat=True)
        payments = Payment.objects.filter(student_fee_id__in=fee_ids).order_by('-payment_date')[:10]
        
        context = {
            'fees': fees,
            'payments': payments,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_balance': total_balance,
        }
        return render(request, 'fees/student_fees.html', context)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('home')


@login_required
def download_receipt(request, payment_id):
    """Generate and download PDF receipt for a payment"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Verify the payment belongs to the logged-in student
    if payment.student_fee.student.student != request.user:
        messages.error(request, "Access denied.")
        return redirect('student_fees')
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6366f1'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#4f46e5'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Header
    elements.append(Paragraph("TechMate - Smart Learning Platform", title_style))
    elements.append(Paragraph("Fee Payment Receipt", heading_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Receipt Details
    receipt_data = [
        ['Receipt Number:', payment.receipt_number],
        ['Transaction ID:', payment.transaction_id],
        ['Date:', payment.payment_date.strftime('%B %d, %Y %I:%M %p')],
    ]
    
    receipt_table = Table(receipt_data, colWidths=[2*inch, 4*inch])
    receipt_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(receipt_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Student Details
    elements.append(Paragraph("Student Information", heading_style))
    student_data = [
        ['Student Name:', payment.student_fee.student.student.get_full_name],
        ['Student ID:', payment.student_fee.student.student.username],
        ['Program:', payment.student_fee.student.department.title if payment.student_fee.student.department else 'N/A'],
        ['Email:', payment.student_fee.student.student.email],
    ]
    
    student_table = Table(student_data, colWidths=[2*inch, 4*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Payment Details
    elements.append(Paragraph("Payment Details", heading_style))
    payment_data = [
        ['Fee Type:', payment.student_fee.fee_structure.fee_type],
        ['Academic Year:', payment.student_fee.fee_structure.academic_year],
        ['Amount Paid:', f"₹{payment.amount:,.2f}"],
        ['Payment Method:', payment.payment_method],
        ['Received By:', payment.received_by or 'System'],
    ]
    
    payment_table = Table(payment_data, colWidths=[2*inch, 4*inch])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('BACKGROUND', (0, 2), (1, 2), colors.HexColor('#dcfce7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTSIZE', (1, 2), (1, 2), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 0.5 * inch))
    
    # Fee Summary
    elements.append(Paragraph("Fee Summary", heading_style))
    summary_data = [
        ['Total Fee Amount:', f"₹{payment.student_fee.amount:,.2f}"],
        ['Amount Paid (This Receipt):', f"₹{payment.amount:,.2f}"],
        ['Total Paid:', f"₹{payment.student_fee.paid_amount:,.2f}"],
        ['Balance Due:', f"₹{payment.student_fee.balance_amount:,.2f}"],
        ['Status:', payment.student_fee.status],
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('BACKGROUND', (0, 3), (1, 3), colors.HexColor('#fef3c7') if payment.student_fee.balance_amount > 0 else colors.HexColor('#dcfce7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTNAME', (1, 3), (1, 4), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTSIZE', (1, 3), (1, 3), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5 * inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("_______________________________________________", footer_style))
    elements.append(Paragraph("This is a computer-generated receipt and does not require a signature.", footer_style))
    elements.append(Paragraph("TechMate - Smart Learning Platform | www.techmate.edu | support@techmate.edu", footer_style))
    elements.append(Paragraph(f"Generated on: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF value
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.receipt_number}.pdf"'
    response.write(pdf)
    
    return response


@login_required
def download_all_fees_pdf(request):
    """Generate PDF with all fee details for student"""
    if not request.user.is_student:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    try:
        student = Student.objects.get(student=request.user)
        fees = StudentFee.objects.filter(student=student).select_related('fee_structure').order_by('-due_date')
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#6366f1'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Header
        elements.append(Paragraph("TechMate - Smart Learning Platform", title_style))
        elements.append(Paragraph("Fee Statement", styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Student Info
        elements.append(Paragraph(f"<b>Student:</b> {student.student.get_full_name}", styles['Normal']))
        elements.append(Paragraph(f"<b>Student ID:</b> {student.student.username}", styles['Normal']))
        elements.append(Paragraph(f"<b>Program:</b> {student.department.title if student.department else 'N/A'}", styles['Normal']))
        elements.append(Paragraph(f"<b>Generated:</b> {timezone.now().strftime('%B %d, %Y')}", styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Fee Table
        fee_data = [['Fee Type', 'Academic Year', 'Amount', 'Paid', 'Balance', 'Status', 'Due Date']]
        
        total_amount = 0
        total_paid = 0
        
        for fee in fees:
            fee_data.append([
                fee.fee_structure.fee_type,
                fee.fee_structure.academic_year,
                f"₹{fee.amount:,.2f}",
                f"₹{fee.paid_amount:,.2f}",
                f"₹{fee.balance_amount:,.2f}",
                fee.status,
                fee.due_date.strftime('%Y-%m-%d')
            ])
            total_amount += fee.amount
            total_paid += fee.paid_amount
        
        # Add totals row
        fee_data.append([
            'TOTAL', '', 
            f"₹{total_amount:,.2f}",
            f"₹{total_paid:,.2f}",
            f"₹{total_amount - total_paid:,.2f}",
            '', ''
        ])
        
        fee_table = Table(fee_data, colWidths=[1.3*inch, 1*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.8*inch, 0.9*inch])
        fee_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f3f4f6')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(fee_table)
        
        # Build PDF
        doc.build(elements)
        
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="fee_statement_{student.student.username}.pdf"'
        response.write(pdf)
        
        return response
        
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('home')
