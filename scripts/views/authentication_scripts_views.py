from authentication.models import User
from rest_framework.decorators import api_view


@api_view(['GET'])
def load_users(request, company_id):
    # Logic to load users for the given company_id
    all_users = User.objects.all()
    print("all users : ", all_users)

@api_view(['GET'])
def load_roles(request, company_id):
    pass

@api_view(['GET'])
def load_permissions(request, company_id):
    pass

@api_view(['GET'])
def load_countries(request, company_id):
    pass