from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from django.views.decorators.http import require_POST

from common.decorators import ajax_required
from .forms import LoginForm, RegisterNewUser, \
     UserEditForm, ProfileEditForm
# Create your views here.
from .models import Contact


def user_login(request):

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password']
                    )
            
            if user is not None:
                if user.is_active:
                    # attach user to a session
                    login(request, user)
                    return HttpResponse("Authenticated successfully")
                else:
                    return HttpResponse("Disabled account, Contact Admin")
            else:
                return HttpResponse("Invalid credentials")
        
    else:
        form = LoginForm()
        return render(request, 'account/login.html', {'form':form})


#user redirect after login
@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html',{'section':'dashboard'})



def register(request):
    
    if request.method == 'POST':
        user_form = RegisterNewUser(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False) # do not save plain text passwords
            new_user.set_password(user_form.cleaned_data['password'])
            # creating a new user will fire a post save
            # signal in signals.py file to create a new profile
            new_user.save()

            return render(request, 'account/register_done.html', {'new_user':new_user})
        
    else:
            user_form = RegisterNewUser()
    return render(request, 'account/register.html', {'user_form':user_form})
    


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(
                                        instance = request.user.profile,
                                        data= request.POST,
                                        files = request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            # messages.info(request, 'Profile updated successfully')
            # messages.warning(request, 'Profile updated successfully')
            # messages.debug(request, 'Profile updated successfully')
            # messages.error(request, 'Profile updated successfully')
        else:
            messages.error(request, f"Error Updating your profile data,\n {user_form.errors},\n{profile_form.errors}")
        
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance = request.user.profile)
    context = {
        'user_form':user_form,
        'profile_form':profile_form,
    }
    return render(request, 'account/edit.html', context)


@login_required
def users_list(request):
    users = get_user_model().objects.filter(is_active=True)

    return render(request, 'account/user/list.html',
                    {'section':'people', 'users':users})           



@login_required
def user_detail(request, username):
    user = get_object_or_404(get_user_model(), username = username, is_active=True)

    return render(request,
                    'account/user/detail.html',
                    {
                        'section':'people',
                        'user':user,
                    })
                    

@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = get_user_model().objects.get(id = user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from = request.user, user_to = user)
                # create_action(request.user, 'is')
            else:
                Contact.objects.filter(user_from = request.user, user_to = user).delete()
            
            return JsonResponse({'status':'ok'})
        except get_user_model().DoesNotExist:
            return JsonResponse({'status':'error'})
    return JsonResponse({'status': 'error'})
        
