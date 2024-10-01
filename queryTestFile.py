import os
import pandas
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univaProductionMonitor.settings')
from datetime import date,datetime,time

import django
django.setup()

from data.models import ProductionData
from devices.models import ShiftTiming,MachineDetails
from datetime import datetime, timedelta
from django.db.models import Q



def generate_hourly_intervals_with_dates_shift(from_date, start_time, shift_date, shift_time):
        start_datetime = datetime.strptime(f"{from_date} {start_time}", '%Y-%m-%d %H:%M:%S')
        
        
        max_end_datetime = start_datetime + timedelta(hours=8)
        
        try:
            shift_datetime = datetime.strptime(f"{shift_date} {shift_time}", '%Y-%m-%d %H:%M:%S')
            end_datetime = min(max_end_datetime, shift_datetime)
        except Exception as e:
            end_datetime = max_end_datetime
            
        current_time = datetime.now()
        
        intervals = []
        
        
        while start_datetime < end_datetime:
            next_datetime = start_datetime + timedelta(hours=1)
            
        
            if next_datetime > current_time:
                intervals.append([
                    (start_datetime.strftime('%Y-%m-%d'), start_datetime.strftime('%H:%M:00')),
                    (current_time.strftime('%Y-%m-%d'), current_time.strftime('%H:%M:00'))
                ])
                break
            
        
            if next_datetime > end_datetime:
                intervals.append([
                    (start_datetime.strftime('%Y-%m-%d'), start_datetime.strftime('%H:%M:00')),
                    (end_datetime.strftime('%Y-%m-%d'), end_datetime.strftime('%H:%M:00'))
                ])
                break
            
            intervals.append([
                (start_datetime.strftime('%Y-%m-%d'), start_datetime.strftime('%H:%M:00')),
                (next_datetime.strftime('%Y-%m-%d'), next_datetime.strftime('%H:%M:00'))
            ])
            start_datetime = next_datetime

        return intervals

def generate_hourly_intervals_with_dates_shift_1(from_date, start_time, shift_date, shift_time):
        start_datetime = datetime.strptime(f"{from_date} {start_time}", '%Y-%m-%d %H:%M:%S')
        start_datetime = start_datetime.replace(second=0)
        
        
        max_end_datetime = start_datetime + timedelta(hours=8)
        
        try:
            shift_datetime = datetime.strptime(f"{shift_date} {shift_time}", '%Y-%m-%d %H:%M:%S')
            end_datetime = min(max_end_datetime, shift_datetime)
        except Exception as e:
            end_datetime = max_end_datetime
            
        current_time = datetime.now()
        
        intervals = []
        
        
        while start_datetime < end_datetime:
            next_datetime = start_datetime + timedelta(hours=1)
            
        
            if next_datetime > current_time:
                current_time = current_time.replace(second=0)
                current_time = current_time - timedelta(seconds=1)
                intervals.append([
                    (start_datetime.strftime('%Y-%m-%d'), start_datetime.strftime('%H:%M:00')),
                    (current_time.strftime('%Y-%m-%d'), current_time.strftime('%H:%M:%S'))
                ])
                break
            
        
            if next_datetime > end_datetime:
                current_time = current_time.replace(second=0)
                current_time = current_time - timedelta(seconds=1)
                intervals.append([
                    (start_datetime.strftime('%Y-%m-%d'), start_datetime.strftime('%H:%M:00')),
                    (end_datetime.strftime('%Y-%m-%d'), end_datetime.strftime('%H:%M:%S'))
                ])
                break
            
            intervals.append([
                (start_datetime.strftime('%Y-%m-%d'), start_datetime.strftime('%H:%M:00')),
                (next_datetime.strftime('%Y-%m-%d'), next_datetime.strftime('%H:%M:00'))
            ])
            start_datetime = next_datetime

        return intervals



