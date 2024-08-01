from rest_framework import serializers
from .models import RawData, ProblemData, LastProblemData,LogData, DeviceData, MachineData, ProductionData
from events.serializers import *
from devices.serializers import *
from Userauth.models import UserDetail

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
        fields = ['date', 'time', 'received_data',  'protocol',  'topic_api', 'data_id' ]

class DeviceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceData
        fields = ['date', 'time',  'data', 'device_id', 'protocol', 'topic_api', 'create_date_time', 'update_date_time', 'log_data_id','timestamp' ]

class MachineDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineData
        fields = [  'date', 'time',  'machine_id', 'data', 'device_id', 'create_date_time', 'update_date_time', 'data_id','timestamp']

class ProductionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionData
        fields = ['date', 'time','shift_number', 'shift_name',  'target_production', 'machine_id', 'machine_name', 'production_count','production_date', 'data_id']
        


class MachineProductionSerializer(serializers.ModelSerializer):
    production_count = serializers.SerializerMethodField()
    target_production = serializers.SerializerMethodField()

    class Meta:
        model = MachineDetails
        fields = ['machine_name', 'machine_id', 'production_count', 'target_production']

    def get_production_count(self, obj):
        last_production = ProductionData.objects.filter(machine_id=obj).order_by('-date', '-time').first()
        return last_production.production_count if last_production else 0

    def get_target_production(self, obj):
        last_production = ProductionData.objects.filter(machine_id=obj).order_by('-date', '-time').first()
        return last_production.target_production if last_production else 0

class MachineGroupSerializer(serializers.ModelSerializer):
    machines = serializers.SerializerMethodField()
    number_of_machines = serializers.SerializerMethodField()

    class Meta:
        model = MachineGroup
        fields = ['group_name', 'number_of_machines', 'machines']

    def get_machines(self, obj):
        machines = obj.machine_list.all()
        return MachineProductionSerializer(machines, many=True).data

    def get_number_of_machines(self, obj):
        return obj.machine_list.count()

class DashboardSerializer(serializers.Serializer):
    number_of_groups = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    def get_number_of_groups(self, obj):
        return MachineGroup.objects.count()

    def get_groups(self, obj):
        groups = MachineGroup.objects.all()
        return MachineGroupSerializer(groups, many=True).data
    
    
class HourlyDataSerializer(serializers.Serializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    production_count = serializers.IntegerField()
    target_production = serializers.IntegerField()

class ShiftReportSerializer(serializers.Serializer):
    date = serializers.CharField()
    shift_id = serializers.IntegerField()
    machine_id = serializers.CharField()

class SummaryReportSerializer(serializers.Serializer):
    date = serializers.DateField()
    machine_id = serializers.CharField(max_length=255)

class ShiftwiseReportSerializer(serializers.Serializer):
    date = serializers.DateField()
    machine_id = serializers.CharField()

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username', 'is_active')

class EmployeeDetailSerializer(serializers.ModelSerializer):
    # Include User fields directly in the EmployeeDetailSerializer
    id = serializers.IntegerField(source='extUser.id', read_only=True)
    EmployeeName = serializers.CharField(source='extUser.username')
    Status = serializers.BooleanField(source='extUser.is_active')
    
    class Meta:
        model = UserDetail
        fields = ('id', 'EmployeeName', 'employee_id', 'mobile_no', 'registered_status', 'Status')
    
    def create(self, validated_data):
        ext_user_data = validated_data.pop('extUser')
        user = User.objects.create(**ext_user_data)
        validated_data['extUser'] = user
        user_detail = UserDetail.objects.create(**validated_data)
        return user_detail
    
    def update(self, instance, validated_data):
        ext_user_data = validated_data.pop('extUser')
        user = instance.extUser
        
        instance.employee_id = validated_data.get('employee_id', instance.employee_id)
        instance.mobile_no = validated_data.get('mobile_no', instance.mobile_no)
        instance.registered_status = validated_data.get('registered_status', instance.registered_status)
        instance.save()
        
        user.username = ext_user_data.get('username', user.username)
        user.is_active = ext_user_data.get('is_active', user.is_active)
        user.save()
        
        return instance


class ShiftDataSerializer(serializers.Serializer):
    date = serializers.DateField()
    time = serializers.TimeField()
    shift_name = serializers.CharField()
    shift_start_time = serializers.TimeField()
    shift_end_time = serializers.TimeField()
    production_count = serializers.IntegerField()
    target_production = serializers.IntegerField()
    total = serializers.IntegerField()

class MachineReportSerializer(serializers.Serializer):
    machine_id = serializers.CharField()
    shifts = ShiftDataSerializer(many=True)

class TableReportSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    machines = MachineReportSerializer(many=True)

class MachineSerializer(serializers.Serializer):
    machine_id = serializers.CharField()
    machine_name = serializers.CharField()
    shifts = ShiftDataSerializer(many=True)
    

class GroupDataSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    group_name = serializers.CharField()
    machines = MachineSerializer(many=True)

class ProductionTableSerializer(serializers.Serializer):
    date = serializers.DateField()
    groups = GroupDataSerializer(many=True)
    
