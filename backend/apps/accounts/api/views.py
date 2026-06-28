from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.api.serializers import (
    LoginSerializer,
    LogoutSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    RegistrationSerializer,
    UserProfileSerializer,
    VerifyEmailSerializer,
)
from apps.accounts.services import auth_service


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = auth_service.create_jwt_pair(user)
        return Response({"user": UserProfileSerializer(user).data, **tokens}, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = auth_service.login_user(
            email=serializer.validated_data["email"],
            **{"password": serializer.validated_data["password"]},
            request=request,
        )
        return Response(
            {
                "user": UserProfileSerializer(data["user"]).data,
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
            }
        )


class LogoutAPIView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class VerifyEmailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = auth_service.verify_email(serializer.validated_data["token"])
        return Response({"user": UserProfileSerializer(user).data})


class PasswordResetRequestAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth_service.request_password_reset(serializer.validated_data["email"])
        return Response({"detail": "If this email exists, a reset link has been sent."})


class PasswordResetAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth_service.reset_password(
            serializer.validated_data["token"],
            serializer.validated_data["new_password"],
        )
        return Response({"detail": "Password reset successful."})


class PasswordChangeAPIView(APIView):
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth_service.change_password(
            request.user,
            serializer.validated_data["old_password"],
            serializer.validated_data["new_password"],
        )
        return Response({"detail": "Password changed successfully."})


class MeAPIView(APIView):
    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = auth_service.update_profile(request.user, **serializer.validated_data)
        return Response(UserProfileSerializer(user).data)


class AuthTokenRefreshAPIView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
