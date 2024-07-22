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
                production_data = ProductionData.objects.filter(machine_id=machine.id).order_by('-date', '-time').first()
                
                machine_data = {
                    'machine_id': machine.id,
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

        shifts = ShiftTimings.objects.all()
        groups = MachineGroup.objects.all()

        cumulative_machine_data = {}

        for shift in shifts:
            shift_data = {
                'shift_id': shift._id,
                'shift_name': shift.shift_name,
                'shift_start_time': shift.start_time,
                'shift_end_time': shift.end_time,
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
                        machine_id=machine.id,
                        shift_id=shift._id
                    ).order_by('-date', '-time').first()

                    if latest_production_data:
                        production_count = latest_production_data.production_count
                        target_production = latest_production_data.target_production
                    else:
                        production_count = 0
                        target_production = 0

                    machine_data = {
                        'machine_id': machine.id,
                        'machine_name': machine.machine_name,
                        'production_count': production_count,
                        'target_production': target_production
                    }

                    group_data['machines'].append(machine_data)
                    group_data['total_production_count_by_group'] += production_count
                    group_data['total_target_count_by_group'] += target_production

                    if machine.id not in cumulative_machine_data:
                        cumulative_machine_data[machine.id] = {
                            'machine_id': machine.id,
                            'machine_name': machine.machine_name,
                            'cumulative_production_count': production_count,
                            'cumulative_target_production': target_production
                        }
                    else:
                        cumulative_machine_data[machine.id]['cumulative_production_count'] += production_count
                        cumulative_machine_data[machine.id]['cumulative_target_production'] += target_production

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
            shift = ShiftTimings.objects.get(_id=shift_id)
            print("Shift found:", shift)
        except ShiftTimings.DoesNotExist:
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
            machine_id=machine.id,
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



