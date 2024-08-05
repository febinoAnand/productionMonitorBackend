import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univaProductionMonitor.settings')
from datetime import date

import django
django.setup()

from data.models import ProductionData



# specific_date = date(2023, 8, 5)



selectDate = date(2024,8,3)
machineID = 'M003'

print("Current Date -->",selectDate)
print("Machine ID -->",machineID)

allProductiondata = ProductionData.objects.all().order_by('timestamp').filter(production_date = selectDate, machine_id = machineID)

lastProductionData = ProductionData.objects.all().order_by('timestamp').filter(production_date = selectDate, machine_id = machineID).first()

lastProdcutionCount = lastProductionData.production_count

print(lastProdcutionCount)



currentDataCount = 0
lastDataCount = 0
count = 0

for data in allProductiondata:
    currentDataCount = data.production_count
    count +=  currentDataCount -lastProdcutionCount
    lastProdcutionCount = currentDataCount
    

    print(data.production_date, data.time, data.shift_number ,data.production_count , count)    



