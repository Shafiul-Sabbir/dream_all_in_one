from payments.models import Agent
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from authentication.models import User, Company, Role
from payments.serializers.agent_serializers import AgentSerializer, AgentListSerializer
from payments.utils import get_unique_username

@api_view(['POST'])
def createAgent(request):
    data = request.data
    print("data : ", data)

    company_id = data.get('company_id', None)
    print("company id is : ", company_id)
    email = data.get('email', None)
    print("email id is : ", email)

    company = Company.objects.get(id=company_id)
    print("company is : ", company)


    user = User.objects.filter(company=company, email=email).first()

    if user:
        print("user is : ", user)
        agent = Agent.objects.filter(company=company_id, user=user).first()
        if agent:
            return Response({
                "message" : "Both User & Agent with this email is already exists. "
            })
        else:
            agent_data = {}
            agent_data['company'] = company.id
            agent_data['user'] = user.id
            agent_data['phone'] = data.get('phone', None)
            agent_data['coupon_text'] = data.get('coupon_text', None) 
            agent_data['discount_type'] = data.get('discount_type', None) 
            agent_data['discount_percentage'] = data.get('discount_percentage', None) 
            agent_data['discount_value'] = data.get('discount_value', None) 
            agent_data['coupon_start_date'] = data.get('coupon_start_date', None) 
            agent_data['coupon_end_date'] = data.get('coupon_end_date', None) 
            agent_data['reference_no'] = data.get('reference_no', None) 
            agent_data['commission_type'] = data.get('commission_type', None) 
            agent_data['commission_percentage'] = data.get('commission_percentage', None) 
            agent_data['commission_value'] = data.get('commission_value', None) 

            print("agent data is : ", agent_data)
            serializer = AgentSerializer(data=agent_data)
            if serializer.is_valid():
                serializer.save()
                print("agent created successfully...")
                return Response({
                   "message": "agent created successfully...",
                   "agent_data" : serializer.data
                }, status=201)
            else:
                return Response({
                   "message": "agent creation failed...",
                   "errors" : serializer.errors
                }, status=400)

    else:
        user_data = {}
        username = get_unique_username(data.get('first_name', None), data.get('last_name', None))
        role, _ = Role.objects.get_or_create(name="AGENT")

        user_data['company'] = company
        user_data['first_name'] = data.get('first_name', None)
        user_data['last_name'] = data.get('last_name', None)
        user_data['email'] = data.get('email', None)
        user_data['primary_phone'] = data.get('phone', None)
        user_data['password'] = data.get('password', None)
        user_data['gender'] = data.get('gender', '')
    
        print("user data is : ", user_data)
        user = User.objects.create_user(**user_data)
        if user:
            user.username = username
            user.role = role
            user.save()
            print(f"user created successfully. User id is : {user.id}")

        else:
            print("user creation failed...")
            return Response({
                "message": "user creation failed...",
            }, status=400) 


        agent_data = {}
        agent_data['company'] = company.id
        agent_data['user'] = user.id
        agent_data['phone'] = data.get('phone', None)
        agent_data['coupon_text'] = data.get('coupon_text', None) 
        agent_data['discount_type'] = data.get('discount_type', None) 
        agent_data['discount_percentage'] = data.get('discount_percentage', None) 
        agent_data['discount_value'] = data.get('discount_value', None) 
        agent_data['coupon_start_date'] = data.get('coupon_start_date', None) 
        agent_data['coupon_end_date'] = data.get('coupon_end_date', None) 
        agent_data['reference_no'] = data.get('reference_no', None) 
        agent_data['commission_type'] = data.get('commission_type', None) 
        agent_data['commission_percentage'] = data.get('commission_percentage', None) 
        agent_data['commission_value'] = data.get('commission_value', None) 

        print("agent data is : ", agent_data)
        serializer = AgentSerializer(data=agent_data)
        if serializer.is_valid():
            serializer.save()
            print("agent created successfully...")
            return Response({
                "message": "Both User & Agent created successfully...",
                "agent_data" : serializer.data
            }, status=201)
        else:
            print("agent creation failed...")
            return Response({
                "message": "agent creation failed...",
                "errors" : serializer.errors
            }, status=400)



@api_view(['POST'])
def simpleAgentCreation(request):
    data = request.data
    print("data : ", data)

    company_id = data.get('company_id', None)
    print("company id is : ", company_id)
    email = data.get('email', None)
    print("email id is : ", email)

    company = Company.objects.get(id=company_id)
    print("company is : ", company)


    user = User.objects.filter(company=company, email=email).first()

    if user:
        print("user is : ", user)
        agent = Agent.objects.filter(company=company_id, user=user).first()
        if agent:
            return Response({
                "message" : "Both User & Agent with this email is already exists . "
            })
        else:
            agent_data = {}
            agent_data['company'] = company.id
            agent_data['user'] = user.id
            agent_data['phone'] = data.get('phone', None)

            print("agent data is : ", agent_data)
            serializer = AgentSerializer(data=agent_data)
            if serializer.is_valid():
                serializer.save()
                print("agent created successfully from simple creation...")
                return Response({
                   "message": "agent created successfully from simple creation...",
                   "agent_data" : serializer.data
                }, status=201)
            else:
                return Response({
                   "message": "agent creation failed from simple creation...",
                   "errors" : serializer.errors
                }, status=400)

    else:
        user_data = {}
        username = get_unique_username(data.get('first_name', None), data.get('last_name', None))
        role, _ = Role.objects.get_or_create(name="AGENT")

        user_data['company'] = company
        user_data['first_name'] = data.get('first_name', None)
        user_data['last_name'] = data.get('last_name', None)
        user_data['email'] = data.get('email', None)
        user_data['primary_phone'] = data.get('phone', None)
        user_data['password'] = data.get('password', None)
        user_data['gender'] = data.get('gender', '')
    
        print("user data is : ", user_data)
        user = User.objects.create_user(**user_data)
        if user:
            user.username = username
            user.role = role
            user.save()
            print(f"user created successfully from simple creation. User id is : {user.id}")

        else:
            print("user creation failed...")
            return Response({
                "message": "user creation failed...",
            }, status=400) 


        agent_data = {}
        agent_data['company'] = company.id
        agent_data['user'] = user.id
        agent_data['phone'] = data.get('phone', None)

        print("agent data is : ", agent_data)
        serializer = AgentSerializer(data=agent_data)
        if serializer.is_valid():
            serializer.save()
            print("agent created successfully from simple creation...")
            return Response({
                "message": "Both User & Agent created successfully...",
                "agent_data" : serializer.data
            }, status=201)
        else:
            print("agent creation failed from simple creation...")
            return Response({
                "message": "agent creation failed...",
                "errors" : serializer.errors
            }, status=400)