from django.db import models
from django.utils import timezone
from accounts.models import Student
from course.models import Program

# Fee Types
SEMESTER_FEE = "Semester Fee"
REGISTRATION_FEE = "Registration Fee"
EXAM_FEE = "Exam Fee"

FEE_TYPE_CHOICES = (
    (SEMESTER_FEE, "Semester Fee"),
    (REGISTRATION_FEE, "Registration Fee"),
    (EXAM_FEE, "Exam Fee"),
)

# Payment Status
PENDING = "Pending"
PAID = "Paid"
PARTIAL = "Partial"
OVERDUE = "Overdue"

PAYMENT_STATUS_CHOICES = (
    (PENDING, "Pending"),
    (PAID, "Paid"),
    (PARTIAL, "Partial"),
    (OVERDUE, "Overdue"),
)

# Payment Method
CASH = "Cash"
CARD = "Card"
UPI = "UPI"
NET_BANKING = "Net Banking"
CHEQUE = "Cheque"

PAYMENT_METHOD_CHOICES = (
    (CASH, "Cash"),
    (CARD, "Card"),
    (UPI, "UPI"),
    (NET_BANKING, "Net Banking"),
    (CHEQUE, "Cheque"),
)


class FeeStructure(models.Model):
    """Define fee amounts for different programs and fee types"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='fee_structures')
    fee_type = models.CharField(max_length=50, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    semester = models.CharField(max_length=20, blank=True, null=True, help_text="e.g., 1st, 2nd")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fee Structure"
        verbose_name_plural = "Fee Structures"
        ordering = ['-academic_year', 'program', 'fee_type']

    def __str__(self):
        return f"{self.program.title} - {self.fee_type} - ₹{self.amount}"


class StudentFee(models.Model):
    """Track fees assigned to students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PENDING)
    due_date = models.DateField()
    assigned_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Student Fee"
        verbose_name_plural = "Student Fees"
        ordering = ['-due_date', 'student']

    def __str__(self):
        return f"{self.student} - {self.fee_structure.fee_type} - ₹{self.amount}"

    @property
    def balance_amount(self):
        return self.amount - self.paid_amount

    @property
    def is_overdue(self):
        if self.status != PAID and self.due_date < timezone.now().date():
            return True
        return False

    def update_payment_status(self):
        """Update payment status based on paid amount"""
        if self.paid_amount >= self.amount:
            self.status = PAID
        elif self.paid_amount > 0:
            self.status = PARTIAL
        elif self.is_overdue:
            self.status = OVERDUE
        else:
            self.status = PENDING
        self.save()


class Payment(models.Model):
    """Track individual payments made by students"""
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(default=timezone.now)
    received_by = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    receipt_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment #{self.receipt_number} - {self.student_fee.student} - ₹{self.amount}"

    def save(self, *args, **kwargs):
        # Generate receipt number if not exists
        if not self.receipt_number:
            import random
            self.receipt_number = f"TM{timezone.now().year}{random.randint(10000, 99999)}"
        
        # Generate transaction ID if not exists
        if not self.transaction_id:
            import uuid
            self.transaction_id = str(uuid.uuid4())[:12].upper()
        
        # Check if this is a new payment
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Update student fee paid amount and status only for new payments
        if is_new:
            from decimal import Decimal
            self.student_fee.paid_amount = Decimal(str(self.student_fee.paid_amount)) + Decimal(str(self.amount))
            self.student_fee.update_payment_status()
