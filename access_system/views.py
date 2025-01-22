from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import update_last_login
from codes.forms import CodeForm
from banking.models import CustomUser, Customer, Transaction, Manager, Device
from codes.models import Code
from django.shortcuts import render, redirect
from .utils import send_sms, validate_and_format_phone
from banking.forms import LoginForm
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import IntegrityError
import json
import re,uuid
from random import randint
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
import base64
from django.urls import reverse
import hashlib
import httpagentparser
import socket,os


def landing_page(request):
    return render(request, 'landing_page.html')

# **************************** CUSTOMER **************************** #
@csrf_exempt
def fetch_customers(request):
    # Fetch all customers and return their details
    customers = Customer.objects.all().values('customer_id', 'name', 'account_number', 'phone_number', 'balance', 'password')
    return JsonResponse(list(customers), safe=False)

@csrf_exempt
def add_customer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            name = data.get('name')
            account_number = data.get('account_number')
            phone_number = data.get('phone_number')
            balance = data.get('balance')
            password = data.get('password')
            device_id = data.get('device_id')
            username = name  # Assuming the username is the customer's name

            # Password policy checks
            password_valid, error_message = password_policy_check(password, username)
            if not password_valid:
                return JsonResponse({'error': error_message}, status=400)

            if not name or not account_number or not phone_number or balance is None or not password or not device_id:
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            # Add the customer to the database
            customer = Customer.objects.create(
                name=name,
                account_number=account_number,
                phone_number=phone_number,
                balance=balance,
                password=password,
                device_id=device_id
            )
            return JsonResponse({
                'customer_id': customer.customer_id,
                'name': customer.name,
                'account_number': customer.account_number,
                'phone_number': customer.phone_number,
                'balance': str(customer.balance),
                'device_id': customer.device_id
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@require_http_methods(["PUT"])
def update_customer(request, customer_id):
    try:
        # Load the request body as JSON
        data = json.loads(request.body)

        # Find the customer by ID
        customer = Customer.objects.get(customer_id=customer_id)

        # Update customer fields
        customer.name = data.get('name')
        customer.account_number = data.get('account_number')
        customer.phone_number = data.get('phone_number')

        # Get the password from the request
        password = data.get('password')
        if password:
            # Check the password against the policy
            is_valid, validation_message = password_policy_check(password, customer.name)
            if not is_valid:
                return JsonResponse({'error': validation_message}, status=400)

            # Store the plain text password
            customer.password = password

        customer.save()
        return JsonResponse({'message': 'Customer updated successfully'}, status=200)

    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def password_policy_check(password, username):
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."
    if not re.search(r'[@$!%*?&#;]', password):
        return False, "Password must contain at least one special character (e.g., @$!%*?&#)."
    if username.lower() in password.lower():
        return False, "Password should not contain the username."
    if len(password) <= 8:
        return False, "Password must be more than 10 characters long."
    if re.search(r'(012|123|234|345|456|567|678|789)', password):
        return False, "Password must not contain consecutive numbers (e.g., 123, 456)."
    return True, ""

@csrf_exempt
def delete_customer(request, customer_id):
    if request.method == 'DELETE':
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            customer.delete()
            return JsonResponse({'success': 'Customer deleted successfully.'})
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def edit_customer(request, customer_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            customer = Customer.objects.get(customer_id=customer_id)
            
            # Update fields with new data
            customer.name = data.get('name', customer.name)
            customer.account_number = data.get('account_number', customer.account_number)
            customer.phone_number = data.get('phone_number', customer.phone_number)
            customer.balance = data.get('balance', customer.balance)
            customer.password = data.get('password', customer.password)  # Update password if provided
            customer.save()

            return JsonResponse({
                'customer_id': customer.customer_id,
                'name': customer.name,
                'account_number': customer.account_number,
                'phone_number': customer.phone_number,
                'balance': str(customer.balance),
                'password': customer.password  # Include password in the response if needed
            })
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
        
@csrf_exempt
def add_transaction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            customer_name = data.get('customer_name')
            account_number = data.get('account_number')
            amount = data.get('amount')
            date = data.get('date')
            time = data.get('time')
            transaction_type = data.get('transaction_type')

            # Validate data
            if not all([customer_name, account_number, amount, date, time, transaction_type]):
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            # Create the transaction in the database
            transaction = Transaction.objects.create(
                date=date,
                time=time,
                account_number=account_number,
                customer_name=customer_name,
                amount=amount,
                transaction_type=transaction_type
            )

            return JsonResponse({
                'id': transaction.id,
                'date': str(transaction.date),
                'time': str(transaction.time),
                'customer_name': transaction.customer_name,
                'account_number': transaction.account_number,
                'amount': str(transaction.amount),
                'transaction_type': transaction.transaction_type
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# ************************************* MANAGER **************************** #
@csrf_exempt
def fetch_manager(request):
    managers = Manager.objects.all().values('manager_id', 'name', 'level', 'phone_number', 'years_of_experience', 'password')
    print(managers)
    return JsonResponse(list(managers), safe=False)

@csrf_exempt
def add_manager(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            name = data.get('name')
            level = data.get('level')
            phone_number = data.get('phone_number')
            years_of_experience = data.get('experience')
            password = data.get('password')
            username = name  # Assuming the username is the manager's name

            # Password policy checks
            password_valid, error_message = password_policy_check(password, username)
            if not password_valid:
                return JsonResponse({'error': error_message}, status=400)

            if not name or not level or not phone_number or years_of_experience is None:
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            # Add the manager to the database
            manager = Manager.objects.create(
                name=name,
                level=level,
                phone_number=phone_number,
                years_of_experience=years_of_experience,
                password=password
            )
            return JsonResponse({
                'manager_id': manager.manager_id,
                'name': manager.name,
                'level': manager.level,
                'phone_number': manager.phone_number,
                'years_of_experience': str(manager.years_of_experience),
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@require_http_methods(["PUT"])
def update_manager(request, manager_id):
    try:
        # Load the request body as JSON
        data = json.loads(request.body)

        # Find the manager by ID
        manager = Manager.objects.get(manager_id=manager_id)

        # Update manager fields
        manager.name = data.get('name')
        manager.level = data.get('level')
        manager.phone_number = data.get('phone_number')
        manager.years_of_experience = data.get('years_of_experience')

        # Get the password from the request
        password = data.get('password')
        if password:
            # Check the password against the policy
            is_valid, validation_message = password_policy_check(password, manager.name)
            if not is_valid:
                return JsonResponse({'error': validation_message}, status=400)

            # Store the plain text password
            manager.password = password

        manager.save()
        return JsonResponse({'message': 'Manager updated successfully'}, status=200)

    except Manager.DoesNotExist:
        return JsonResponse({'error': 'Manager not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def delete_manager(request, manager_id):
    if request.method == 'DELETE':
        try:
            manager = Manager.objects.get(manager_id=manager_id)
            manager.delete()
            return JsonResponse({'success': 'Manager deleted successfully.'})
        except Manager.DoesNotExist:
            return JsonResponse({'error': 'Manager not found.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def edit_manager(request, manager_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            manager = Manager.objects.get(manager_id=manager_id)
            
            # Update fields with new data
            manager.name = data.get('name', manager.name)
            manager.level = data.get('level', manager.level)
            manager.phone_number = data.get('phone_number', manager.phone_number)
            manager.years_of_experience = data.get('years_of_experience', manager.years_of_experience)
            manager.password = data.get('password', manager.password)  # Update password if provided
            manager.save()

            return JsonResponse({
                'manager_id': manager.manager_id,
                'name': manager.name,
                'level': manager.level,
                'phone_number': manager.phone_number,
                'years_of_experience': manager.years_of_experience,
                'password': manager.password  # Include password in the response if needed
            })
        except Manager.DoesNotExist:
            return JsonResponse({'error': 'Manager not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

# Admin Dashboard view (to render the HTML page)

def admin_dashboard(request):
    customers = Customer.objects.all()  
    transactions = Transaction.objects.all()
    managers = Manager.objects.all()
    return render(request, 'admin_dashboard.html', {'customers': customers, 'transactions': transactions, 'managers':managers})

def manager_dashboard(request):
    transactions = Transaction.objects.all()
    return render(request, 'manager_dashboard.html',{'transactions': transactions})

def customer_dashboard(request):
    customer_data = request.session.get('customer_data')
    if not customer_data:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('login-view')
    return render(request, 'customer_dashboard.html', {'customer_data': customer_data})

def main_page(request):
    return render(request, 'main.html') 

def auth_view(request):
    form = AuthenticationForm()
    role = request.GET.get('role')
    request.session['role'] = role
    print(role)
    if request.method == "POST":
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')

        if role == 'manager':
            print("Hello manager")
            manager = Manager.objects.get(name=username)
            if manager.password == password:
                request.session['pk'] = manager.manager_id
                return redirect('verify-view')

        if role == 'customer':
            try:
                customer = Customer.objects.get(name=username)
                if customer.is_locked:
                    request.session['pk'] = customer.customer_id
                    messages.error(request, 'Account is locked. Please contact the admin.')
                    return redirect('auth-view')

                if customer.password == password:  
                    request.session['pk'] = customer.customer_id
                    request.session['role'] = 'customer'
                    customer.failed_attempts = 0
                    customer.save()
                    return redirect('verify-view')  
                else:
                    request.session['pk'] = customer.customer_id
                    customer.failed_attempts += 1
                    if customer.failed_attempts == 3:
                        return redirect('generate_qr')  

                    if customer.failed_attempts >= 3:
                        customer.is_locked = True
                        messages.error(request, 'Account is locked.')
                    else:
                        messages.error(request, 'Invalid credentials.')

                    customer.save()
            except Customer.DoesNotExist:
                messages.error(request, 'Customer does not exist.')

        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                request.session['pk'] = user.pk
                request.session['role'] = role
                return redirect('verify-view')
            else:
                messages.error(request, 'Invalid credentials.')

    return render(request, 'auth.html', {'form': form, 'role': role})

def verify_view(request):
    form = CodeForm(request.POST or None)
    pk = request.session.get('pk') 
    role = request.session.get('role')  
    if role == 'admin':
        try:
            user = CustomUser.objects.get(pk=pk)  
            code = Code.objects.get(user=user) 
            if not request.POST:
                print(f"User phone number: {user.phone_number}")
                code_user = f"{user.username}: {code.number}"
                print(code_user)
                formatted_number = validate_and_format_phone(f"+91{user.phone_number}")
                send_sms(code_user, formatted_number)
            if request.method == 'POST' and form.is_valid():
                num = form.cleaned_data.get('number')
                if str(code.number) == num:
                    login(request, user)
                    return redirect('admin-dashboard')  
                else:
                    messages.error(request, 'Invalid verification code. Please try again.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Admin user does not exist. Please log in again.')
            return redirect('login-view')  

    if role == "customer" or role =="manager":
        if 'verification_code' not in request.session:
            verification_code = str(randint(10000, 99999))
            request.session['verification_code'] = verification_code
            print(f"Generated verification code for {role}: {verification_code}")
        if request.method == 'POST' and form.is_valid():
            entered_code = form.cleaned_data.get('number')  
            if str(entered_code) == request.session.get('verification_code'):
                if role == 'customer':
                    request.session['customer_logged_in'] = True 
                    customer = Customer.objects.get(pk=pk)
                    customer_data = {
                        'name': customer.name,
                        'account_number': customer.account_number,
                        'phone_number': customer.phone_number,
                        'balance': float(customer.balance) 
                    }
                    request.session['customer_data'] = customer_data
                    return redirect('customer-dashboard')
                elif role == 'manager':
                    request.session['manager_logged_in'] = True  
                    return redirect('manager-dashboard')
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
    return render(request, 'verify.html', {'form': form})


@csrf_exempt
def unlock_customer(request, customer_id):
    if request.method == 'POST':
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            customer.failed_attempts = 0  
            customer.is_locked = False    
            customer.save()
            return JsonResponse({'message': 'Customer account unlocked successfully.'})
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

def get_local_ip():
    host_name = socket.gethostname()
    local_ip = socket.gethostbyname(host_name)
    return local_ip

def generate_qr(request):
    server_ip = get_local_ip() 
    port = os.getenv('SERVER_PORT', '8000')     
    url = f"http://{server_ip}:{port}{reverse('verify_device')}"
    qr = qrcode.make(url)  
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return render(request, 'generate_qr.html', {'qr_code_data': qr_code_data})

def verify_device(request):
    device_id = str(uuid.uuid4())[:10]  
    if 'device_id' in request.session:
        device_id = request.session['device_id']
    else:
        request.session['device_id'] = device_id
        if request.user.is_authenticated:
            customer = Customer.objects.get(name=request.user.username)
            customer.device_id = device_id
            customer.save()
    return HttpResponse(f"Your device ID: {device_id}")

def check_device_id(request):
    role = request.session.get('role')
    if request.method == 'POST':
        input_device_id = request.POST.get('device_id')
        username = request.POST.get('username')  
        try:
            customer = Customer.objects.get(name=username)
            if not customer.device_id:
                customer.device_id = input_device_id  
                customer.save()
                return redirect('verify-view') 
            elif customer.device_id == input_device_id:
                return redirect('verify-view')  
            else:
                return HttpResponse("Device ID does not match. Verification failed.")

        except Customer.DoesNotExist:
            return HttpResponse("Customer not found.")
    return render(request, 'check_device_id.html')