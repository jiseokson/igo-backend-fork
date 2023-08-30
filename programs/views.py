from django.utils import timezone
from django.db.models import Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from profiles.models import CarerProfile

from programs.models import Program
from programs.serializers import ProgramSerializer
from .permissions import IsCarer, IsProgramAuthor, IsStudent


class ProgramViewSet(ModelViewSet):
    serializer_class = ProgramSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        address=CarerProfile.objects.get(user=self.request.user).address)

    def get_queryset(self):
        queryset = Program.objects.order_by('-created_at')
        address_query = self.request.query_params.get('address', None)
        activity_query = self.request.query_params.get('activity', None)
        if address_query:
            queryset = queryset.filter(
                Q(address__address__icontains=address_query))
        if activity_query:
            queryset = queryset.filter(activity_category=activity_query)
        return queryset

    def get_permissions(self):
        if self.action == 'subscribe':
            permission_classes = [IsAuthenticated, IsStudent]
        elif self.action == 'authenticate':
            permission_classes = [IsAuthenticated, IsCarer, IsProgramAuthor]
        elif self.action in ['create']:
            permission_classes = [IsAuthenticated, IsCarer]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsCarer, IsProgramAuthor]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=('POST', 'DELETE'))
    def subscribe(self, request, *args, **kwargs):
        program = self.get_object()

        if request.method == 'POST':
            if not program.is_registing:
                return Response({"detail": "현재는 프로그램 모집 기간이 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)
            program.subscriber.add(request.user)
            program.save()
            return Response(self.serializer_class(program).data)
        elif request.method == 'DELETE':
            if not program.regist_start_at <= timezone.now().date() <= program.regist_end_at:
                return Response({"detail": "현재는 프로그램 모집 기간이 아닙니다."},
                                status=status.HTTP_400_BAD_REQUEST)
            program.subscriber.remove(request.user)
            program.save()
            return Response(self.serializer_class(program).data)

    @action(detail=True, methods=('POST',))
    def authenticate(self, request, *args, **kwargs):
        program = self.get_object()
        if program.activity_status != 'done' or program.is_rewarded == True:
            return Response({'detail': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
        for user in program.subscriber.all():
            user.point += program.reward
            user.save()
        program.is_rewarded = True
        program.save()
        return Response(ProgramSerializer(program).data)
