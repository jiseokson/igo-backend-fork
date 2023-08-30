from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from accounts.serializer import UserSerializer
from profiles.models import CarerProfile, StudentProfile
from profiles.serializers import CarerProfileSerializer, StudentProfileSerializer
from programs.models import Program
from programs.serializers import ProgramSerializer
from rentals.models import RentalContract
from rentals.serializers import RentalContractSerializer

from rest_framework.decorators import action
from programs.models import Program
from programs.serializers import ProgramSerializer


class AccountCreateRetrieveViewSet(CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = get_user_model().objects.all()
    permission_classes = (IsAuthenticated,)

    def user_info(self, user):
        data = UserSerializer(user).data

        # 해당 유저의 프로필 정보 조회
        # 존재하지 않는다면 공백
        profile = None
        try:
            if user.is_student:
                profile = StudentProfileSerializer(
                    StudentProfile.objects.get(user=user)).data
            elif user.is_carer:
                profile = CarerProfileSerializer(
                    CarerProfile.objects.get(user=user)).data
        finally:
            data['profile'] = profile or {}

        return Response(data=data)

    def list(self, request, *args, **kwargs):
        return self.user_info(request.user)

    def retrieve(self, request, *args, **kwargs):
        return self.user_info(self.get_object())

    def create(self, request):
        user = request.user
        data = request.data
        query_params = request.query_params

        if user.is_student or user.is_carer:
            return Response({'detail': 'This user is already registered.'}, status=status.HTTP_400_BAD_REQUEST)

        if query_params.get('type') == 'student':
            profile_seriailzer = StudentProfileSerializer(data=data)
        elif query_params.get('type') == 'carer':
            profile_seriailzer = CarerProfileSerializer(data=data)
        else:
            return Response({"detail": "User type not passed."}, status=status.HTTP_400_BAD_REQUEST)

        if not profile_seriailzer.is_valid():
            return Response(profile_seriailzer.errors, status=status.HTTP_400_BAD_REQUEST)
        profile_seriailzer.save(user=user)
        user.set_type(query_params.get('type'))
        user.set_regist()

        data = UserSerializer(user).data
        data['profile'] = profile_seriailzer.data
        return Response(data=data)

    @action(detail=True, methods=('GET',))
    def program(self, request, *args, **kwargs):
        user = self.get_object()

        if user.is_student:
            return Response({'detail': 'This user is not a carer.'}, status=status.HTTP_400_BAD_REQUEST)

        programs = Program.objects.filter(author=user)
        serializer = ProgramSerializer(programs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def rental(self, request, *args, **kwargs):
        user = self.get_object()
        rental_contracts = RentalContract.objects.filter(borrower=user)
        serializer = RentalContractSerializer(rental_contracts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=('GET',))
    def subscribe(self, request, *args, **kwargs):
        user = self.get_object()

        if user.is_student:
            programs = Program.objects.filter(subscriber=user)
            SpecificProgram = ProgramSerializer(programs, many=True)
            return Response(SpecificProgram.data)
        else:
            return Response({"detail": "사용자 유형을 확인해주십시오."},
                            status=status.HTTP_400_BAD_REQUEST)
