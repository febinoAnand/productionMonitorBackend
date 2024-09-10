import os

from celery import Celery, shared_task
# import celery
import urllib.request
import requests
import json
import math

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


import datetime
import time


import django

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univaProductionMonitor.settings')

django.setup()

from configuration.models import Setting
from django.conf import settings
from data.models import LogData, DeviceData, MachineData,ProductionData, DashbaordData
from devices.models import DeviceDetails, MachineDetails,ShiftTiming, MachineGroup


app = Celery('univaProductionMonitor')
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# @app.task(bind=True, ignore_result=True)
@shared_task
def processAndSaveMqttData(msg_data):
    
    # print ("Received Data-->",msg_data)
    handle_production_data(msg_data)
    update_dashboard_data()
    # print ("Finished...")

    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)(
    #     'productionMonitorGroup', {
    #         'type' : 'sendmqttmessage',
    #         'value': json.loads(arg)
    #         }
    # )
    
    # from emailtracking.tasks import inboxReadTask
    # inboxReadTask(arg)

# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(5.0, mainMailReadTask.s())

def update_dashboard_data():
    # print ("Updating dashboard data...")
    
    # setting = Setting.objects.first()
    
    # today = datetime.datetime.now().date()
    currentTimeStamp = time.time()
    # production_data_today = ProductionData.objects.filter(date=today).order_by('timestamp')

    
    group_data = {}

    all_groups = MachineGroup.objects.prefetch_related('machine_list').all()

    last_production_data = ProductionData.objects.order_by('-timestamp').first()

    running_production_date = datetime.datetime.today().date()
    try:
        running_shift = last_production_data.shift_number
        # running_production_date = last_production_data.production_date
    except:
        running_shift = 1
        # running_production_date = datetime.today().date()

    # running_shift = 1
    # running_production_date = date(2024,8,31)

    # print(running_production_date, "--",running_shift)

    for group in all_groups:
        group_id = group.id
        group_name = group.group_name

        if group_id not in group_data:
            group_data[group_id] = {
                'group_id': group_id,
                'group_name': group_name,
                'machine_count': len(group.machine_list.all()),
                'running_shift':running_shift,
                'machines': {},
                'total_production_count': 0,
                'total_target_production': 0,
                'total_count_difference': 0
            }

        for machine in group.machine_list.all():
            machine_id = machine.machine_id
            machine_name = machine.machine_name
            machine_target = machine.production_per_hour
            # print("currenttime->",currentTimestamp)
            count = 0
            lastcount = 0
            multiplyTraget = 0
            current_production_data = ProductionData.objects.filter(date = running_production_date, shift_number = running_shift).order_by('timestamp')
            if current_production_data.exists():
                sub_data_first = current_production_data.first()
                multiplyTraget = math.ceil((currentTimeStamp - eval(sub_data_first.timestamp))/3600)
                if multiplyTraget > 8:
                    multiplyTraget = 8
                # print (machine_name,"Mulitply Traget : ",currentTimeStamp, "-", sub_data_first.timestamp , "=",currentTimeStamp-eval(sub_data_first.timestamp),multiplyTraget)
                current_production_data = current_production_data.filter(machine_id=machine_id)

            

            try:
                
                sub_data_first = current_production_data.first()
                first_before_data = ProductionData.objects.filter(
                    machine_id=machine.machine_id,
                    timestamp__lt=sub_data_first.timestamp
                ).last()
                lastcount = first_before_data.production_count
            except:
                pass


            if current_production_data:
                for pro_shift_data in current_production_data:
                    temp = pro_shift_data.production_count - lastcount
                    count += temp if temp >= 0 else pro_shift_data.production_count
                    lastcount = pro_shift_data.production_count
                

            group_data[group_id]['machines'][machine_id] = {
                'machine_id': machine_id,
                'machine_name': machine_name,
                'production_count': count,
                'target_production': machine_target * multiplyTraget,
                'count_difference': 0,
                'previous_production_count': 0
            }

    response_data = {
        'groups': [
            {
                **group,
                'machines': list(group['machines'].values())
            }
            for group in group_data.values()
        ],
    }

    try:
        dashboardData = DashbaordData.objects.all().first()
        if dashboardData:
            dashboardData.dashbaordData = response_data
            dashboardData.save()
        else:
            DashbaordData.objects.create(dashbaordData = response_data)
            print ("No data found...")
    except Exception as e:
        print (e)
        
    # print (response_data)
    send_to_socket(response_data)

def send_to_socket(websocket_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'productionMonitorGroup', {
            'type' : 'sendmqttmessage',
            'value': websocket_data
            }
    )

def handle_production_data(message_data):
    setting = Setting.objects.first()
    enable_printing = setting.enable_printing if setting else False

    end_shift_time_str = settings.END_SHIFT_TIME
    end_shift_number = settings.END_SHIFT_NUMBER

    if isinstance(end_shift_time_str, str):
        end_shift_time = datetime.datetime.strptime(end_shift_time_str, "%H:%M:%S").time()
    else:
        # If end_shift_time_str is already a time object, use it directly
        end_shift_time = end_shift_time_str

    timestamp = message_data['timestamp']
    # dt = datetime.datetime.utcfromtimestamp(timestamp)
    dt = datetime.datetime.fromtimestamp(timestamp)
    message_date = dt.date()
    message_time = dt.time()

    if 'PHR' in message_data and 'PMIN' in message_data and 'PSEC' in message_data:
        plcHR = int(message_data['PHR'])
        plcMIN = int(message_data['PMIN'])
        plcSEC = int(message_data['PSEC'])
        # print (plcHR,plcMIN,plcSEC)
        message_time = datetime.time(plcHR,plcMIN,plcSEC)

 
    
    
    device_token = message_data['device_token']
    shift_number = message_data['shift_no']
    errors = []

    for machine_id, production_count in message_data.items():
        if machine_id in ['timestamp', 'device_token', 'shift_no']:
            continue

        machine = MachineDetails.objects.filter(machine_id=machine_id).first()
        if not machine:
            # errors.append(f"No machine found for machine_id: {machine_id}")
            if enable_printing:
              print(f"No machine found for machine_id: {machine_id}")
            continue

        try:
            last_production_data = ProductionData.objects.filter(machine_id=machine.machine_id, timestamp__lt = timestamp).order_by('-timestamp').first()
        except Exception as e:
           pass

        # print ("Last production:",last_production_data.date,last_production_data.time,last_production_data.shift_number, last_production_data.machine_id, last_production_data.production_count, last_production_data.target_production)
        # if last_production_data and last_production_data.production_count > production_count:
        #     errors.append({
        #         "status": "PRODUCTION COUNT ERROR",
        #         "message": "Production count is less than last recorded count for " + machine_id,
        #         "device_token": device_token,
        #         "production_count": production_count,
        #         "timestamp": timestamp
        #     })
        #     print('Production count is less than the last recorded count')
        #     continue

        shift_instance = ShiftTiming.objects.filter(shift_number=shift_number).first()
        if not shift_instance:
            shift_instance = ShiftTiming(
                shift_number=shift_number,
                start_time=None,
                end_time=None,
                shift_name=None
            )
            shift_instance.save()

        production_date = message_date - datetime.timedelta(days=1) if dt.time() < end_shift_time and shift_number == end_shift_number else message_date

        try:
            if not last_production_data or last_production_data.shift_number != shift_instance.shift_number or last_production_data.target_production != machine.production_per_hour or last_production_data.production_count != production_count or last_production_data.production_date != production_date:
                if last_production_data and production_count == 0 and last_production_data.shift_number == shift_instance.shift_number:
                   pass
                else:
                    production_data = ProductionData(
                        date=message_date,
                        time=message_time,
                        shift_number=shift_instance.shift_number,
                        shift_name=shift_instance.shift_name,
                        target_production=machine.production_per_hour,
                        machine_id=machine.machine_id,
                        machine_name=machine.machine_name,
                        production_count=production_count,
                        production_date=production_date,
                        log_data_id=message_data["log_id"],
                        timestamp=timestamp
                    )
                    production_data.save()
                # print ("Production:",production_data.date,production_data.time,production_data.shift_number, production_data.machine_id, production_data.production_count, production_data.target_production)

                    if enable_printing:
                        print(f'Saved production data to database: {production_data}')

        except Exception as e:
            errors.append({
                "status": "DATA SAVE ERROR",
                "message": f"Error saving production data: {e}",
                "device_token": device_token,
                "timestamp": timestamp,
            })
            if enable_printing:
              print(f'Error saving production data to database: {e}')
            continue
    # print()   
    if errors:
        for error in errors:
            response = {
                "status": "ERROR",
                "message": error
            }
            print (response)
    #         publish_response(mqtt_client, device_token, response, is_error=True)
    #     return False

    # response = {
    #     "status": "OK",
    #     "message": "Successfully saved data",
    #     "device_token": device_token,
    #     "timestamp": timestamp
    # }
    # publish_response(mqtt_client, device_token, response)