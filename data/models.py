import datetime as datetime
from django.utils import timezone,dateformat
import datetime
from django.db import models
from events.models import Event,EventGroup
from devices.models import MachineDetails,RFID, DeviceDetails,ShiftTimings
from univaProductionMonitor import settings
from datetime import timedelta

# Create your models here.

class RawData(models.Model):
    # {"date": "2023-08-26", "time": "08:26:17", "eventID": "EV123-001", "deviceID": "DEV123","eventGroupID":"GEV123"} Data format
    # datetime = models.DateTimeField(editable=False,default=dateformat.format(timezone.now(), 'Y-m-d H:i:s'))
    datetime = models.DateTimeField(editable=False,default=datetime.datetime.now)
    data = models.TextField(blank=False)
    date = models.DateField(blank=True,null=True)
    time = models.TimeField(blank=True,null=True)
    eventID = models.ForeignKey(Event,on_delete=models.CASCADE,blank=True,null=True)
    deviceID = models.ForeignKey(DeviceDetails,on_delete=models.CASCADE,blank=True,null=True)
    machineID = models.ForeignKey(MachineDetails,on_delete=models.CASCADE,blank=False,null=True)
    eventGroupID = models.ForeignKey(EventGroup,on_delete=models.CASCADE,blank=True,null=True)
    def __str__(self):
        return str(self.id)

    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         self.datetime = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    #
    #     return super(RawData, self).save(*args, **kwargs)

class ProblemData(models.Model):
    date = models.DateField()
    time = models.TimeField()
    eventID = models.ForeignKey(Event,blank=False,on_delete=models.CASCADE)
    eventGroupID = models.ForeignKey(EventGroup,blank=False,on_delete=models.CASCADE)
    machineID = models.ForeignKey(MachineDetails, blank=False, on_delete=models.CASCADE)
    deviceID = models.ForeignKey(DeviceDetails, blank=False, on_delete=models.CASCADE, null=True)
    issueTime = models.DateTimeField()
    acknowledgeTime = models.DateTimeField(blank=True,null=True)
    rfidTime = models.ForeignKey(RFID,on_delete=models.CASCADE,blank=True,null=True)
    endTime = models.DateTimeField(blank=True,null=True)
    dateTimeNow = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.eventGroupID)


class LastProblemData(models.Model):
    # UUID = models.UUIDField()
    date = models.DateField()
    time = models.TimeField()
    eventID = models.ForeignKey(Event,blank=False,on_delete=models.CASCADE)
    eventGroupID = models.ForeignKey(EventGroup,blank=False,on_delete=models.CASCADE)
    deviceID = models.ForeignKey(DeviceDetails, blank=False, on_delete=models.CASCADE, null=True)
    machineID = models.ForeignKey(MachineDetails, blank=False, on_delete=models.CASCADE)
    issueTime = models.DateTimeField(blank=True,null=True)
    acknowledgeTime = models.DateTimeField(blank=True,null=True)
    rfidTime = models.ForeignKey(RFID,on_delete=models.CASCADE,blank=True,null=True)
    endTime = models.DateTimeField(blank=True,null=True)
    dateTimeNow = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.eventGroupID)



class LogData(models.Model):
    date = models.DateField(blank=False)
    time = models.TimeField(blank=False)
    received_data = models.CharField(max_length=2000, null=True, blank=True)
    protocol = models.CharField(max_length=15, null=True, blank=True)
    topic_api = models.CharField(max_length=100, null=True, blank=True)
    data_id = models.CharField(max_length=50, unique=False,null=True, blank=True)
    response = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.date:
            cutoff_date = self.date - timedelta(days=settings.LOG_DATA_RETENTION_DAYS)
            LogData.objects.filter(date__lt=cutoff_date).delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.data_id)
    
    # def save(self, *args, **kwargs):
    #     self.delete_old_logs()
    #     super().save(*args, **kwargs)

    # @classmethod
    # def delete_old_logs(cls):
    #     retention_days = settings.LOG_DATA_RETENTION_DAYS
    #     cutoff_date = timezone.now().date() - timedelta(days=retention_days)
    #     cls.objects.filter(date__lt=cutoff_date).delete()
    

class DeviceData(models.Model):
    date = models.DateField(blank=False)
    time = models.TimeField(blank=False)
    data = models.JSONField(blank=False)
    device_id = models.ForeignKey(DeviceDetails, on_delete=models.CASCADE)
    protocol = models.CharField(max_length=10, null=True, blank=True)
    topic_api = models.CharField(max_length=100, null=True, blank=True)
    create_date_time = models.DateTimeField(auto_now_add=True)
    update_date_time = models.DateTimeField(auto_now=True)
    timestamp=models.CharField(max_length=50, unique=False, blank=False,null=True)
    log_data_id = models.ForeignKey(LogData, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.device_id.device_name)
    
class MachineData(models.Model):
    date = models.DateField(blank=False)
    time = models.TimeField(blank=False)
    machine_id = models.ForeignKey(MachineDetails, on_delete=models.CASCADE)
    data = models.JSONField(blank=False)
    device_id = models.ForeignKey(DeviceDetails, on_delete=models.CASCADE)
    create_date_time = models.DateTimeField(auto_now_add=True)
    update_date_time = models.DateTimeField(auto_now=True)
    timestamp=models.CharField(max_length=50, unique=False, blank=False,null=True)
    log_data_id = models.ForeignKey(LogData, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.machine_id.machine_name)

class ProductionData(models.Model):
    date = models.DateField(blank=False)
    time = models.TimeField(blank=False)
    shift_number = models.IntegerField(blank=False,null=True)
    shift_name = models.CharField(max_length=45, blank=True, null=True)
    target_production = models.IntegerField(blank=False)
    machine_id = models.CharField(max_length=45, blank=False)  
    machine_name = models.CharField(max_length=45, blank=False)
    production_count = models.IntegerField(blank=False)
    production_date=models.DateField(blank=False,null=True)
    log_data_id = models.IntegerField(blank=False)
    timestamp=models.CharField(max_length=50, unique=False, blank=False,null=True)  

    def __str__(self):
        return str(self.shift_number)
    
    class Meta:
        indexes = [
            models.Index(fields=['production_date']),
            models.Index(fields=['machine_id']),
        ]
    


class DashbaordData(models.Model):
    date = models.DateField(auto_now=True)
    time = models.TimeField(auto_now=True)
    dashbaordData = models.JSONField()

class ProductionUpdateData(models.Model):
    date = models.DateField()
    time = models.TimeField(auto_now=True)
    production_data = models.JSONField()

    def __str__(self):
        return f"ProductionUpdateData at {self.date}"