from django.shortcuts import render, redirect
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

    form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def LogInView(request):
    if request.user.is_authenticated:
        return redirect('forumapp:channel')

    elif request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            raw_password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=raw_password)

            if user is not None:
                login(request, user)
                return redirect('forumapp:channel')

    form = AuthenticationForm()
    return render(request, 'registration/signup.html', {'form': form})


