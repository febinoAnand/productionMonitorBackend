from rest_framework import serializers
from .models import RawData, ProblemData, LastProblemData,LogData, DeviceData, MachineData, ProductionData
from events.serializers import *
from devices.serializers import *

class RawSerializer(serializers.ModelSerializer):
    # deviceToken = serializers.CharField()
    class Meta:
        model = RawData
        fields = ('date','time','eventID','machineID','eventGroupID')

class RawSerializerWithDateTime(serializers.ModelSerializer):
    # deviceToken = serializers.CharField()
    class Meta:
        model = RawData
        fields = ('datetime','date','time','eventID','machineID','eventGroupID')

    # def to_representation(self, instance):
    #     data = super(RawSerializer, self).to_representation(instance)
    #     data.fields.datetime = data.fields.datetime.strftime("%Y-%m-%d %H:%M:%S")
    #     return data

class ProblemDataSerializer(serializers.ModelSerializer):
    eventGroupID = serializers.SerializerMethodField()
    event = EventSerializer(source='eventID',read_only=True)
    machine = MachineSerializer(source='machineID',read_only=True)

    def get_eventGroupID(self,obj):
        return obj.eventGroupID.groupID

    class Meta:
        model = ProblemData
        fields = ('date','time','eventGroupID','event','machine','issueTime','acknowledgeTime','endTime','dateTimeNow')

class LastProblemDataSerializer(serializers.ModelSerializer):
    event = EventSerializer(source="eventID",read_only=True)
    machine = MachineSerializer(source="machineID",read_only=True)
    eventGroupID = serializers.SerializerMethodField()

    def get_eventGroupID(self,obj):
        return obj.eventGroupID.groupID
    class Meta:
        model = LastProblemData
        fields = ('date','time','eventGroupID','event','machine','issueTime','acknowledgeTime','endTime','dateTimeNow')

# class LiveDataSerializer(serializers.Serializer):
#     # machines = MachineSerializer(source="machineID",read_only=True,many=True)
#     machines = serializers.SerializerMethodField()
#     currentEvent = serializers.SerializerMethodField()
#     class Meta:
#         fields = ['machines','currentEvent']
#
#     def get_machiens(self,obj):
#         return MachineSerializer(obj.machine.all(),many=True).data
#
#     def get_currentEvent(self,obj):
#         return EventSerializer(obj.event.all(),many=True).data

# class rawGetMethodeSerializer(serializers.Serializer):
#     dateTime = serializers.DateTimeField()
#     data = serializers.CharField()

class LogDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogData
        fields = ['date', 'time', 'received_data',  'protocol',  'topic_api', 'unique_id' ]

class DeviceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceData
        fields = ['date', 'time',  'data', 'device_id', 'protocol', 'topic_api', 'create_date_time', 'update_date_time', 'log_data_id' ]

class MachineDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineData
        fields = [  'date', 'time',  'machine_id', 'data', 'device_id', 'create_date_time', 'update_date_time', 'data_id']

class ProductionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionData
        fields = ['date', 'time', 'shift_id', 'shift_name', 'shift_start_time', 'shift_end_time', 'target_production', 'machine_id', 'machine_name', 'production_count', 'data_id']