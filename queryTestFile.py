import os
import pandas
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univaProductionMonitor.settings')
from datetime import date

import django
django.setup()

from data.models import ProductionData
from devices.models import ShiftTiming
from datetime import datetime, timedelta



selectDate = date(2024,8,6)
machineID = 'M001'

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
                (start_datetime.strftime('%Y-%m-%d'), start_datetime.strftime('%H:%M')),
                (end_datetime.strftime('%Y-%m-%d'), end_datetime.strftime('%H:%M'))
            ])
            break
        intervals.append([
            (start_datetime.strftime('%Y-%m-%d'), start_datetime.strftime('%H:%M')),
            (next_datetime.strftime('%Y-%m-%d'), next_datetime.strftime('%H:%M'))
        ])
        start_datetime = next_datetime
    
    return intervals


print ()


allProductiondata = ProductionData.objects.all().order_by('timestamp').filter(production_date = selectDate, machine_id = machineID)

# lastProductionData = ProductionData.objects.all().order_by('timestamp').filter(production_date = selectDate, machine_id = machineID).first()

# lastProdcutionCount = lastProductionData.production_count

# print(allProductiondata)

# allProductiondata =  allProductiondata.filter(date__gte="2024-08-06",date__lte="2024-08-07")
# allProductiondata =  allProductiondata.filter(date__gte="2024-08-06",date__lte="2024-08-07").filter(time__gte = '22:00:00' , time__lte = '06:30:00' )

for data in allProductiondata:
    print (data.date,data.time,data.shift_number,data.production_count)


print ()

totalShifts = ShiftTiming.objects.all()
print ("Total shift No:")
for shift in totalShifts:
    print (" *",shift)

print ()

# count = 0


for shift in totalShifts:
    if shift.shift_number == 0:
        continue

    

    print ("shiftnumber=",shift.shift_number)
    
    prodcutionDataQuerySet = ProductionData.objects.filter(production_date = selectDate, machine_id = machineID, shift_number = shift.shift_number).order_by('timestamp')
    

    productionData = prodcutionDataQuerySet.first()
    shift_start_date = productionData.date
    shift_start_time = productionData.time
    print("startDate =",shift_start_date)
    print("startTime =",shift_start_time)


    productionData = prodcutionDataQuerySet.last()
    shift_end_date = productionData.date
    shift_end_time = productionData.time
    print("endDate =",shift_end_date)
    print("endTime =",shift_end_time)


    splitHours = generate_hourly_intervals_with_dates(str(shift_start_date), str(shift_end_date), str(shift_start_time), str(shift_end_time))
    print("splited hours=",splitHours)

    print ()
    print ()


    for startEndDateTime in splitHours:
        count = 0
        lastIncCount = 0

        start_date = startEndDateTime[0][0]
        start_time = startEndDateTime[0][1]

        end_date = startEndDateTime[1][0]
        end_time = startEndDateTime[1][1]

        # print ("startEndDateTime", startEndDateTime)
        

        # temp_end_time = datetime.strptime(end_time,'%H:%M')

        # temp_end_time -= timedelta(seconds=1)

        # end_time = str(temp_end_time)

        print (start_date, start_time, end_date, end_time)
        
        subData = prodcutionDataQuerySet.filter(date__gte = start_date, date__lte = end_date).filter(time__gte=start_time, time__lte=end_time)

        for dta in subData:

            print (" ->",dta.date,dta.time,dta.shift_number,dta.production_count)
            temp = dta.production_count - lastIncCount
            if temp < 0:
                count += dta.production_count
            else:
                count += temp

            lastIncCount = dta.production_count
        print (" -> Total =",count)
        print()

    print ()
    print ()
    print ()


    

