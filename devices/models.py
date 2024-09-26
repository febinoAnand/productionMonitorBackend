import uuid

import binascii
import os

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


# Create your models here.

class DeviceDetails(models.Model):
    PROTOCOL_CHOICES = [
        ('mqtt', 'MQTT'),
        ('http', 'HTTP')
    ]

    device_name = models.CharField(max_length=45, blank=False)
    device_token = models.CharField(max_length=100, blank=False, unique=True)
    hardware_version = models.CharField(max_length=10, null=True, blank=True)
    software_version = models.CharField(max_length=10, null=True, blank=True)
    create_date_time = models.DateTimeField(auto_now_add=True)
    update_date_time = models.DateTimeField(auto_now=True)
    protocol = models.CharField(max_length=10, blank=False, choices=PROTOCOL_CHOICES)
    pub_topic = models.CharField(max_length=100, null=True, blank=True)
    sub_topic = models.CharField(max_length=100, null=True, blank=True)
    api_path = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.device_name

    def clean(self):
      
        if self.protocol == 'mqtt':
            if not self.pub_topic or not self.sub_topic:
                raise ValidationError('pub_topic and sub_topic are required for MQTT protocol.')
        elif self.protocol == 'http':
            if not self.api_path:
                raise ValidationError('api_path is required for HTTP protocol.')

    def save(self, *args, **kwargs):
        self.clean()
        super(DeviceDetails, self).save(*args, **kwargs)
    

class MachineDetails(models.Model):
    machine_name = models.CharField(max_length=45, blank=False, default="none")
    machine_id = models.CharField(max_length=15, unique=True, blank=False)
    line = models.CharField(max_length=30, null=True, blank=True)
    manufacture = models.CharField(max_length=45, null=True, blank=True)
    year = models.CharField(max_length=30, null=True, blank=True)
    device = models.ForeignKey(DeviceDetails, on_delete=models.CASCADE, null=True, blank=True)
    production_per_hour = models.IntegerField(blank=False, default=0)
    create_date_time = models.DateTimeField(auto_now_add=True)
    update_date_time = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

    def __str__(self):
        return self.machine_id
    

class MachineGroup(models.Model):
    machine_list = models.ManyToManyField(MachineDetails)
    group_name = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.group_name

    def clean(self):
        if self.pk:  
            for machine in self.machine_list.all():
                if MachineGroup.objects.filter(machine_list=machine).exclude(id=self.id).exists():
                    raise ValidationError(f'The machine {machine.machine_name} is already assigned to another group.')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  
        self.clean()  

class ShiftTimings(models.Model):
    _id=models.AutoField(primary_key=True, default=1)
    shift_number = models.IntegerField(blank=False, null=False ,default=1)  # Required field
    start_time = models.TimeField(blank=True, null=True)  # Optional field
    end_time = models.TimeField(blank=True, null=True)  # Optional field
    shift_name = models.CharField(max_length=45, blank=True, null=True)  # Optional field
    create_date_time = models.DateTimeField(auto_now_add=True)
    update_date_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.shift_number)  # Convert to string

class ShiftTiming(models.Model):
    # _id=models.AutoField(primary_key=True, default=1)
    shift_number = models.IntegerField(blank=False, null=False ,default=1)  # Required field
    start_time = models.TimeField(blank=True, null=True)  # Optional field
    end_time = models.TimeField(blank=True, null=True)  # Optional field
    shift_name = models.CharField(max_length=45, blank=True, null=True)  # Optional field
    create_date_time = models.DateTimeField(auto_now_add=True)
    update_date_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.shift_number)  # Convert to string

    # def clean(self):
    #     if self.start_time and self.end_time:
    #         if self.start_time >= self.end_time:
    #             raise ValidationError('Start time must be before end time.')

    # def save(self, *args, **kwargs):
    #     self.clean()
    #     super(ShiftTimings, self).save(*args, **kwargs)

class RFID(models.Model):
    rfid = models.CharField(max_length=50,blank=False,unique=True,default=uuid.uuid1)
    rfidUser = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.rfid


class UnRegisteredDevice(models.Model):
    sessionID = models.UUIDField(blank=False,null=False)
    deviceID = models.CharField(max_length=15,blank=False,unique=True,default=uuid.uuid1)
    model = models.CharField(max_length=10,blank=True,null=True)
    hardwareVersion = models.CharField(max_length=10,blank=True,null=True)
    softwareVersion = models.CharField(max_length=10,blank=True,null=True)
    devicePassword = models.CharField(max_length=20)
    OTP = models.IntegerField(null=True,blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

class Token(models.Model):
    deviceID = models.OneToOneField(DeviceDetails,blank=False,null=False,on_delete=models.CASCADE,related_name="deviceToken")
    token = models.CharField(max_length=30)
    createdAt = models.DateTimeField(auto_now_add=True)


