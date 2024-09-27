import os

from celery import Celery, shared_task
# import celery
import urllib.request
import requests
import json
import math
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


import datetime
import time
from django.utils import timezone
from datetime import datetime, timedelta, time as datetime_time
import django

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univaProductionMonitor.settings')

django.setup()

from configuration.models import Setting
from django.conf import settings
from data.models import LogData, DeviceData, MachineData,ProductionData, DashbaordData, ProductionUpdateData
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
    send_production_updates()
    date = msg_data.get('date')
    machine_id = msg_data.get('machine_id')

    if date and machine_id :
        generate_shift_report(date, machine_id)
    else:
        print("Missing required arguments for generate_shift_report")
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
    MACHINE_OFFLINE_TIME = settings.MACHINE_OFFLINE_TIME
    
    # setting = Setting.objects.first()
    
    # today = datetime.datetime.now().date()
    currentTimeStamp = time.time()
    # production_data_today = ProductionData.objects.filter(date=today).order_by('timestamp')

    
    group_data = {}

    all_groups = MachineGroup.objects.prefetch_related('machine_list').all()

    last_production_data = ProductionData.objects.order_by('timestamp').last()

    # running_production_date = datetime.today().date()
    try:
        running_shift = last_production_data.shift_number
        running_production_date = last_production_data.production_date
    except:
        running_shift = 1
        running_production_date = datetime.today().date()

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
            current_production_data = ProductionData.objects.filter(production_date = running_production_date, shift_number = running_shift).order_by('timestamp')
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
                ).order_by("timestamp").last()
                lastcount = first_before_data.production_count
            except:
                pass


            if current_production_data:
                for pro_shift_data in current_production_data:
                    temp = pro_shift_data.production_count - lastcount
                    count += temp if temp >= 0 else pro_shift_data.production_count
                    lastcount = pro_shift_data.production_count

                first_production_count = current_production_data.first().production_count
                current_production_count = count

                if current_production_count == first_production_count:
                    time_difference = currentTimeStamp - eval(sub_data_first.timestamp)
                    if time_difference > MACHINE_OFFLINE_TIME:
                        status = 1
                        print(f"Machine {machine_name} status changed to offline.")
                    else:
                        status = 0
                        print(f"Machine {machine_name} status changed to online.")
                else:
                    status = 0
                    print(f"Machine {machine_name} status changed to online.")

                machine.save()

            group_data[group_id]['machines'][machine_id] = {
                'machine_id': machine_id,
                'machine_name': machine_name,
                'status': status,
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

def send_production_updates(date_str=None):
    if date_str is None:
        date_str = timezone.now().strftime('%Y-%m-%d')

    try:
        select_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        print(f"Invalid date format: {date_str}")
        return

    production_data = {
        'date': select_date.strftime('%Y-%m-%d'),
        'machine_groups': []
    }

    for group in MachineGroup.objects.all():
        group_json = {
            'group_name': group.group_name,
            'machines': []
        }

        for machine in group.machine_list.all():
            machine_json = {
                'machine_id': machine.machine_id,
                'machine_name': machine.machine_name,
                'shifts': []
            }

            all_production_data = ProductionData.objects.filter(
                production_date=select_date, machine_id=machine.machine_id
            ).order_by('timestamp')

            total_shifts = ShiftTiming.objects.all()

            for shift in total_shifts:
                if shift.shift_number == 0:
                    continue

                shift_json = {
                    'shift_no': shift.shift_number,
                    'shift_name': shift.shift_name,
                    'shift_start_time': shift.start_time.strftime('%H:%M:%S') if shift.start_time else None,
                    'shift_end_time': shift.end_time.strftime('%H:%M:%S') if shift.end_time else None,
                    'timing': {},
                    'total_shift_production_count': 0
                }

                current_shift_production = all_production_data.filter(
                    shift_number=shift.shift_number
                )
                
                max_production_count = 0

                if current_shift_production.exists():
                    for pro_shift_data in current_shift_production:
                        if pro_shift_data.production_count > max_production_count:
                            max_production_count = pro_shift_data.production_count
                shift_json['total_shift_production_count'] = max_production_count

                machine_json['shifts'].append(shift_json)

            group_json['machines'].append(machine_json)

        production_data['machine_groups'].append(group_json)

    try:
        production_update, created = ProductionUpdateData.objects.get_or_create(
            date=select_date,
            defaults={'production_data': production_data}
        )
        if not created:
            production_update.production_data = production_data
            production_update.save()
    except Exception as e:
        print(f"Error saving production update data: {e}")

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'production_updates', {
            'type': 'send_message',
            'message': production_data
        }
    )

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
    dt = datetime.fromtimestamp(timestamp)
    message_date = dt.date()
    message_time = dt.time()

    if 'PHR' in message_data and 'PMIN' in message_data and 'PSEC' in message_data:
        plcHR = int(message_data['PHR'])
        plcMIN = int(message_data['PMIN'])
        plcSEC = int(message_data['PSEC'])
        # print (plcHR,plcMIN,plcSEC)
        message_time = datetime_time(plcHR, plcMIN, plcSEC)

 
    
    
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

        production_date = message_date - timedelta(days=1) if dt.time() < end_shift_time and shift_number == end_shift_number else message_date

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

                    # print ("Production:",production_data.date,production_data.time,production_data.shift_number, production_data.machine_id, production_data.production_count, production_data.target_production,production_data.production_date)

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

