from rest_framework import serializers
from .models import *



class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceDetails
        fields = ('_id','device_name','hardware_version','software_version','device_token','protocol','pub_topic','sub_topic','api_path')


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineDetails
        fields = ['_id', 'machine_id', 'machine_name', 'manufacture', 'line', 'device']


class MachineWithoutDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineDetails
        fields = ('id','machineID','name','manufacture','model','line')
    # def create(self, validated_data):
    #     print("trying to create")
    #     print(validated_data)
    #     return {"message":"ok"}
    #
    #
    # def update(self, instance, validated_data):
    #     print ("tryin to update")



class RFIDSerializer(serializers.ModelSerializer):
    rfidUser = serializers.SerializerMethodField();

    def get_rfidUser(self,obj):
        return obj.rfidUser.username

    class Meta:
        model = RFID
        fields = ('rfid','rfidUser')

class UnRegisteredSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnRegisteredDevice
        fields = ('sessionID','deviceID','devicePassword','model','hardwareVersion','softwareVersion','OTP')

class UnRegisteredGetMethodSerializer(serializers.Serializer):
    deviceID = serializers.CharField()
    model = serializers.CharField()
    hardwareVersion = serializers.CharField()
    softwareVersion = serializers.CharField()
    devicePassword = serializers.CharField()
    class Meta:
        fields = ('deviceID','devicePassword','model','hardwareVersion','softwareVersion')


class VerifyDeviceSerializer(serializers.Serializer):
    sessionID = serializers.UUIDField()
    OTP = serializers.CharField()
    # class Meta:
    #     fields = ('OTP','sessionID')

class GetTokenSerializer(serializers.Serializer):
    deviceID = serializers.CharField()
    devicePassword = serializers.CharField()

class MachineGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineGroup
        fields = ['_id','machine_list', 'group_name']

class ShiftTimingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftTimings
        fields = ['_id', 'start_time', 'end_time', 'shift_name', 'create_date_time', 'update_date_time']
