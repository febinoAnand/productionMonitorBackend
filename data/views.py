import json
from rest_framework import viewsets, status, views
from rest_framework.response import Response
import datetime
from django.core import serializers
from django.db.models import Q
from rest_framework.decorators import action
from .models import *
from .serializers import *
from django.db.models import Sum
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from Userauth.models import UserDetail
from django.db.models import Max
from rest_framework.exceptions import NotFound
from collections import defaultdict
from configuration.models import Setting

class RawGetMethod(views.APIView):
    schema = None
    def get(self,request):
        currentRawData = RawData.objects.all().order_by('-pk')
        jsonRawData = serializers.serialize('json', currentRawData)

        # rawDataSerializer = RawSerializerWithDateTime(currentRawData,many=True)

        # print (rawDataSerializer.data['datetime'])

        # updateDateTime = {'datetime':'testing'}
        # updateDateTime.update(rawDataSerializer.data)

        # return Response(rawDataSerializer.data, status=status.HTTP_201_CREATED)
        return Response(json.loads(jsonRawData), status=status.HTTP_201_CREATED)

class MachineLiveDataViewset(views.APIView):
    schema = None
    def get(self,request):
        # print (request.GET['machineid'])
        machinejson = {}
        machineID = request.GET['machineid']
        machineDetails = MachineDetails.objects.get(machineID = machineID)
        deviceDetails = DeviceDetails.objects.get(deviceID = machineDetails.device.deviceID)
        activeProblemDetails = ProblemData.objects.filter(machineID = machineDetails,endTime=None).order_by('-pk')
        problemHistoryDetails = ProblemData.objects.filter(machineID = machineDetails).exclude(endTime=None).order_by('-pk')

        machineSerializerData = MachineWithoutDeviceSerializer(machineDetails,many=False)
        deviceSerializer = DeviceSerializer(deviceDetails,many=False)

        machineDetailsJson = json.dumps(machineSerializerData.data)
        deviceJson = json.dumps(deviceSerializer.data)

        machinejson["machine"] = json.loads(machineDetailsJson)
        machinejson["device"] = json.loads(deviceJson)

        try:
            problemHistorySerializer = ProblemDataSerializer(problemHistoryDetails,many=True)
            problemHistroyJson = json.dumps(problemHistorySerializer.data)
            machinejson["problemhistory"] = json.loads(problemHistroyJson)

        except Exception as e:
            print("history",e)
            machinejson["problemhistory"] = []

        try:
            activeProblemSerializer = ProblemDataSerializer(activeProblemDetails,many=True)
            activeProblemJson = json.dumps(activeProblemSerializer.data)
            machinejson["activeproblem"] = json.loads(activeProblemJson)
            # print("activeok")
        except Exception as e:
            # print("active",e)
            machinejson["activeproblem"] = []

        # print(machinejson)
        return Response(machinejson,status=status.HTTP_200_OK)

class LiveDataViewset(views.APIView):
    schema = None
    def get(self,request):
        responseArray = []
        machines = MachineDetails.objects.all()
        for machine in machines:
            # print (machine)
            machineEvent = {}
            machineEvent["machineID"] = machine.machineID
            unsolvedeventcount = 0
            try:
                try:
                    currentMachineProblem = ProblemData.objects.filter(machineID=machine,endTime=None).order_by('-pk')
                    unsolvedeventcount = len(currentMachineProblem)
                    machineEvent['unsolvedeventcount'] = unsolvedeventcount
                    currentMachineProblem = currentMachineProblem[0]
                except Exception as e:
                    currentMachineProblem = ProblemData.objects.filter(machineID=machine).order_by('-pk')[0]
                currentEvent = Event.objects.get(eventID = currentMachineProblem.eventID)
                currentEventSerializer = EventSerializer(currentEvent,many=False)
                jsonCurrentEvent = json.dumps(currentEventSerializer.data)
                machineEvent['event'] = json.loads(jsonCurrentEvent)

            except IndexError as indexerr:
                machineEvent['event'] = {}
            except Exception as e:
                machineEvent['event'] = {}
                # print(e)
            responseArray.append(machineEvent)


        # print (responseArray)
        return Response(responseArray,status=status.HTTP_200_OK)
        # return Response({"status":"working fine"},status=status.HTTP_200_OK)


