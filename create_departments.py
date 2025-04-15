import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_system.settings')
django.setup()

# Import required models
from polls.models import Department

def create_default_departments():
    """Create default departments if they don't exist."""
    default_departments = [
        {
            'name': 'Computer Science',
            'description': 'Department focused on computing technologies, programming, and computer engineering.'
        },
        {
            'name': 'Law',
            'description': 'Department focused on legal studies, regulations, and judiciary matters.'
        },
        {
            'name': 'Marketing',
            'description': 'Department focused on business promotion, advertising strategies, and market research.'
        }
    ]
    
    created = 0
    for dept_data in default_departments:
        department, created_now = Department.objects.get_or_create(
            name=dept_data['name'],
            defaults={'description': dept_data['description']}
        )
        if created_now:
            created += 1
            print(f"Created department: {department.name}")
        else:
            print(f"Department already exists: {department.name}")
    
    print(f"Created {created} new departments")

if __name__ == "__main__":
    create_default_departments() 