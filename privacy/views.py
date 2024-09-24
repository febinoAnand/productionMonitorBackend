from django.shortcuts import render
# from django.http import HttpResponse

# Create your views here.
def privacyView(request):
    
    return render(request,'privacy/policy.html')