# Create your views here.
class RawDataViewset(viewsets.ModelViewSet):
    serializer_class = RawSerializer
    queryset = RawData.objects.all()
    http_method_names = ['post']

    def create(self,request,*args,**kwargs):
        res = request.body
        print (res)

        # if not RawSerializer(data=request.data).is_valid():
        #     errorJson = {"status":"Not valid JSON"}
        #     return Response(errorJson,status=status.HTTP_201_CREATED)

        try:

            #sample ---- > {"date": "2023-08-26","time": "08:26:17","eventID": "EVE103","machineID": "MAC101","eventGroupID": "EG100"}
            jsondata = json.loads(res)
            tokenString = request.META.get("HTTP_DEVICEAUTHORIZATION")
            currentToken = Token.objects.get(token = tokenString)
            currentEvent = Event.objects.get(eventID=jsondata["eventID"])
            currentGroup = EventGroup.objects.get(groupID = jsondata['eventGroupID'])
            currentMachine = MachineDetails.objects.get(machineID = jsondata['machineID'])
            currentDevice = DeviceDetails.objects.get(deviceID=currentToken.deviceID)


            # for event in currentGroup.events:
            #     if event == currentEvent:

            #TODO validate event and eventGroup

            # if currentToken == None:
            #     errorJson = {"status":"Authentication Error. Add Token in the header in a name of 'DEVICEAUTHORIZATION'"}
            #     return Response(errorJson,status=status.HTTP_201_CREATED)


            # savedToken = Token.objects.get(deviceID = currentDevices)
            # if not currentToken == savedToken.token:
            #     errorJson = {"status":"Authentication Error. Invalid Token"}
            #     return Response(errorJson,status=status.HTTP_201_CREATED)


            # print (currentEvents)
            # print (currentDevices)
            # print (currentGroup)

            RawData.objects.create(
                        date = jsondata['date'],
                        time = jsondata['time'],
                        eventID = currentEvent,
                        deviceID = currentDevice,
                        machineID = currentMachine,
                        eventGroupID = currentGroup,
                        data = jsondata
                    )

            # currentMachine = Machine.objects.get(device = currentDevice)
            # print ("CurrentMachine--", currentMachine)


            eventTime = jsondata['date'] +" "+ jsondata['time']
            resEventTime = datetime.datetime.strptime(eventTime,"%Y-%m-%d %H:%M:%S")
            # print (resEventTime)

            # currentEventGroup = EventGroup.objects.filter(events__in = [currentEvents])
            # print ("currentEventGroup--", currentEventGroup)

            currentEventProblemType = currentEvent.problem.problemType
            # print ("currentEventProblemType---",currentEventProblemType)

            try:
                currentProbleData = ProblemData.objects.filter(eventGroupID = currentGroup, deviceID = currentDevice, machineID = currentMachine).order_by('-id')[0]
                # print("currentProbleDataIssueTime",currentProbleData.issueTime)
                # print("currentProbleDataEndTime",currentProbleData.endTime)
            except Exception as e:
                currentProbleData = None
                # print(e)

            LastProblemData.objects.create(
                date = jsondata['date'],
                time = jsondata['time'],
                eventID = currentEvent,
                eventGroupID = currentGroup,
                machineID = currentMachine,
                deviceID = currentDevice,
                endTime = resEventTime,
            )

            if currentEventProblemType == "FINE":
                if currentProbleData is not None and currentProbleData.endTime == None :
                    currentProbleData.eventID = currentEvent
                    currentProbleData.endTime = resEventTime
                    currentProbleData.save()

            elif currentEventProblemType == "ACKNOWLEDGE":
                if currentProbleData is not None and currentProbleData.acknowledgeTime == None:
                    currentProbleData.acknowledgeTime = resEventTime
                    currentProbleData.save()

            else:
                if currentProbleData == None or currentProbleData.endTime is not None:
                    ProblemData.objects.create(
                        date = jsondata['date'],
                        time = jsondata['time'],
                        eventID = currentEvent,
                        eventGroupID = currentGroup,
                        machineID = currentMachine,
                        deviceID = currentDevice,
                        issueTime = resEventTime,
                    )
                elif currentProbleData is not None or currentProbleData.endTime is None:
                    currentProbleData.date = jsondata['date']
                    currentProbleData.time = jsondata['time']
                    currentProbleData.eventID = currentEvent
                    currentProbleData.issueTime = resEventTime
                    currentProbleData.save()


            jsonResponse = {"data":"Success"}
            return Response(jsonResponse, status=status.HTTP_201_CREATED)
        except Exception as a:
            # print (a)
            # print("Not valid Json")
            RawData.objects.create(
                data = res
            )
            errorJson = {"data":"Not valid","error":str(a)}
            return Response(errorJson,status=status.HTTP_201_CREATED)


    # def create(self,request,*args,**kwargs):
    #     res = request.data
    #     # print (res)
    #
    #     try:
    #         jsondata = json.dumps(res["data"])
    #         RawData.objects.create(
    #             data = jsondata
    #         )
    #         return Response(res,status=status.HTTP_201_CREATED)
    #     except Exception as e:
    #         print("Not valid Json")
    #         RawData.objects.create(
    #             data = res
    #         )
    #         errorJson = {"data":"Not valid"}
    #         return Response(errorJson,status=status.HTTP_201_CREATED)


class ProblemViewSet(viewsets.ModelViewSet):
    schema = None
    serializer_class = ProblemDataSerializer
    queryset = ProblemData.objects.all().order_by('-pk')

class LastProblemViewSet(viewsets.ModelViewSet):
    schema = None
    serializer_class = LastProblemDataSerializer
    queryset = LastProblemData.objects.all().order_by('-pk')

class LogDataViewSet(viewsets.ModelViewSet):
    queryset = LogData.objects.all()
    serializer_class = LogDataSerializer

class DeviceDataViewSet(viewsets.ModelViewSet):
    queryset = DeviceData.objects.all()
    serializer_class = DeviceDataSerializer

class MachineDataViewSet(viewsets.ModelViewSet):
    queryset = MachineData.objects.all()
    serializer_class = MachineDataSerializer

class ProductionDataViewSet(viewsets.ModelViewSet):
    queryset = ProductionData.objects.all()
    serializer_class = ProductionDataSerializer




class DashboardViewSet(viewsets.ViewSet):

    def list(self, request):
        groups = MachineGroup.objects.all()
        dashboard_data = []

        for group in groups:
            machines = group.machine_list.all()
            group_data = {
                'group_id': group.id,
                'group_name': group.group_name,
                'machine_count': machines.count(),
                'machines': []
            }

            for machine in machines:
                production_data = ProductionData.objects.filter(machine_id=machine.machine_id).order_by('-date', '-time').first()
                
                machine_data = {
                    'machine_id': machine.machine_id,
                    'machine_name': machine.machine_name,
                    'production_count': production_data.production_count if production_data else 0,
                    'target_production': production_data.target_production if production_data else 0,
                }
                group_data['machines'].append(machine_data)
            
            dashboard_data.append(group_data)

        return Response(dashboard_data)
 
