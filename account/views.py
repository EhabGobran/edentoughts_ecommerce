from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm, UpdateForm
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods, require_safe, require_GET
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
from asgiref.sync import sync_to_async

# Create your views here.

@require_http_methods(list(request_method_enum.keys()))
async def register(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        # Inline sync execution for form validation
        if await sync_to_async(form.is_valid)():
            user = await sync_to_async(form.save)(commit=False)
            user.is_active = False
            await user.asave()
            
            current_site = await sync_to_async(get_current_site)(request)
            subject = "email verification"
            message = render_to_string('account/registration/email_verification.html', {
                "user": user,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "domain": current_site.domain,
                "token": await sync_to_async(user_tokenizer_generate.make_token)(user),
                "protocol": "https" if request.is_secure() else "http",
            })
            
            await sync_to_async(user.email_user)(subject=subject, message=message)
            return redirect('email_verification_sent')
    else:
        form = CreateUserForm()
        
    return render(request, 'account/registration/register.html', {"form": form})


@require_GET
async def email_verification(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = await User.objects.aget(pk=uid)
        
        if user and await sync_to_async(user_tokenizer_generate.check_token)(user, token):
            user.is_active = True
            await user.asave()
            return redirect('email_verification_success')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass
        
    return redirect('emailverification_failed')


@require_safe
def email_verification_sent(request):
    return render(request, 'account/registration/email_verification_sent.html')


@require_safe
def email_verification_success(request):
    return render(request, 'account/registration/email_verification_success.html')


@require_safe
def emailverification_failed(request):
    return render(request, 'account/registration/emailverification_failed.html')


@require_http_methods(list(request_method_enum.keys()))
def Login_view(request):
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


@require_safe
def logout_view(request):
    for key in list(request.session.keys()):
        if key != 'session-key':
            del request.session[key]
            
    messages.success(request, "you're logged out")
    return redirect('store')


@login_required(login_url="login")
def dashboard_view(request):
    return render(request, 'account/dashboard.html')


@login_required(login_url="login")
async def profile_managment(request):
    if request.method == "POST":
        form = UpdateForm(request.POST, instance=request.user)
        # Fix: Wrapped form validation inside sync_to_async
        if await sync_to_async(form.is_valid)():
            # Fix: ModelForms do not have .asave(). Wrap standard .save() instead.
            await sync_to_async(form.save)()
            return redirect('dashboard')
    else:
        form = UpdateForm(instance=request.user)
        
    return render(request, 'account/profile_managment.html', {'form': form})


@login_required(login_url="login")
async def delete_account(request):
    if request.method == "POST":
        user = await User.objects.aget(id=request.user.id)
        await user.adelete()
        return redirect('store')
        
    return render(request, 'account/delete_account.html')


@login_required(login_url='login')
@require_http_methods(list(request_method_enum.keys()))
async def manage_shipping(request):
    try:
        shipping_instance = await Shipping_Address.objects.aget(user=request.user.pk)
    except Shipping_Address.DoesNotExist:
        shipping_instance = None
        
    request_method = request_method_enum[request.method](request)
    shipping_form = ShippingForm(request_method, instance=shipping_instance)
    
    if request.method == "POST":
        # Fix: Forms are sync; execute validation via inline sync_to_async wrapper
        if await sync_to_async(shipping_form.is_valid)():
            shipping_db_row = await sync_to_async(shipping_form.save)(commit=False)
            shipping_db_row.user = request.user
            await shipping_db_row.asave()
            return redirect('dashboard')
            
    return render(request, 'account/manage_shipping.html', {'form': shipping_form})
