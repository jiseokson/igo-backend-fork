from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

from programs.permissions import IsStudent

from rentals.models import Rental
from rentals.serializers import RentalContractSerializer, RentalListRetrieveSerializer


class RentalListRetrieveViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Rental.objects.filter(is_active=True)
    serializer_class = RentalListRetrieveSerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action == 'subscribe':
            permission_classes = [IsAuthenticated, IsStudent]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=('POST',))
    def subscribe(self, request, *args, **kwargs):
        user = request.user
        rental = self.get_object()
        if user.point >= rental.point:
            data = request.data
            data['borrower'] = user.pk
            data['rental'] = rental.pk
            data['rental_start_at'] = rental.rental_start_at
            data['rental_end_at'] = rental.rental_end_at

            serializer = RentalContractSerializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            user.point -= rental.point
            user.save()
            rental.is_active = False
            rental.save()

            return Response(serializer.data)
        else:
            return Response({'detail': 'Not enough points.'}, status=status.HTTP_400_BAD_REQUEST)
