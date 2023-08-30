from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from profiles.models import Address, CarerProfile, StudentProfile


class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        exclude = ['id']


class StudentProfileSerializer(ModelSerializer):
    user = serializers.ReadOnlyField(source='user.pk')
    address = AddressSerializer(many=False, read_only=False)

    class Meta:
        model = StudentProfile
        fields = '__all__'

    def create(self, validate_data):
        address = validate_data.pop('address')
        address_inst = Address.objects.create(**address)
        profile_inst = StudentProfile.objects.create(
            **validate_data, address=address_inst)
        return profile_inst

    def update(self, obj, validated_data):
        address = obj.address
        address_data = validated_data.pop('address', None)
        if address_data:
            for attr, value in address_data.items():
                setattr(address, attr, value)
            address.save()
        for attr, value in validated_data.items():
            setattr(obj, attr, value)
        obj.save()
        return obj


class CarerProfileSerializer(ModelSerializer):
    user = serializers.ReadOnlyField(source='user.pk')
    address = AddressSerializer(many=False, read_only=False)

    class Meta:
        model = CarerProfile
        fields = '__all__'

    def create(self, validate_data):
        address = validate_data.pop('address')
        address_inst = Address.objects.create(**address)
        profile_inst = CarerProfile.objects.create(
            **validate_data, address=address_inst)
        return profile_inst

    def update(self, obj, validated_data):
        address = obj.address
        address_data = validated_data.pop('address', None)
        if address_data:
            for attr, value in address_data.items():
                setattr(address, attr, value)
            address.save()
        for attr, value in validated_data.items():
            setattr(obj, attr, value)
        obj.save()
        return obj
