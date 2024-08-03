from rest_framework import serializers
from .models import *



class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceDetails
        fields = ('id','device_name','hardware_version','software_version','device_token','protocol','pub_topic','sub_topic','api_path')


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineDetails
        fields = ['id', 'machine_id', 'machine_name', 'manufacture', 'line', 'device','production_per_hour']


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

class MachineDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineDetails
        fields = ['id','machine_id', 'machine_name']

class MachineGroupSerializer(serializers.ModelSerializer):
    machine_list = serializers.PrimaryKeyRelatedField(
        queryset=MachineDetails.objects.all(), 
        many=True, 
        write_only=True
    )
    machines = MachineDetailsSerializer(source='machine_list', many=True, read_only=True)
    group_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = MachineGroup
        fields = ['group_id', 'group_name', 'machine_list', 'machines']
    
    def validate_machine_list(self, value):
        for machine in value:
            if MachineGroup.objects.filter(machine_list=machine).exists():
                raise serializers.ValidationError(f'The machine {machine.machine_name} is already assigned to another group.')
        return value
    
    def create(self, validated_data):
        machine_ids = validated_data.pop('machine_list')
        machine_group = MachineGroup.objects.create(**validated_data)
        machine_group.machine_list.set(machine_ids)
        return machine_group

    def update(self, instance, validated_data):
        machine_ids = validated_data.pop('machine_list')
        instance.group_name = validated_data.get('group_name', instance.group_name)
        instance.save()
        instance.machine_list.set(machine_ids)
        return instance

class ShiftTimingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftTiming
        fields = ['shift_number', 'start_time', 'end_time', 'shift_name', 'create_date_time', 'update_date_time']
