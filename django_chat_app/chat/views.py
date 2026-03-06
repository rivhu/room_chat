from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import Room, Message, PrivateMessage
from .forms import SignUpForm, RoomForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Account created.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def home_view(request):
    rooms = Room.objects.all().order_by('-created_at')
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/home.html', {'rooms': rooms, 'users': users})


@login_required
def room_view(request, room_name):
    room = get_object_or_404(Room, name=room_name)
    room_messages = room.messages.select_related('author').order_by('timestamp')[:100]
    room.members.add(request.user)
    return render(request, 'chat/room.html', {
        'room': room,
        'messages': room_messages,
    })


@login_required
def create_room_view(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.created_by = request.user
            room.save()
            room.members.add(request.user)
            messages.success(request, f'Room "{room.name}" created!')
            return redirect('room', room_name=room.name)
    else:
        form = RoomForm()
    return render(request, 'chat/create_room.html', {'form': form})


@login_required
def private_chat_view(request, username):
    other_user = get_object_or_404(User, username=username)
    if other_user == request.user:
        return redirect('home')

    chat_messages = PrivateMessage.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')[:100]

    # Mark messages as read
    PrivateMessage.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/private_chat.html', {
        'other_user': other_user,
        'messages': chat_messages,
        'users': users,
    })


@login_required
def delete_room_view(request, room_name):
    room = get_object_or_404(Room, name=room_name)
    if request.user == room.created_by or request.user.is_superuser:
        room.delete()
        messages.success(request, f'Room "{room_name}" deleted.')
    return redirect('home')
