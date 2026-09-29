from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm, UpdateForm
from django.contrib.auth.models import User
from django.contrib import messages
from ecommerce.constants import request_method_enum
from payment.forms import ShippingForm
from payment.models import Shipping_Address
from django.contrib.sites.shortcuts import get_current_site
from .token import user_tokenizer_generate
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.http import HttpResponseNotAllowed

def register(request):
    allowed_methods = list(request_method_enum.keys())
    if request.method not in allowed_methods:
        return HttpResponseNotAllowed(allowed_methods)
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            current_site = get_current_site(request)
            subject = "email verification"
            message = render_to_string('account/registration/email_verification.html', {
                "user": user,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "domain": current_site.domain,
                "token": user_tokenizer_generate.make_token(user),
                "protocol": "https" if request.is_secure() else "http",
            })
            
            user.email_user(subject=subject, message=message)
            return redirect('email_verification_sent')
    else:
        form = CreateUserForm()
        
    return render(request, 'account/registration/register.html', {"form": form})


def email_verification(request, uidb64, token):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)
    
    if user and user_tokenizer_generate.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('email_verification_success')
    
    return redirect('emailverification_failed')


def email_verification_sent(request):
    if request.method not in ["GET", "HEAD"]:
        return HttpResponseNotAllowed(["GET", "HEAD"])
    return render(request, 'account/registration/email_verification_sent.html')


def email_verification_success(request):
    if request.method not in ["GET", "HEAD"]:
        return HttpResponseNotAllowed(["GET", "HEAD"])
    return render(request, 'account/registration/email_verification_success.html')


def emailverification_failed(request):
    if request.method not in ["GET", "HEAD"]:
        return HttpResponseNotAllowed(["GET", "HEAD"])
    return render(request, 'account/registration/emailverification_failed.html')


def Login_view(request):
    allowed_methods = list(request_method_enum.keys())
    if request.method not in allowed_methods:
        return HttpResponseNotAllowed(allowed_methods)
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('dashboard')
    else:
        form = LoginForm()
        
    return render(request, 'account/login.html', {'form': form})


def logout_view(request):
    if request.method not in ["GET", "HEAD"]:
        return HttpResponseNotAllowed(["GET", "HEAD"])

    for key in list(request.session.keys()):
        if key != 'session-key':
            del request.session[key]
            
    messages.success(request, "you're logged out")
    return redirect('store')


@login_required(login_url="login")
def dashboard_view(request):
    if request.method not in ["GET", "HEAD"]:
        return HttpResponseNotAllowed(["GET", "HEAD"])
    return render(request, 'account/dashboard.html')


@login_required(login_url="login")
def profile_managment(request):
    allowed_methods = list(request_method_enum.keys())
    if request.method not in allowed_methods:
        return HttpResponseNotAllowed(allowed_methods)
    
    if request.method == "POST":
        form = UpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UpdateForm(instance=request.user)
        
    return render(request, 'account/profile_managment.html', {'form': form})


@login_required(login_url="login")
def delete_account(request):
    allowed_methods = list(request_method_enum.keys())
    if request.method not in allowed_methods:
        return HttpResponseNotAllowed(allowed_methods)
    
    if request.method == "POST":
        user = User.objects.get(id=request.user.id)
        user.delete()
        return redirect('store')
        
    return render(request, 'account/delete_account.html')


@login_required(login_url='login')
def manage_shipping(request):
    allowed_methods = list(request_method_enum.keys())
    if request.method not in allowed_methods:
        return HttpResponseNotAllowed(allowed_methods)
    
    try:
        shipping_instance = Shipping_Address.objects.get(user=request.user.pk)
    except Shipping_Address.DoesNotExist:
        shipping_instance = None
        
    request_method = request_method_enum[request.method](request)
    shipping_form = ShippingForm(request_method, instance=shipping_instance)
    
    if request.method == "POST":
        if shipping_form.is_valid():
            shipping_db_row = shipping_form.save(commit=False)
            shipping_db_row.user = request.user
            shipping_db_row.save()
            return redirect('dashboard')
            
    return render(request, 'account/manage_shipping.html', {'form': shipping_form})