def generate_hourly_intervals_with_dates(from_date, to_date, start_time, end_time):
    
    start_datetime = datetime.strptime(f"{from_date} {start_time}", '%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.strptime(f"{to_date} {end_time}", '%Y-%m-%d %H:%M:%S')
    
    
    intervals = []

    
    if end_datetime <= start_datetime:
        end_datetime += timedelta(days=1)

    
    while start_datetime < end_datetime:
        next_datetime = start_datetime + timedelta(hours=1) 
        if next_datetime > end_datetime:
            intervals.append([
                (start_datetime.strftime('%Y-%m-%d'), start_datetime.strftime('%H:%M:%S')),
                (end_datetime.strftime('%Y-%m-%d'), end_datetime.strftime('%H:%M:%S'))
            ])
            break
        intervals.append([
            (start_datetime.strftime('%Y-%m-%d'), start_datetime.strftime('%H:%M:%S')),
            (next_datetime.strftime('%Y-%m-%d'), next_datetime.strftime('%H:%M:%S'))
        ])
        start_datetime = next_datetime 
    
    return intervals


def convert_to_12hr_format(time_24hr_str):
    
    time_24hr = datetime.strptime(time_24hr_str, '%H:%M:%S')
    
    time_12hr_str = time_24hr.strftime('%I:%M %p')
    
    return time_12hr_str


print ()


select_date = datetime(2024,9,30)
machine_id = "M017"
shift = 3

start_date = datetime(2024,9,30)
end_date = datetime(2024,9,30)

start_time = time(22,31,4)
end_time = time(23,31,4)

print("Current Date -->", select_date)
print("Machine ID -->", machine_id)
print("shift -->",shift)

print

###reference print
# allProductiondata = ProductionData.objects.filter(production_date = select_date,shift_number = shift, machine_id = machine_id).order_by('-production_count')

# allProductiondata = allProductiondata.filter( Q(date__gte=start_date,time__gte=start_time) | Q(date__lte=end_date,time__lte=end_time))

# if start_time > end_time:
#     allProductiondata = allProductiondata.filter( Q(date__gte=start_date,time__gte=start_time) | Q(date__lte=end_date,time__lt=end_time))
# else:
#     allProductiondata = allProductiondata.filter(date__gte=start_date,date__lte=end_date).filter(time__gte=start_time,time__lt=end_time)
                    


# start_datetime = datetime(2024, 9, 19, 23, 15)
# end_datetime = datetime(2024, 9, 19, 23, 55)

# # Filter the queryset
# allProductiondata = allProductiondata.filter(
#     Q(date__gte=start_datetime.date(), time__gte=start_datetime.time()) |
#     Q(date__lte=end_datetime.date(), time__lte=end_datetime.time())
# )

# start_datetime = datetime(2024, 9, 19, 23, 45)
# end_datetime = datetime(2024, 9, 20, 0, 15)

# # Filter the queryset
# allProductiondata = allProductiondata.filter(
#     timestamp__gte=start_datetime,
#     timestamp__lte=end_datetime
# )

# allProductiondata = allProductiondata.filter(
#     Q(date=start_datetime.date(), time__gte=start_datetime.time()) |  # Same day after start time
#     Q(date=end_datetime.date(), time__lte=end_datetime.time()) |      # Next day before end time
#     Q(date=start_datetime.date() + timedelta(days=1), time__lte=end_datetime.time()) # Handle the case of date span over next day
# )

# for data in allProductiondata:
#     print (data.date,data.time,data.shift_number,data.production_count,data.timestamp)

# print ()


select_date = '2024-09-30'
machine_id = 'M017'



select_date = datetime.strptime(select_date, '%Y-%m-%d').date()
machine = MachineDetails.objects.get(machine_id = machine_id)
if not machine:
    print ("No Machine found")
    exit()

all_production_data = ProductionData.objects.filter(production_date=select_date, machine_id=machine_id).order_by('timestamp')


output_json = {
    "date": select_date.strftime('%Y-%m-%d'),
    "machine_id": machine_id,
    "machine_name": machine.machine_name,
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

    current_shift_production = all_production_data.filter(shift_number=shift.shift_number)

   

    if current_shift_production.exists():
        first_production_data = current_shift_production.first()
        last_production_data = current_shift_production.last()

        
        shift_start_date = first_production_data.date
        shift_start_time = first_production_data.time

        shift_json["shift_start_time"] = str(shift_start_date) + " " + str(shift_start_time)

        shift_end_date = last_production_data.date
        shift_end_time = last_production_data.time
        
        print()
        print("shiftno->",shift.shift_number)
        for data in current_shift_production:
            print (data.date,data.time,data.shift_number,data.production_count,data.timestamp)
        print ()
        

        try:
            nextShiftEndData = ProductionData.objects.filter(timestamp__gt=last_production_data.timestamp, machine_id=machine_id).order_by('timestamp').first()
            next_shift_date = nextShiftEndData.date
            next_shift_time = nextShiftEndData.time
        except Exception as e:
            next_shift_date = ""
            next_shift_time = ""
            print ("Not found next shift data")


        split_hours = generate_hourly_intervals_with_dates_shift(
            str(shift_start_date),
            str(shift_start_time),
            str(next_shift_date),
            str(next_shift_time)
        )

        # print ("split-hours",split_hours)
        # for hours in split_hours:
        #     print(hours[0],"-",hours[1])


        last_inc_count = 0
        target_production_count = 0
        shift_timing_list = {}
        total_count = 0

        for start_end_datetime in split_hours:
            count = 0
            target = 0
            target_production_count = 0
            
            

            start_date = start_end_datetime[0][0]
            start_time = start_end_datetime[0][1]

            end_date = start_end_datetime[1][0]
            end_time = start_end_datetime[1][1]

            shift_json["shift_end_time"] = str(end_date) + " " + str(end_time)

            print('[',start_date,start_time,'-',end_date,end_time,']')
            
            
            # if start time is greater than end time, means next day changed. below condition will sort the data
            if start_time > end_time:
                sub_data = current_shift_production.filter( Q(date__gte=start_date,time__gte=start_time) | Q(date__lte=end_date,time__lt=end_time))
            else:
                sub_data = current_shift_production.filter(date__gte=start_date,date__lte=end_date).filter(time__gte=start_time,time__lt=end_time)
            

            if end_date == shift_end_date.strftime("%Y-%m-%d") and end_time == shift_end_time.strftime("%H:%M:%S"):
                sub_data = current_shift_production.filter(date__gte=start_date, date__lte=end_date).filter(time__gte=start_time, time__lte=end_time)

            try:
                sub_data_first = sub_data.first()
                first_before_data = ProductionData.objects.filter(
                    machine_id=machine_id,
                    timestamp__lt=sub_data_first.timestamp
                ).order_by('timestamp').last()
                
                print ("first before ->",first_before_data.date,first_before_data.time,first_before_data.shift_number,first_before_data.production_count,first_before_data.timestamp)
                # if enable_printing:
                # # Debugging: Check first_before_data values
                #     print("First before data:", first_before_data.production_count, first_before_data.target_production)
                
                last_inc_count = first_before_data.production_count
                # last_inc_target = first_before_data.target_production
            except:
                pass

            for data in sub_data:
                
                
                
                count += max(0, data.production_count - last_inc_count)
                last_inc_count = data.production_count
                # print(f"last count -->{last_inc_count}")
                target_production_count = data.target_production

                print (data.date,data.time,data.shift_number,data.production_count,data.timestamp,count)

            
            total_count += count
            # print(start_date,start_time,"-",end_date,end_time,count)
            if target_production_count > 0:
                last_target_production = target_production_count  # Update last non-zero target production
            
            print ()

            # Replace [0, 0] with [0, last_target_production]
            if count == 0 and target_production_count == 0:
                shift_timing_list[convert_to_12hr_format(start_time) + " - " + convert_to_12hr_format(end_time)] = [0, last_target_production]
            else:
                shift_timing_list[convert_to_12hr_format(start_time) + " - " + convert_to_12hr_format(end_time)] = [count, target_production_count]

            # if enable_printing:
            #     print(f"Interval: {start_time} - {end_time}, Count: {count}, Target: {target_production_count}")
        print("total count->",total_count)
        shift_json["timing"] = shift_timing_list
        

    output_json["shifts"].append(shift_json)

# print(output_json)