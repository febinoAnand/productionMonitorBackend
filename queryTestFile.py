import os
import pandas
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univaProductionMonitor.settings')
from datetime import date,datetime

import django
django.setup()

from data.models import ProductionData
from devices.models import ShiftTiming
from datetime import datetime, timedelta






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

# selectDate = date(2024,8,12)
# machineID = 'M003'

# print("Current Date -->",selectDate)
# print("Machine ID -->",machineID)

# ###reference print
# allProductiondata = ProductionData.objects.filter(production_date = selectDate, machine_id = machineID).order_by('timestamp')

# for data in allProductiondata:
#     print (data.date,data.time,data.shift_number,data.production_count,data.timestamp)

# print ()
# ######


# outputJSON = {}

# outputJSON["date"] = selectDate.strftime('%Y-%m-%d')
# outputJSON["machine_id"] = machineID


# totalShifts = ShiftTiming.objects.all()
# print ("Total shift No:")
# for shift in totalShifts:
#     print (" *",shift)

# print ()

# # count = 0
# outputJSON["shifts"] = []

# for shift in totalShifts:
#     if shift.shift_number == 0:
#         continue

#     print ("shiftnumber=",shift.shift_number)
    
#     shiftJson = {}

#     shiftJson["shift_no"] = shift.shift_number
#     shiftJson["shift_name"] = shift.shift_name
    

#     allprodcutionDataQuerySet = ProductionData.objects.all().order_by('timestamp')

#     productionDataQuerySet = allprodcutionDataQuerySet.filter(production_date = selectDate, machine_id = machineID)
    
#     currentShfitProduction = productionDataQuerySet.filter(shift_number = shift.shift_number)

#     if currentShfitProduction.exists():
#         firstProducitonData = currentShfitProduction.first()
#         lastProductiondData = currentShfitProduction.last()    
        
#         shift_start_date = firstProducitonData.date
#         shift_start_time = firstProducitonData.time
#         print("startDate =",shift_start_date)
#         print("startTime =",shift_start_time)

#         shiftJson["shift_start_time"] = str(shift_start_date) + " " + str(shift_start_time)
        
#         shift_end_date = lastProductiondData.date
#         shift_end_time = lastProductiondData.time
#         print("endDate =",shift_end_date)
#         print("endTime =",shift_end_time)

#         shiftJson["shift_end_time"] = str(shift_end_date) + " " + str(shift_end_time)



#         splitHours = generate_hourly_intervals_with_dates(str(shift_start_date), str(shift_end_date), str(shift_start_time), str(shift_end_time))
#         print("splited hours=",splitHours)

#         print ()
#         print ()

#         lastIncCount = 0
#         actualCount = 0
        
#         shiftTimingList = {}

#         for startEndDateTime in splitHours:

#             count = 0
            
            
#             start_date = startEndDateTime[0][0]
#             start_time = startEndDateTime[0][1]

#             end_date = startEndDateTime[1][0]
#             end_time = startEndDateTime[1][1]

#             print (start_date, start_time, end_date, end_time)
#             # print (shift_start_date, shift_start_time, shift_end_date, shift_end_time.strftime("%H:%M"))

#             subData = productionDataQuerySet.filter(date__gte = start_date, date__lte = end_date).filter(time__gte=start_time, time__lt=end_time)

#             if end_date == shift_end_date.strftime("%Y-%m-%d") and end_time == shift_end_time.strftime("%H:%M:%S"):
#                 subData = productionDataQuerySet.filter(date__gte = start_date, date__lte = end_date).filter(time__gte=start_time, time__lte=end_time)

#             try:
#                 subDataFirst = subData.first()
#                 firstBeforeData = allprodcutionDataQuerySet.filter(machine_id = machineID,timestamp__lt = subDataFirst.timestamp,shift_number = shift.shift_number).last()
#                 lastIncCount = firstBeforeData.production_count
                
#             except:
#                 pass

#             print(" -> LastIncCount",lastIncCount)
            
#             for dta in subData:
#                 print (" ->",dta.date,dta.time,dta.shift_number,dta.production_count,dta.timestamp)
#                 temp = dta.production_count - lastIncCount
#                 if temp < 0:
#                     count += dta.production_count
#                 else:
#                     count += temp
#                 lastIncCount = dta.production_count

#             print (" -> Total =",count)
#             shiftTimingList[convert_to_12hr_format(start_time) + " - " + convert_to_12hr_format(end_time)] = count
#             print()

#         shiftJson["timing"] = shiftTimingList

