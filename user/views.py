from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User as User
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from django.http import Http404, HttpResponseForbidden, JsonResponse
from rest_framework.authtoken.models import Token

import user
from .models import Friend_Request, User
from .serializers import UserSerializer
import requests

def index(request):
    return HttpResponse("Olá mundo! Este é o caminho do vazio. Aqui é bem vazio, vá para http://localhost:8000/api/news lá é muito mais cheio")

@api_view(['GET'])
def api_news(request):

    url = "https://gaming-news.p.rapidapi.com/news"

    headers = {
	    "X-RapidAPI-Host": "gaming-news.p.rapidapi.com",
	    "X-RapidAPI-Key": "431b871e74msha3177211b2d7899p1645e3jsnde8a9570000a"
    }

    response = requests.request("GET", url, headers=headers)

    data =  HttpResponse(response.text)

    return data

@api_view(['POST'])
def api_signup(request):
    try:
        if request.method == 'POST':
            username = request.data['username']
            password = request.data['password']
            if username is not None and password is not None:
                if not User.objects.filter(username = username):
                    new_user = User.objects.create_user(username=username, password=password)
                    new_user.save()
                    return Response({"response":"User created successfully!"})
                else:
                    return Response({"response":"Username already exists. Please, try again."})      
    except:
        return HttpResponseForbidden()

@api_view(['POST'])
def api_get_token(request):
    try:
        if request.method == 'POST':
            username = request.data['username']
            password = request.data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                return JsonResponse({"token":token.key})
            else:
                return HttpResponseForbidden()
    except:
        return HttpResponseForbidden()

@permission_classes([IsAuthenticated])
def send_friend_request(request, user_id):
    from_user = request.user
    to_user = User.objects.get(id = user_id)
    friend_request, created = Friend_Request.objects.get_or_create(
        from_user=from_user, to_user = to_user)
    if created:
        return HttpResponse('friend request sent')
    else:
        return HttpResponse('friend request was alredy sent')

# @login_required
@permission_classes([IsAuthenticated])
def accept_friend_request(request, request_id):
    friend_request = Friend_Request.objects.get(id=request_id)
    if friend_request.to_user == request.user:
        friend_request.to_user.friends.add(friend_request.from_user)
        friend_request.delete()
        return HttpResponse('friend request accepted')
    else:
        return HttpResponse('friend request not accepted')

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_user(request):
    try:
        user = User.objects.all()
    except User.DoesNotExist:
        raise Http404()
    if request.method == 'POST':
        new_user_data = request.data
        # user.title = new_note_data['title']
        user.friend = new_user_data['friend']
        user.save()
    
    users = User.objects.filter(user = request.user)
    serialized_user = UserSerializer(users, many = True)
    return Response(serialized_user.data)