class ProductionMonitorViewSet(viewsets.ViewSet):

    def list(self, request):
        shift_wise_data = []
        total_production_count_all_shifts = 0
        total_target_production_all_shifts = 0

        shifts = ShiftTiming.objects.all()
        groups = MachineGroup.objects.all()

        cumulative_machine_data = {}

        for shift in shifts:
            shift_data = {
                'shift_id': shift.id,
                'shift_number': shift.shift_number,
                'shift_name': shift.shift_name,
                'shift_start_time': shift.start_time,
                'shift_end_time': shift.end_time,
                'shift_date': shift.create_date_time,
                'groups': [],
                'total_production_count_by_shifts': 0,
                'total_target_count_by_shifts': 0
            }

            for group in groups:
                machines = group.machine_list.all()
                group_data = {
                    'group_id': group.id,
                    'group_name': group.group_name,
                    'machines': [],
                    'total_production_count_by_group': 0,
                    'total_target_count_by_group': 0
                }

                for machine in machines:
                    latest_production_data = ProductionData.objects.filter(
                        machine_id=machine.machine_id,
                        shift_number=shift.shift_number
                    ).order_by('-date', '-time').first()

                    if latest_production_data:
                        production_count = latest_production_data.production_count
                        target_production = latest_production_data.target_production
                    else:
                        production_count = 0
                        target_production = 0

                    machine_data = {
                        'machine_id': machine.machine_id,
                        'machine_name': machine.machine_name,
                        'production_count': production_count,
                        'target_production': target_production
                    }

                    group_data['machines'].append(machine_data)
                    group_data['total_production_count_by_group'] += production_count
                    group_data['total_target_count_by_group'] += target_production

                    if machine.id not in cumulative_machine_data:
                        cumulative_machine_data[machine.machine_id] = {
                            'machine_id': machine.machine_id,
                            'machine_name': machine.machine_name,
                            'cumulative_production_count': production_count,
                            'cumulative_target_production': target_production
                        }
                    else:
                        cumulative_machine_data[machine.machine_id]['cumulative_production_count'] += production_count
                        cumulative_machine_data[machine.machine_id]['cumulative_target_production'] += target_production

                shift_data['groups'].append(group_data)
                shift_data['total_production_count_by_shifts'] += group_data['total_production_count_by_group']
                shift_data['total_target_count_by_shifts'] += group_data['total_target_count_by_group']

            shift_wise_data.append(shift_data)
            total_production_count_all_shifts += shift_data['total_production_count_by_shifts']
            total_target_production_all_shifts += shift_data['total_target_count_by_shifts']

        return Response({
            'shift_wise_data': shift_wise_data,
            'cumulative_machine_data': list(cumulative_machine_data.values()),
            'total_production_count_all_shifts': total_production_count_all_shifts,
            'total_target_production_all_shifts': total_target_production_all_shifts,
        })





