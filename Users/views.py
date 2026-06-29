from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth, messages
from .models import AdminKey

def register_page(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        admin_key = request.POST.get('admin_key', '')
        
        print(f"DEBUG: Registration attempt - Username: {username}, Email: {email}")
        
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                print(f"DEBUG: Username {username} already exists")
                messages.info(request, 'Username already exists')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                print(f"DEBUG: Email {email} already exists")
                messages.info(request, 'Email already exists')
                return redirect('register')
            else:
                if admin_key == '':
                    user = User.objects.create_user(username=username, password=password1, email=email, first_name=first_name, last_name=last_name)
                    user.save()
                    print(f"DEBUG: User {username} created successfully (ID: {user.id})")
                else:
                    if AdminKey.objects.filter(admin_key=admin_key).exists():
                        user = User.objects.create_user(username=username, password=password1, email=email, first_name=first_name, last_name=last_name)
                        user.is_staff = True
                        user.is_superuser = True
                        user.save()
                        print(f"DEBUG: Admin user {username} created successfully (ID: {user.id})")
                    else:
                        print(f"DEBUG: Invalid admin key: {admin_key}")
                        messages.info(request, 'Invalid admin key')
                        return redirect('register')
                messages.success(request, 'User created successfully')
                return redirect('login')
        else:
            print("DEBUG: Passwords do not match")
            messages.info(request, 'Passwords do not match')
            return redirect('register')
    else:
        return render(request, 'Users/register.html')

def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:   
            messages.info(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'Users/login.html')

def logout_page(request):
    auth.logout(request)
    return render(request, 'Users/logout.html')