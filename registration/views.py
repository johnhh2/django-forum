from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def SignUpView(request):
    if request.user.is_authenticated:
        return redirect('forumapp:channel')

    elif request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            if password1 == password2:
                user = authenticate(request, username=username, password=password1)

                login(request, user)
                return redirect('forumapp:channel')
            else: # passwords dont match
                messages.error(request, 'Passwords do not match')

        else: # tell user why form isnt valid
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')

            if form.fields['password1'] != form.fields['password2']:
                messages.error(request, 'Passwords do not match')
            else:
                messages.error(request, 'Invalid username or password')

    form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def LogInView(request):
    if request.user.is_authenticated:
        return redirect('forumapp:channel')

    elif request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=raw_password)
            if user is not None:
                login(request, user)

                return redirect('forumapp:channel')
        else:
            messages.error(request, 'Invalid username or password')


    form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
