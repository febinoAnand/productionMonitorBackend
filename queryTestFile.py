import os
import pandas
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univaProductionMonitor.settings')
from datetime import date

import django
django.setup()

from data.models import ProductionData
from devices.models import ShiftTiming
from datetime import datetime, timedelta



selectDate = date(2024,8,10)
machineID = 'M003'

print("Current Date -->",selectDate)
print("Machine ID -->",machineID)


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

###reference print
allProductiondata = ProductionData.objects.filter(production_date = selectDate, machine_id = machineID).order_by('timestamp')

for data in allProductiondata:
    print (data.date,data.time,data.shift_number,data.production_count,data.timestamp)

print ()
######


outputJSON = {}

outputJSON["date"] = selectDate.strftime('%Y-%m-%d')
outputJSON["machine_id"] = machineID


totalShifts = ShiftTiming.objects.all()
print ("Total shift No:")
for shift in totalShifts:
    print (" *",shift)

print ()

# count = 0
outputJSON["shifts"] = []

for shift in totalShifts:
    if shift.shift_number == 0:
        continue

    print ("shiftnumber=",shift.shift_number)
    
    shiftJson = {}

    shiftJson["shift_no"] = shift.shift_number
    shiftJson["shift_name"] = shift.shift_name
    

    allprodcutionDataQuerySet = ProductionData.objects.all().order_by('timestamp')

    productionDataQuerySet = allprodcutionDataQuerySet.filter(production_date = selectDate, machine_id = machineID)
    
    currentShfitProduction = productionDataQuerySet.filter(shift_number = shift.shift_number)

    if currentShfitProduction.exists():
        firstProducitonData = currentShfitProduction.first()
        lastProductiondData = currentShfitProduction.last()    
        
        shift_start_date = firstProducitonData.date
        shift_start_time = firstProducitonData.time
        print("startDate =",shift_start_date)
        print("startTime =",shift_start_time)

        shiftJson["shift_start_time"] = str(shift_start_date) + " " + str(shift_start_time)
        
        shift_end_date = lastProductiondData.date
        shift_end_time = lastProductiondData.time
        print("endDate =",shift_end_date)
        print("endTime =",shift_end_time)

        shiftJson["shift_end_time"] = str(shift_end_date) + " " + str(shift_end_time)



        splitHours = generate_hourly_intervals_with_dates(str(shift_start_date), str(shift_end_date), str(shift_start_time), str(shift_end_time))
        print("splited hours=",splitHours)

        print ()
        print ()

        lastIncCount = 0
        actualCount = 0
        
        shiftTimingList = {}

        for startEndDateTime in splitHours:

            count = 0
            
            
            start_date = startEndDateTime[0][0]
            start_time = startEndDateTime[0][1]

            end_date = startEndDateTime[1][0]
            end_time = startEndDateTime[1][1]

            print (start_date, start_time, end_date, end_time)
            # print (shift_start_date, shift_start_time, shift_end_date, shift_end_time.strftime("%H:%M"))

            subData = productionDataQuerySet.filter(date__gte = start_date, date__lte = end_date).filter(time__gte=start_time, time__lt=end_time)

            if end_date == shift_end_date.strftime("%Y-%m-%d") and end_time == shift_end_time.strftime("%H:%M:%S"):
                subData = productionDataQuerySet.filter(date__gte = start_date, date__lte = end_date).filter(time__gte=start_time, time__lte=end_time)

            try:
                subDataFirst = subData.first()
                firstBeforeData = allprodcutionDataQuerySet.filter(machine_id = machineID,timestamp__lt = subDataFirst.timestamp).last()
                lastIncCount = firstBeforeData.production_count
                
            except:
                pass

            print(" -> LastIncCount",lastIncCount)
            
            for dta in subData:
                print (" ->",dta.date,dta.time,dta.shift_number,dta.production_count,dta.timestamp)
                temp = dta.production_count - lastIncCount
                if temp < 0:
                    count += dta.production_count
                else:
                    count += temp
                lastIncCount = dta.production_count

            print (" -> Total =",count)
            shiftTimingList[convert_to_12hr_format(start_time) + " - " + convert_to_12hr_format(end_time)] = count
            print()

        shiftJson["timing"] = shiftTimingList

        print ()
        print ()
        print ()
    else:
        shiftJson["shift_start_time"] = None
        shiftJson["shift_end_time"] = None
        shiftJson["timing"] = {}

    outputJSON["shifts"].append(shiftJson)

print ("output json", outputJSON)


    

