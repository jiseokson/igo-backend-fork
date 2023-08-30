from django.contrib.auth import get_user_model

from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from profiles.models import CarerProfile, StudentProfile
from profiles.permissions import ProfileRetrievUpdatePermission
from profiles.serializers import CarerProfileSerializer, StudentProfileSerializer


class ProfileRetrieveUpdateView(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = get_user_model().objects.all()
    permission_classes = (IsAuthenticated, ProfileRetrievUpdatePermission)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_student:
            serializer = StudentProfile.objects.get(user=user)
        elif user.is_carer:
            serializer = CarerProfile.objects.get(user=user)
        return Response(data=serializer.data)

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()

        if user.is_student:
            profile = StudentProfile.objects.get(user=user)
            serializer = StudentProfileSerializer(
                profile, data=request.data, partial=True)
        elif user.is_carer:
            profile = CarerProfile.objects.get(user=user)
            serializer = CarerProfileSerializer(
                profile, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)
