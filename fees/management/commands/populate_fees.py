"""
Django Management Command to Populate Fee Data for TechMate
Creates fee structures and assigns fees to all students
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from fees.models import FeeStructure, StudentFee, Payment
from accounts.models import Student
from course.models import Program

class Command(BaseCommand):
    help = 'Populate fee structures and assign fees to students'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting fee data population...'))
        
        # Get all programs
        programs = Program.objects.all()
        
        if not programs.exists():
            self.stdout.write(self.style.ERROR('No programs found! Please create programs first.'))
            return
        
        # Create Fee Structures for each program
        academic_year = "2024-2025"
        fee_types_amounts = {
            'Semester Fee': 45000.00,
            'Registration Fee': 5000.00,
            'Exam Fee': 2500.00,
        }
        
        self.stdout.write('\nCreating fee structures...')
        structures_created = 0
        
        for program in programs:
            for fee_type, amount in fee_types_amounts.items():
                structure, created = FeeStructure.objects.get_or_create(
                    program=program,
                    fee_type=fee_type,
                    academic_year=academic_year,
                    defaults={
                        'amount': amount,
                        'is_active': True,
                    }
                )
                if created:
                    structures_created += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ Created: {program.title} - {fee_type} - ₹{amount:,.2f}'
                    ))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Created {structures_created} fee structures'))
        
        # Assign fees to all students
        self.stdout.write('\nAssigning fees to students...')
        students = Student.objects.all().select_related('department')
        
        fees_assigned = 0
        today = timezone.now().date()
        
        for student in students:
            if not student.department:
                continue
            
            # Get fee structures for student's program
            fee_structures = FeeStructure.objects.filter(
                program=student.department,
                academic_year=academic_year,
                is_active=True
            )
            
            for structure in fee_structures:
                # Set different due dates for different fee types
                if structure.fee_type == 'Registration Fee':
                    due_date = today + timedelta(days=30)
                elif structure.fee_type == 'Semester Fee':
                    due_date = today + timedelta(days=60)
                else:  # Exam Fee
                    due_date = today + timedelta(days=90)
                
                # Create StudentFee if it doesn't exist
                student_fee, created = StudentFee.objects.get_or_create(
                    student=student,
                    fee_structure=structure,
                    defaults={
                        'amount': structure.amount,
                        'due_date': due_date,
                        'status': 'Pending',
                    }
                )
                
                if created:
                    fees_assigned += 1
                    
                    # Randomly mark some fees as paid (for demo purposes)
                    import random
                    if random.random() < 0.3:  # 30% chance
                        payment_amount = structure.amount
                        Payment.objects.create(
                            student_fee=student_fee,
                            amount=payment_amount,
                            payment_method=random.choice(['Cash', 'UPI', 'Card', 'Net Banking']),
                            payment_date=timezone.now() - timedelta(days=random.randint(1, 20)),
                            received_by='Admin Office',
                            remarks='Sample payment for demonstration'
                        )
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Assigned {fees_assigned} fees to students'))
        
        # Display summary
        total_students = Student.objects.count()
        total_fees = StudentFee.objects.count()
        total_payments = Payment.objects.count()
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('✅ Fee Data Population Complete!'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f'  Students: {total_students}')
        self.stdout.write(f'  Total Fees Assigned: {total_fees}')
        self.stdout.write(f'  Sample Payments Created: {total_payments}')
        self.stdout.write(f'  Fee Structures: {structures_created}')
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write('\n📊 Students can now view fees at: /fees/my-fees/')
        self.stdout.write('🔧 Admin can manage fees at: /admin/fees/')
        self.stdout.write(self.style.SUCCESS('='*70))
