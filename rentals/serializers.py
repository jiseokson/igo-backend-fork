from django.utils import timezone

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from profiles.models import Address
from profiles.serializers import AddressSerializer

from rentals.models import Rental, RentalContract


class RentalListRetrieveSerializer(ModelSerializer):
    class Meta():
        model = Rental
        fields = '__all__'


class RentalContractSerializer(ModelSerializer):
    status = serializers.ReadOnlyField()
    address = AddressSerializer(many=False, read_only=False)

    class Meta():
        model = RentalContract
        fields = '__all__'

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address_inst = Address.objects.create(**address_data)
        rental_contract_inst = RentalContract.objects.create(
            **validated_data, address=address_inst)
        return rental_contract_inst