#         print ()
#         print ()
#         print ()
#     else:
#         shiftJson["shift_start_time"] = None
#         shiftJson["shift_end_time"] = None
#         shiftJson["timing"] = {}

#     outputJSON["shifts"].append(shiftJson)

# print ("output json", outputJSON)

# Validate input
        

        # Convert date to the correct format
        # select_date = datetime.strptime(select_date, '%Y-%m-%d').date()

select_date = datetime(2024,8,12)
machine_id = "M003"

print("Current Date -->", select_date)
print("Machine ID -->", machine_id)

print

###reference print
allProductiondata = ProductionData.objects.filter(production_date = select_date, machine_id = machine_id).order_by('timestamp')

for data in allProductiondata:
    print (data.date,data.time,data.shift_number,data.production_count,data.timestamp)

print ()
######

# Query for production data
all_production_data = ProductionData.objects.filter(production_date=select_date, machine_id=machine_id).order_by('timestamp')

output_json = {
    "date": select_date.strftime('%Y-%m-%d'),
    "machine_id": machine_id,
    "shifts": []
}

# Query for all shifts
total_shifts = ShiftTiming.objects.all().order_by('shift_number')
print("Total shift No:")
for shift in total_shifts:
    print(" *", shift)

for shift in total_shifts:
    if shift.shift_number == 0:
        continue

    print("shiftnumber=", shift.shift_number)

    shift_json = {
        "shift_no": shift.shift_number,
        "shift_name": shift.shift_name,
        "shift_start_time": None,
        "shift_end_time": None,
        "timing": {}
    }

    # Get the production data for the current shift
    current_shift_production = all_production_data.filter(shift_number=shift.shift_number)

    if current_shift_production.exists():
        first_production_data = current_shift_production.first()
        last_production_data = current_shift_production.last()

        shift_start_date = first_production_data.date
        shift_start_time = first_production_data.time
        print("startDate =", shift_start_date)
        print("startTime =", shift_start_time)

        shift_json["shift_start_time"] = str(shift_start_date) + " " + str(shift_start_time)

        shift_end_date = last_production_data.date
        shift_end_time = last_production_data.time
        print("endDate =", shift_end_date)
        print("endTime =", shift_end_time)

        shift_json["shift_end_time"] = str(shift_end_date) + " " + str(shift_end_time)

        # Generate hourly intervals within the shift
        split_hours = generate_hourly_intervals_with_dates(
            str(shift_start_date),
            str(shift_end_date),
            str(shift_start_time),
            str(shift_end_time)
        )
        print("splited hours=", split_hours)

        last_inc_count = 0
        shift_timing_list = {}

        for start_end_datetime in split_hours:
            count = 0

            start_date = start_end_datetime[0][0]
            start_time = start_end_datetime[0][1]

            end_date = start_end_datetime[1][0]
            end_time = start_end_datetime[1][1]

            print(start_date, start_time, end_date, end_time)

            sub_data = current_shift_production.filter(
                date__gte=start_date, date__lte=end_date,
                time__gte=start_time, time__lte=end_time,
                
            )
            
            if end_date == shift_end_date.strftime("%Y-%m-%d") and end_time == shift_end_time.strftime("%H:%M:%S"):
                sub_data = current_shift_production.filter(date__gte = start_date, date__lte = end_date).filter(time__gte=start_time, time__lte=end_time)

            try:
                sub_data_first = sub_data.first()
                first_before_data = ProductionData.objects.filter(
                    machine_id=machine_id,
                    timestamp__lt=sub_data_first.timestamp,
                    # shift_number = shift.shift_number
                ).last()
                last_inc_count = first_before_data.production_count
                print(" -> lastdata =", first_before_data.date,first_before_data.time,first_before_data.shift_number,first_before_data.production_count,first_before_data.timestamp)
            except:
                print(" -> lastdata =","No data found")
                pass

            print(" -> LastIncCount", last_inc_count)

            for data in sub_data:
                print(" ->", data.date, data.time, data.shift_number, data.production_count, data.timestamp)
                temp = data.production_count - last_inc_count
                count += temp if temp >= 0 else data.production_count
                last_inc_count = data.production_count

            print(" -> Total =", count)
            shift_timing_list[convert_to_12hr_format(start_time) + " - " + convert_to_12hr_format(end_time)] = count
            print()

        shift_json["timing"] = shift_timing_list
        print()
        print()
        print()

    output_json["shifts"].append(shift_json)

print("output json", output_json)


    