def generate_shift_report(date, machine_id, room_group_name):
    machine_details = get_object_or_404(MachineDetails, machine_id=machine_id)
    machines_details_json = {
        "date": date,
        "machine_id": machine_id,
        "machine_name": machine_details.machine_name,
        "shifts": []
    }

    total_shifts = ShiftTiming.objects.all()
    for shift in total_shifts:
        if shift.shift_number == 0:
            continue

        shift_json = {
            "shift_no": shift.shift_number,
            "shift_name": shift.shift_name,
            "shift_start_time": None,
            "shift_end_time": None,
            "timing": {}
        }
        
        machine_production_data_by_shift = ProductionData.objects.filter(
            production_date=date,
            shift_number=shift.shift_number,
            machine_id=machine_id
        ).order_by('timestamp')

        if machine_production_data_by_shift.exists():
            first_production_data = machine_production_data_by_shift.first()
            last_production_data = machine_production_data_by_shift.last()

            shift_start_datetime = first_production_data.timestamp
            shift_end_datetime = last_production_data.timestamp

            shift_json["shift_start_time"] = shift_start_datetime.strftime('%Y-%m-%d %H:%M:%S')
            shift_json["shift_end_time"] = shift_end_datetime.strftime('%Y-%m-%d %H:%M:%S')

            split_hours = generate_hourly_intervals_with_dates(
                shift_start_datetime.date(),
                shift_end_datetime.date(),
                shift_start_datetime.time(),
                shift_end_datetime.time()
            )

            last_inc_count = 0
            target_production_count = 0
            shift_timing_list = {}

            for start_end_datetime in split_hours:
                count = 0
                start_date, start_time = start_end_datetime[0]
                end_date, end_time = start_end_datetime[1]

                sub_data = machine_production_data_by_shift.filter(
                    timestamp__date__gte=start_date, timestamp__date__lte=end_date,
                    timestamp__time__gte=start_time, timestamp__time__lte=end_time
                )

                if end_date == shift_end_datetime.date() and end_time == shift_end_datetime.time():
                    sub_data = machine_production_data_by_shift.filter(
                        timestamp__date__gte=start_date
                    ).filter(timestamp__time__gte=start_time, timestamp__time__lte=end_time)

                try:
                    sub_data_first = sub_data.first()
                    first_before_data = ProductionData.objects.filter(
                        machine_id=machine_id,
                        timestamp__lt=sub_data_first.timestamp
                    ).last()

                    last_inc_count = first_before_data.production_count if first_before_data else 0
                except:
                    pass

                for data in sub_data:
                    temp_count = data.production_count - last_inc_count
                    count += temp_count if temp_count >= 0 else data.production_count
                    last_inc_count = data.production_count

                    if data.target_production != 0:
                        target_production_count = data.target_production

                shift_timing_list[f"{convert_to_12hr_format(start_time)} - {convert_to_12hr_format(end_time)}"] = {
                    "actual_production": count,
                    "target_production": target_production_count
                }

            shift_json["timing"] = shift_timing_list
        machines_details_json["shifts"].append(shift_json)
    print("Sending shift report data:", machines_details_json)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "shift_groups",
        {
            "type": "shift_report",
            "message": machines_details_json
        }
    )

def generate_hourly_intervals_with_dates(from_date, to_date, start_time, end_time):
    start_datetime = datetime.combine(from_date, start_time)
    end_datetime = datetime.combine(to_date, end_time)

    intervals = []

    if end_datetime <= start_datetime:
        end_datetime += timedelta(days=1)

    while start_datetime < end_datetime:
        next_datetime = start_datetime + timedelta(hours=1)
        if next_datetime > end_datetime:
            intervals.append([
                (start_datetime.date(), start_datetime.time()),
                (end_datetime.date(), end_datetime.time())
            ])
            break
        intervals.append([
            (start_datetime.date(), start_datetime.time()),
            (next_datetime.date(), next_datetime.time())
        ])
        start_datetime = next_datetime

    return intervals

def convert_to_12hr_format(time_24hr):
    return time_24hr.strftime('%I:%M %p')