class ShiftReportViewSet(viewsets.ViewSet):

    def create(self, request):
        print("Request data:", request.data)  # Debug statement
        serializer = ShiftReportSerializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)  # Debug statement
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract validated data
        date_str = serializer.validated_data.get('date')
        shift_id = serializer.validated_data.get('shift_id')
        machine_id = serializer.validated_data.get('machine_id')
        
        print("Validated data:", serializer.validated_data)  # Debug statement

        # Check if date is a string and parse it
        if isinstance(date_str, str):
            parsed_date = parse_date(date_str)
            print("Successfully parsed date:", parsed_date)
            if parsed_date is None:
                print("Invalid date format")
                return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("Date must be a string")
            return Response({"error": "Date must be a string"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get shift timings
        try:
            shift = ShiftTiming.objects.get(_id=shift_id)
            print("Shift found:", shift)
        except ShiftTiming.DoesNotExist:
            print("Shift not found")
            return Response({"error": "Shift not found"}, status=status.HTTP_404_NOT_FOUND)

        start_time = shift.start_time
        end_time = shift.end_time
        print("Start time:", start_time, "End time:", end_time)

        # Calculate hourly production data
        hourly_data = []
        current_time = datetime.combine(parsed_date, start_time)
        print("Initial current_time:", current_time)

        # Retrieve the machine instance
        try:
            machine = MachineDetails.objects.get(machine_id=machine_id)
            print("Machine found:", machine)
        except MachineDetails.DoesNotExist:
            print("Machine not found")
            return Response({"error": "Machine not found"}, status=status.HTTP_404_NOT_FOUND)
        
        production_data_all = ProductionData.objects.filter(
            date=parsed_date,
            machine_id=machine.machine_id,
        )
        print("Production data for this date and machine:", production_data_all)
        
        while current_time.time() < end_time:
            next_time = current_time + timedelta(hours=1)
            
            # Debug output
            print(f"Filtering data from {current_time.time()} to {next_time.time()}")

            # Retrieve the last entry within the current time period
            last_entry = production_data_all.filter(
                time__gte=current_time.time(),
                time__lt=next_time.time()
            ).order_by('-time').first()

            # Aggregate data from the last entry
            if last_entry:
                production_data = {
                    'production_count': last_entry.production_count,
                    'target_production': last_entry.target_production
                }
            else:
                production_data = {
                    'production_count': 0,
                    'target_production': 0
                }

            # Debug output
            print(f"Production data for period {current_time.time()} to {next_time.time()}: {production_data}")

            hourly_data.append({
                'start_time': current_time.time().strftime('%H:%M:%S'),
                'end_time': next_time.time().strftime('%H:%M:%S'),
                'production_count': production_data['production_count'],
                'target_production': production_data['target_production']
            })
            
            current_time = next_time

            # Exit loop if current_time is beyond the end of the shift day
            if current_time.date() > parsed_date or (current_time.date() == parsed_date and current_time.time() >= end_time):
                break
            
        print("Successfully done")
        # Prepare the response data
        response_data = {
            'date': date_str,
            'shift_id': shift_id,
            'machine_id': machine_id,
            'hourly_data': hourly_data
        }

        return Response(response_data)


class SummaryReportViewSet(viewsets.ViewSet):

    def create(self, request):
        print("Request data:", request.data)  # Debug statement
        serializer = SummaryReportSerializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)  # Debug statement
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract validated data
        date_str = serializer.validated_data.get('date')
        machine_id = serializer.validated_data.get('machine_id')
        
        print("Validated data:", serializer.validated_data)  # Debug statement

        # Parse the date
        parsed_date = date_str
        print("Parsed date:", parsed_date)

        # Retrieve the machine instance
        try:
            machine = MachineDetails.objects.get(machine_id=machine_id)
            print("Machine found:", machine)
        except MachineDetails.DoesNotExist:
            print("Machine not found")
            return Response({"error": "Machine not found"}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve all production data for the given date and machine_id
        production_data = ProductionData.objects.filter(
            date=parsed_date,
            machine_id=machine.id
        ).values('time', 'production_count', 'target_production')
        
        # Convert queryset to list of dicts
        production_data_list = list(production_data)

        # Prepare the response data
        response_data = {
            'date': date_str,
            'machine_id': machine_id,
            'production_data': production_data_list
        }

        print("Response data:", response_data)  # Debug statement

        return Response(response_data, status=status.HTTP_200_OK)
    

class ShiftwiseReportGenerateViewSet(viewsets.ViewSet):

    def create(self, request):
        print("Request data:", request.data)  # Debug statement
        serializer = ShiftwiseReportSerializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)  # Debug statement
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract validated data
        date_str = serializer.validated_data.get('date')
        machine_id = serializer.validated_data.get('machine_id')
        
        print("Validated data:", serializer.validated_data)  # Debug statement

        # Parse date
        parsed_date = serializer.validated_data.get('date')
        print("Parsed date:", parsed_date)
        
        # Retrieve the machine instance
        try:
            machine = MachineDetails.objects.get(machine_id=machine_id)
            print("Machine found:", machine)
        except MachineDetails.DoesNotExist:
            print("Machine not found")
            return Response({"error": "Machine not found"}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve all shift timings
        shifts = ShiftTiming.objects.all()
        shiftwise_data = []

        for shift in shifts:
            start_time = shift.start_time
            end_time = shift.end_time
            print(f"Processing shift: {shift.shift_name}, Start: {start_time}, End: {end_time}")

            shift_data = {
                "shift_name": shift.shift_name,
                "start_time": start_time.strftime('%H:%M:%S'),
                "end_time": end_time.strftime('%H:%M:%S'),
                "production_data": []
            }

            current_time = datetime.combine(parsed_date, start_time)
            while current_time.time() < end_time:
                next_time = current_time + timedelta(hours=1)

                print(f"Filtering data from {current_time.time()} to {next_time.time()}")

                # Filter production data
                production_entries = ProductionData.objects.filter(
                    date=parsed_date,
                    machine_id=machine.id,
                    time__gte=current_time.time(),
                    time__lt=next_time.time()
                )

                # Debug output for each entry
                for entry in production_entries:
                    print(f"Production entry: Time: {entry.time}, Production Count: {entry.production_count}, Target Production: {entry.target_production}")

                    shift_data["production_data"].append({
                        'time': entry.time.strftime('%H:%M:%S'),
                        'production_count': entry.production_count,
                        'target_production': entry.target_production
                    })

                current_time = next_time
                if current_time.date() > parsed_date or (current_time.date() == parsed_date and current_time.time() >= end_time):
                    break

            shiftwise_data.append(shift_data)

        response_data = {
            'date': date_str,
            'machine_id': machine_id,
            'shiftwise_data': shiftwise_data
        }

        print("Successfully done")
        return Response(response_data, status=status.HTTP_200_OK)
    
    
class ListAchievementsViewSet(viewsets.ViewSet):
    def list(self, request):
        # Fetch all unique entry dates in reverse order
        entry_dates = ProductionData.objects.values_list('date', flat=True).distinct().order_by('-date')
        
        # Get all machine groups
        groups = MachineGroup.objects.all()
        
        # Initialize list to store results
        group_productions = []

        for group in groups:
            group_data = {
                'group': group.group_name,
                'dates': []
            }

            for date in entry_dates:
                date_data = {
                    'date': date,
                    'shifts': []
                }
                
                # Get all shifts
                shifts = ShiftTiming.objects.all()
                
                for shift in shifts:
                    shift_start = shift.start_time
                    shift_end = shift.end_time
                    
                    # Initialize counters for the current shift
                    total_production_count = 0
                    total_target_production = 0
                    data_found = False
                    
                    # Get all machines in the current group
                    machines = group.machine_list.all()
                    
                    for machine in machines:
                        # Filter production data for the given date, machine, and shift
                        production_data = ProductionData.objects.filter(
                            date=date,
                            machine_id=machine.id,
                            time__gte=shift_start,
                            time__lt=shift_end
                        ).order_by('-time').first()
                        
                        if production_data:
                            total_production_count += production_data.production_count
                            total_target_production += production_data.target_production
                            data_found = True
                    
                    # Append shift data to date data
                    date_data['shifts'].append({
                        'shift_name': shift.shift_name,
                        'production_count': total_production_count if data_found else 0,
                        'target_production': total_target_production if data_found else 0
                    })
                
                # Append date data to group data
                group_data['dates'].append(date_data)
            
            # Append group data to the final result list
            group_productions.append(group_data)

        # Return the response
        return Response(group_productions)

class EmployeeDetailViewSet(viewsets.ModelViewSet):
    queryset = UserDetail.objects.all()
    serializer_class = EmployeeDetailSerializer
    

class TableReportViewSet(viewsets.ViewSet):
    def create(self, request):
        machine_ids = request.data.get('machine_ids')
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')

        if not machine_ids:
            return Response({"error": "machine_ids is a required parameter"}, status=400)
        if not isinstance(machine_ids, list) or not all(isinstance(id, str) for id in machine_ids):
            return Response({"error": "machine_ids must be a list of strings"}, status=400)
        if not from_date or not to_date:
            return Response({"error": "from_date and to_date are required parameters"}, status=400)

        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        if to_date < from_date:
            return Response({"error": "to_date cannot be before from_date."}, status=400)

        response_data = {
            'from_date': from_date,
            'to_date': to_date,
            'machines': []
        }

        for machine_id in machine_ids:
            data = ProductionData.objects.filter(machine_id=machine_id, date__range=(from_date, to_date))
            latest_data = data.values('shift_id').annotate(last_entry_time=Max('time'))
            
            shifts = []
            for entry in latest_data:
                shift_data = data.filter(shift_id=entry['shift_id'], time=entry['last_entry_time']).first()
                if shift_data:
                    shifts.append({
                        'date': shift_data.date,
                        'time': shift_data.time,
                        'shift_name': shift_data.shift_name,
                        'shift_start_time': shift_data.shift_start_time,
                        'shift_end_time': shift_data.shift_end_time,
                        'production_count': shift_data.production_count,
                        'target_production': shift_data.target_production,
                        'total': shift_data.target_production - shift_data.production_count
                    })
            
            response_data['machines'].append({
                'machine_id': machine_id,
                'shifts': shifts
            })

        serializer = TableReportSerializer(response_data)
        return Response(serializer.data)
    

class GroupWiseMachineDataViewSet(viewsets.ViewSet):
    def create(self, request):
        date = request.data.get('date')
        
        if not date:
            return Response({"error": "date is a required parameter"}, status=400)
        
        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
        
        # Get all groups
        groups = MachineGroup.objects.all()
        group_data = []

        for group in groups:
            machines = group.machine_list.all()
            machine_data = []

            for machine in machines:
                # Get the last data entry for each shift on the specified date
                data = ProductionData.objects.filter(machine_id=machine.machine_id, date=date)
                latest_data = data.values('shift_id').annotate(last_entry_time=Max('time'))
                
                shifts = []
                for entry in latest_data:
                    shift_data = data.filter(shift_id=entry['shift_id'], time=entry['last_entry_time']).first()
                    if shift_data:
                        shifts.append({
                            'date': shift_data.date,
                            'time': shift_data.time,
                            'shift_name': shift_data.shift_name,
                            'shift_start_time': shift_data.shift_start_time,
                            'shift_end_time': shift_data.shift_end_time,
                            'production_count': shift_data.production_count,
                            'target_production': shift_data.target_production,
                            'total': shift_data.target_production - shift_data.production_count,
                            'machine_id': shift_data.machine_id
                        })
                
                machine_data.append({
                    'machine_id': machine.machine_id,
                    'machine_name': machine.machine_name,
                    'shifts': shifts
                })
            
            group_data.append({
                'group_name': group.group_name,
                'group_id': group.id,
                'machines': machine_data
            })
        
        response_data = {
            'date': date,
            'groups': group_data
        }
        
        serializer = ProductionTableSerializer(response_data)
        return Response(serializer.data)
    
class GroupMachineDataViewSet(viewsets.ViewSet):
    def list(self, request):
        today = datetime.today().date()
        
        groups = MachineGroup.objects.all()
        group_data = []

        for group in groups:
            machines = group.machine_list.all()
            machine_data = []

            for machine in machines:
                # Get the shift timings
                shift_timings = ShiftTiming.objects.all()
                shifts = []

                for shift in shift_timings:
                    shift_data = ProductionData.objects.filter(
                        machine_id=machine.machine_id, 
                        date=today, 
                        # shift_id=shift._id
                    ).order_by('-time').first()

                    if shift_data:
                        shifts.append({
                            'date': shift_data.date,
                            'time': shift_data.time,
                            'shift_name': shift.shift_name,
                            'shift_start_time': shift.start_time,
                            'shift_end_time': shift.end_time,
                            'production_count': shift_data.production_count,
                            'target_production': shift_data.target_production,
                            'total': shift_data.target_production - shift_data.production_count
                        })
                    else:
                        shifts.append({
                            'date': today,
                            'time': None,
                            'shift_name': shift.shift_name,
                            'shift_start_time': shift.start_time,
                            'shift_end_time': shift.end_time,
                            'production_count': 0,
                            'target_production': 0,
                            'total': 0
                        })
                
                machine_data.append({
                    'id': machine.id,
                    'machine_id': machine.machine_id,
                    'machine_name': machine.machine_name,
                    'shifts': shifts
                })
            
            group_data.append({
                'group_id': group.id,
                'group_name': group.group_name,
                'machines': machine_data
            })
        
        response_data = {
            'date': today,
            'groups': group_data
        }
        
        return Response(response_data)
        


class ProductionViewSet(viewsets.ViewSet):
    http_method_names = ['post']

    def create(self, request):
        setting = Setting.objects.first()
        enable_printing = setting.enable_printing if setting else False

        select_date = request.data.get('date')
        if not select_date:
            return Response({"error": "Date is required. Please provide a date in YYYY-MM-DD format."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            select_date = datetime.strptime(select_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        if enable_printing:
            print("Selected Date:", select_date)

        machine_groups = MachineGroup.objects.all()
        output_json = {
            "date": select_date.strftime('%Y-%m-%d'),
            "machine_groups": []
        }

        for group in machine_groups:
            group_json = {
                "group_name": group.group_name,
                "machines": []
            }

            for machine in group.machine_list.all():
                machine_json = {
                    "machine_id": machine.machine_id,
                    "machine_name": machine.machine_name,
                    "shifts": []
                }

                all_production_data = ProductionData.objects.filter(production_date=select_date, machine_id=machine.machine_id).order_by('timestamp')
                if enable_printing:
                    print("All Production Data for Machine ID", machine.machine_id, ":", all_production_data)

                total_shifts = ShiftTiming.objects.all()

                for shift in total_shifts:
                    if shift.shift_number == 0:
                        continue

                    shift_json = {
                        "shift_no": shift.shift_number,
                        "shift_name": shift.shift_name,
                        "shift_start_time": None,
                        "shift_end_time": None,
                        "timing": {},
                        "total_shift_production_count": 0
                    }

                    current_shift_production = all_production_data.filter(shift_number=shift.shift_number)
                    if enable_printing:
                        print("Current Shift Production for Shift Number", shift.shift_number, ":", current_shift_production)

                    if current_shift_production.exists():
                        first_production_data = current_shift_production.first()
                        last_production_data = current_shift_production.last()

                        shift_json["shift_start_time"] = f"{first_production_data.date} {first_production_data.time}"
                        shift_json["shift_end_time"] = f"{last_production_data.date} {last_production_data.time}"
                        try:
                            split_hours = self.generate_hourly_intervals_with_dates(
                            str(first_production_data.date),
                            str(last_production_data.date),
                            str(first_production_data.time),
                            str(last_production_data.time)
                           )
                        except AttributeError:
                            return Response({"error": "The method 'generate_hourly_intervals_with_dates' is not defined in 'ProductionViewSet'."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        
                        if enable_printing:
                            print("Splitted hours:", split_hours)

                        last_inc_count = 0
                        shift_timing_list = {}

                        for start_end_datetime in split_hours:
                            count = 0

                            start_date = start_end_datetime[0][0]
                            start_time = start_end_datetime[0][1]

                            end_date = start_end_datetime[1][0]
                            end_time = start_end_datetime[1][1]

                            if enable_printing:
                                print(start_date, start_time, end_date, end_time)

                            sub_data = current_shift_production.filter(
                                date__gte=start_date, date__lte=end_date,
                                time__gte=start_time, time__lte=end_time
                            )
                            
                            if end_date == last_production_data.date.strftime("%Y-%m-%d") and end_time == last_production_data.time.strftime("%H:%M:%S"):
                                sub_data = current_shift_production.filter(date__gte=start_date, date__lte=end_date).filter(time__gte=start_time, time__lte=end_time)

                            try:
                                sub_data_first = sub_data.first()
                                first_before_data = ProductionData.objects.filter(
                                    machine_id=machine.machine_id,
                                    timestamp__lt=sub_data_first.timestamp
                                ).last()
                                last_inc_count = first_before_data.production_count
                            except:
                                pass

                            if enable_printing:
                                print(" -> LastIncCount", last_inc_count)

                            for data in sub_data:
                                if enable_printing:
                                    print(" -> Data Entry:", data.date, data.time, data.shift_number, data.production_count, data.timestamp)
                                temp = data.production_count - last_inc_count
                                count += temp if temp >= 0 else data.production_count
                                last_inc_count = data.production_count

                            if enable_printing:
                                print(" -> Total =", count)
                            shift_timing_list[self.convert_to_12hr_format(start_time) + " - " + self.convert_to_12hr_format(end_time)] = count
                            if enable_printing:
                                print()
                            
                            shift_json["total_shift_production_count"] += count

                        shift_json["timing"] = shift_timing_list
                        if enable_printing:
                            print()
                        
                            print()

                    machine_json["shifts"].append(shift_json)

                group_json["machines"].append(machine_json)

            output_json["machine_groups"].append(group_json)

        if enable_printing:
            print("Output JSON", output_json)
        return Response(output_json, status=status.HTTP_200_OK)


    def generate_hourly_intervals_with_dates(self, from_date, to_date, start_time, end_time):
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

class HourlyShiftReportViewSet(viewsets.ViewSet):
    def create(self, request):
        # Extract date and machine_id from the request data
        select_date = request.data.get('date')
        machine_id = request.data.get('machine_id')

        # Validate input
        if not select_date or not machine_id:
            return Response({"error": "Both 'date' and 'machine_id' are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Convert date to the correct format
        select_date = datetime.strptime(select_date, '%Y-%m-%d').date()

        print("Current Date -->", select_date)
        print("Machine ID -->", machine_id)

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
                split_hours = self.generate_hourly_intervals_with_dates(
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
                    except:
                        pass

                    print(" -> LastIncCount", last_inc_count)

                    for data in sub_data:
                        print(" ->", data.date, data.time, data.shift_number, data.production_count, data.timestamp)
                        temp = data.production_count - last_inc_count
                        count += temp if temp >= 0 else data.production_count
                        last_inc_count = data.production_count

                    print(" -> Total =", count)
                    shift_timing_list[self.convert_to_12hr_format(start_time) + " - " + self.convert_to_12hr_format(end_time)] = count
                    print()

                shift_json["timing"] = shift_timing_list
                print()
                print()
                print()

            output_json["shifts"].append(shift_json)

        print("output json", output_json)
        return Response(output_json, status=status.HTTP_200_OK)

    def generate_hourly_intervals_with_dates(self, from_date, to_date, start_time, end_time):
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

    def convert_to_12hr_format(self, time_24hr_str):
        time_24hr = datetime.strptime(time_24hr_str, '%H:%M:%S')
        time_12hr_str = time_24hr.strftime('%I:%M %p')
        return time_12hr_str 




class HourlyShiftReportViewSet(viewsets.ViewSet):
    def create(self, request):
        setting = Setting.objects.first()
        enable_printing = setting.enable_printing if setting else False

        select_date = request.data.get('date')
        machine_id = request.data.get('machine_id')

        if not select_date or not machine_id:
            return Response({"error": "Both 'date' and 'machine_id' are required."}, status=status.HTTP_400_BAD_REQUEST)

        select_date = datetime.strptime(select_date, '%Y-%m-%d').date()

        all_production_data = ProductionData.objects.filter(production_date=select_date, machine_id=machine_id).order_by('timestamp')

        output_json = {
            "date": select_date.strftime('%Y-%m-%d'),
            "machine_id": machine_id,
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

                shift_json["shift_end_time"] = str(shift_end_date) + " " + str(shift_end_time)

                split_hours = self.generate_hourly_intervals_with_dates(
                    str(shift_start_date),
                    str(shift_end_date),
                    str(shift_start_time),
                    str(shift_end_time)
                )

                last_inc_count = 0
                target_production_count = 0
                shift_timing_list = {}

                for start_end_datetime in split_hours:
                    count = 0
                    target = 0
                    target_production_count = 0

                    start_date = start_end_datetime[0][0]
                    start_time = start_end_datetime[0][1]

                    end_date = start_end_datetime[1][0]
                    end_time = start_end_datetime[1][1]

                    sub_data = current_shift_production.filter(
                        date__gte=start_date, date__lte=end_date,
                        time__gte=start_time, time__lte=end_time
                    )

                    if end_date == shift_end_date.strftime("%Y-%m-%d") and end_time == shift_end_time.strftime("%H:%M:%S"):
                        sub_data = current_shift_production.filter(date__gte=start_date, date__lte=end_date).filter(time__gte=start_time, time__lte=end_time)

                    try:
                        sub_data_first = sub_data.first()
                        first_before_data = ProductionData.objects.filter(
                            machine_id=machine_id,
                            timestamp__lt=sub_data_first.timestamp
                        ).last()
                        
                        if enable_printing:
                        # Debugging: Check first_before_data values
                          print("First before data:", first_before_data.production_count, first_before_data.target_production)
                        
                        last_inc_count = first_before_data.production_count
                        # last_inc_target = first_before_data.target_production
                    except:
                        pass

                    for data in sub_data:
                        temp_count = data.production_count - last_inc_count
                        count += temp_count if temp_count >= 0 else data.production_count
                        last_inc_count = data.production_count
                        target_production_count += data.target_production

                    if target_production_count > 0:
                        last_target_production = target_production_count  # Update last non-zero target production

                    # Replace [0, 0] with [0, last_target_production]
                    if count == 0 and target_production_count == 0:
                        shift_timing_list[self.convert_to_12hr_format(start_time) + " - " + self.convert_to_12hr_format(end_time)] = [0, last_target_production]
                    else:
                        shift_timing_list[self.convert_to_12hr_format(start_time) + " - " + self.convert_to_12hr_format(end_time)] = [count, target_production_count]

                shift_json["timing"] = shift_timing_list

            output_json["shifts"].append(shift_json)

        return Response(output_json, status=status.HTTP_200_OK)

    def generate_hourly_intervals_with_dates(self, from_date, to_date, start_time, end_time):
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

    def convert_to_12hr_format(self, time_24hr_str):
        time_24hr = datetime.strptime(time_24hr_str, '%H:%M:%S')
        time_12hr_str = time_24hr.strftime('%I:%M %p')
        return time_12hr_str



class MachineHourlyDataViewSet(viewsets.ViewSet):
    def create(self, request):
        setting = Setting.objects.first()
        enable_printing = setting.enable_printing if setting else False

        if enable_printing:
              print("Received request with data:", request.data)
        
        machine_id = request.data.get('machine_id')
        date = request.data.get('date')
        
        if not machine_id or not date:
            if enable_printing:
                print("machine_id and date are required parameters.")

            return Response({"message": "machine_id and date are required parameters."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            date = parse_date(date)
            if date is None:
                if enable_printing:
                  print("Invalid date format.")
                raise ValueError("Invalid date format.")
            
            shift_reports = {}
            shifts = ShiftTiming.objects.all()
            if enable_printing:
               print("Retrieved shifts:", shifts)

            for shift in shifts:
                shift_data = ProductionData.objects.filter(date=date, machine_id=machine_id, shift_number=shift.shift_number).order_by('time')
                if enable_printing:
                   print("Shift", shift.shift_number, "data:", shift_data)
                
                if shift_data.exists():
                    first_time = shift_data.first().time
                    last_time = shift_data.last().time
                    if enable_printing:
                      print("First time:", first_time, "Last time:", last_time)

                    # Generate hourly intervals between first and last data times
                    hourly_intervals = []
                    current_time = datetime.combine(date, first_time)
                    end_time = datetime.combine(date, last_time)
                    if enable_printing:
                       print("Generating hourly intervals from", current_time, "to", end_time)

                    while current_time < end_time:
                        next_time = current_time + timedelta(hours=1)
                        hourly_intervals.append((current_time.time(), next_time.time()))
                        current_time = next_time

                    if enable_printing:
                       print("Hourly intervals:", hourly_intervals)
                    hourly_data = {}

                    for start_time, end_time in hourly_intervals:
                        interval_data = shift_data.filter(time__gte=start_time, time__lt=end_time)
                        if enable_printing:
                           print("Interval", start_time, "to", end_time, "data:", interval_data)
                        
                        if interval_data.exists():
                            first_data = interval_data.first().production_count
                            last_data = interval_data.last().production_count
                            count = last_data - first_data
                            if enable_printing:
                               print("First data:", first_data, "Last data:", last_data, "Count:", count)
                        else:
                            count = 0
                            if enable_printing:
                               print("No data found for interval", start_time, "to", end_time)
                        
                        hourly_data[f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"] = count

                    shift_reports[shift.shift_number] = {
                        "date": date,
                        "first_data_time": first_time,
                        "last_data_time": last_time,
                        "hourly_data": hourly_data
                    }
                    if enable_printing:
                      print("Shift", shift.shift_number, "report:", shift_reports[shift.shift_number])
                else:
                    shift_reports[shift.shift_number] = {
                        "date": date,
                        "first_data_time": None,
                        "last_data_time": None,
                        "hourly_data": {}
                    }
                    if enable_printing:
                       print("No data found for shift", shift.shift_number)
                
            return Response(shift_reports, status=status.HTTP_200_OK)
        except Exception as e:
            if enable_printing:
               print("An error occurred:", str(e))
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IndividualViewSet(viewsets.ViewSet):
    def list(self, request):
        setting = Setting.objects.first()
        enable_printing = setting.enable_printing if setting else False
        today = timezone.now().date()
        seven_days_ago = today - timedelta(days=7)
        
        machines = MachineDetails.objects.all()
        machine_data = MachineData.objects.all()
        production_data_today = ProductionData.objects.filter(date=today)
        production_data_last_seven_days = ProductionData.objects.filter(date__range=[seven_days_ago, today])

        machine_data_by_machine = {}
        production_data_by_machine = {}
        daily_production_totals = defaultdict(lambda: {'production_count': 0, 'target_production': 0})

        for data in machine_data:
            machine_id = str(data.machine_id)
            if machine_id not in machine_data_by_machine:
                machine_data_by_machine[machine_id] = []
            machine_data_by_machine[machine_id].append(data)

        for production in production_data_today:
            machine_id = str(production.machine_id)
            if machine_id not in production_data_by_machine:
                production_data_by_machine[machine_id] = []
            production_data_by_machine[machine_id].append(production)

        daily_totals = ProductionData.objects.filter(date__range=[seven_days_ago, today]) \
            .values('date') \
            .annotate(
                total_production_count=Sum('production_count'),
                total_target_production=Sum('target_production')
            ) \
            .order_by('date')

        for total in daily_totals:
            day_name = total['date'].strftime('%A')
            daily_production_totals[day_name] = {
                'production_count': total['total_production_count'],
                'target_production': total['total_target_production']
            }

        today_totals = production_data_today.aggregate(
            total_production_count=Sum('production_count'),
            total_target_production=Sum('target_production')
        )

        machine_details = []
        for machine in machines:
            machine_id = str(machine.machine_id)
            machine_data_for_machine = machine_data_by_machine.get(machine_id, [])
            production_data_for_machine = production_data_by_machine.get(machine_id, [])

            machine_details.append({
                "id": machine.id,
                "machine_id": machine.machine_id,
                "machine_name": machine.machine_name,
                "line": machine.line,
                "manufacture": machine.manufacture,
                "year": machine.year,
                "device": machine.device.id if machine.device else None,
                "production_per_hour": machine.production_per_hour,
                "create_date_time": machine.create_date_time,
                "update_date_time": machine.update_date_time,
                "machine_data": MachineDataSerializer(machine_data_for_machine, many=True).data,
                "production_data": ProductionDataSerializer(production_data_for_machine, many=True).data,
                "last_seven_days_production_by_day": daily_production_totals
            })

        response_data = {
            'machine_details': machine_details,
            'total_production': today_totals
        }
        
        return Response(response_data)

    def retrieve(self, request, pk=None):
        try:
            machine = MachineDetails.objects.get(id=pk)
        except MachineDetails.DoesNotExist:
            raise NotFound("Machine not found")

        today = timezone.now().date()
        seven_days_ago = today - timedelta(days=7)
        
        machine_data = MachineData.objects.filter(machine_id=pk)
        production_data_today = ProductionData.objects.filter(date=today, machine_id=machine.machine_id)
        production_data_last_seven_days = ProductionData.objects.filter(date__range=[seven_days_ago, today], machine_id=machine.machine_id)

        machine_data_serialized = MachineDataSerializer(machine_data, many=True).data
        production_data_serialized = ProductionDataSerializer(production_data_today, many=True).data

        daily_production_totals = defaultdict(lambda: {'production_count': 0, 'target_production': 0})
        daily_totals = ProductionData.objects.filter(date__range=[seven_days_ago, today], machine_id=machine.machine_id) \
            .values('date') \
            .annotate(
                total_production_count=Sum('production_count'),
                total_target_production=Sum('target_production')
            ) \
            .order_by('date')

        for total in daily_totals:
            day_name = total['date'].strftime('%A')
            daily_production_totals[day_name] = {
                'production_count': total['total_production_count'],
                'target_production': total['total_target_production']
            }

        today_totals = production_data_today.aggregate(
            total_production_count=Sum('production_count'),
            total_target_production=Sum('target_production')
        )

        machine_details = {
            "id": machine.id,
            "machine_id": machine.machine_id,
            "machine_name": machine.machine_name,
            "line": machine.line,
            "manufacture": machine.manufacture,
            "year": machine.year,
            "device": machine.device.id if machine.device else None,
            "production_per_hour": machine.production_per_hour,
            "create_date_time": machine.create_date_time,
            "update_date_time": machine.update_date_time,
            "machine_data": machine_data_serialized,
            "production_data": production_data_serialized,
            "last_seven_days_production_by_day": daily_production_totals
        }

        response_data = {
            'machine_details': machine_details,
            'total_production': today_totals
        }
        
        return Response(response_data)
    
class ShiftDataViewSet(viewsets.ViewSet):
    def list(self, request):
        setting = Setting.objects.first()
        enable_printing = setting.enable_printing if setting else False
        today = timezone.now().date()
        production_data_today = ProductionData.objects.filter(date=today).order_by('timestamp')

        previous_counts = {}
        total_production_count = 0
        total_target_production = 0
        total_count_difference = 0
        current_shift = None
        group_data = {}

        all_groups = MachineGroup.objects.prefetch_related('machine_list').all()

        for group in all_groups:
            group_id = group.id
            group_name = group.group_name

            if group_id not in group_data:
                group_data[group_id] = {
                    'group_id': group_id,
                    'group_name': group_name,
                    'machine_count': len(group.machine_list.all()),
                    'machines': {},
                    'total_production_count': 0,
                    'total_target_production': 0,
                    'total_count_difference': 0
                }

            for machine in group.machine_list.all():
                machine_id = machine.machine_id
                machine_name = machine.machine_name

                group_data[group_id]['machines'][machine_id] = {
                    'machine_id': machine_id,
                    'machine_name': machine_name,
                    'production_count': 0,
                    'target_production': 0,
                    'count_difference': 0,
                    'previous_production_count': 0
                }

        for data in production_data_today:
            if data.shift_number != current_shift:
                current_shift = data.shift_number
                for group in group_data.values():
                    group['total_production_count'] = 0
                    group['total_target_production'] = 0
                    group['total_count_difference'] = 0
                    for machine in group['machines'].values():
                        machine['production_count'] = 0
                        machine['target_production'] = 0
                        machine['count_difference'] = 0
                        machine['previous_production_count'] = 0
                total_production_count = 0
                total_target_production = 0
                total_count_difference = 0
                previous_counts = {}

            previous_count = previous_counts.get(data.machine_id, 0)
            count_diff = data.production_count - previous_count
            previous_counts[data.machine_id] = data.production_count

            group = MachineGroup.objects.filter(machine_list__machine_name=data.machine_name).first()
            group_id = group.id if group else None

            if group_id in group_data and data.machine_id in group_data[group_id]['machines']:
                machine_data = group_data[group_id]['machines'][data.machine_id]
                machine_data['production_count'] = data.production_count
                machine_data['target_production'] = data.target_production
                machine_data['count_difference'] = count_diff
                machine_data['previous_production_count'] = previous_count

                group_data[group_id]['total_production_count'] += data.production_count
                group_data[group_id]['total_target_production'] += data.target_production
                group_data[group_id]['total_count_difference'] += count_diff

                total_production_count += data.production_count
                total_target_production += data.target_production
                total_count_difference += count_diff

        response_data = {
            'groups': [
                {
                    **group,
                    'machines': list(group['machines'].values())
                }
                for group in group_data.values()
            ],
        }

        return Response(response_data)
    
class AchievementsViewSet(viewsets.ViewSet):
    def list(self, request):
        setting = Setting.objects.first()
        enable_printing = setting.enable_printing if setting else False
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=9)

        if enable_printing:
           print("Date Range:", start_date, "to", end_date)

        machine_groups = MachineGroup.objects.all()
        output_json = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "achievements": []
        }

        for group in machine_groups:
            group_json = {
                "group_name": group.group_name,
                "dates": []
            }

            for single_date in [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]:
                date_json = {
                    "date": single_date.strftime('%Y-%m-%d'),
                    "shifts": []
                }

                total_shifts = ShiftTiming.objects.all()

                for shift in total_shifts:
                    if shift.shift_number == 0:
                        continue

                    shift_json = {
                        "shift_no": shift.shift_number,
                        "shift_name": shift.shift_name,
                        "total_production_count": 0
                    }

                   
                    all_production_data = ProductionData.objects.filter(
                        production_date=single_date,
                        shift_number=shift.shift_number,
                        machine_id__in=[machine.machine_id for machine in group.machine_list.all()]
                    )

                    total_production_count = all_production_data.aggregate(total_count=Sum('production_count'))['total_count'] or 0

                    shift_json["total_production_count"] = total_production_count
                    date_json["shifts"].append(shift_json)

                group_json["dates"].append(date_json)

            output_json["achievements"].append(group_json)
        if enable_printing:
           print("Output JSON", output_json)
        return Response(output_json, status=status.HTTP_200_OK)

