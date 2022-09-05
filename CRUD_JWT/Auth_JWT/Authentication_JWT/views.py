import email
from re import S
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from Authentication_JWT.serializers import (UserRegistrationSerializer,
                                            UserLoginSerializer,
                                            UserProfileSerializer,
                                            UserChangePasswordSerializer,
                                            SendResetPasswordSerializer,
                                            UserPasswordResetSerializer)
from django.contrib.auth import authenticate
from Authentication_JWT.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

# Generate JWT token manually for authentication
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    
    
# Create your views here.
# User Registration View
class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'token':token, 'msg': 'Registration Successful!'},
                        status=status.HTTP_201_CREATED)
    

# User Login View
class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token':token, 'msg': 'Login Successful!'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'non_field_errors':['Email or Password is not Valid!']}},
                            status=status.HTTP_404_NOT_FOUND)
                

# User Profile View                
class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# User Change Password View
class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data,
                                                  context={'user':request.user})
        
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Changed Successfully!!'}, status=status.HTTP_200_OK)


# User Reset Password View
class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = SendResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset Link send. Please Check your email!!'}, status=status.HTTP_200_OK)
    
    
class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data,
                                                 context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': "Password Reset Successful!"}, status=status.HTTP_200_OK)