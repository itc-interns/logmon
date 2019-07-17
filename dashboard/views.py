from django.shortcuts import render
from .models import LogsHolder, error_logs
# To initialize the offset to 0 for the first time and to keep track of the number of requests
counter = 0
globaldata = []

def viewall(request):
    global counter
    global globaldata
    counter += 1
    data = []
    noOutput = False
    if request.method == "POST":
        if request.POST.get("reset"):
            counter = 0
            globaldata = []
            request.session['offset'] = 0
        elif request.POST.get("search"):
            request.session['offset'] = 0
            # Get each response of each input field
            remoteAddr = request.POST.get("remoteAddr")
            remoteUser = request.POST.get("remoteUser")
            requestAttr = request.POST.get("requestAttr")
            status = request.POST.get("status")
            httpReferer = request.POST.get("httpReferer")
            httpUserAgent = request.POST.get("httpUserAgent")
            # print(remoteAddr,remoteUser,requestAttr,status,httpReferer,httpUserAgent)

            data = LogsHolder.objects.filter(remoteAddr__contains = remoteAddr, remoteUser__contains = remoteUser, request__contains = requestAttr, status__contains = status, httpReferer__contains = httpReferer, httpUserAgent__contains = httpUserAgent).order_by('-id')
            if(len(data) == 0):
                noOutput = True
            globaldata = data

        elif request.POST.get("next"):
            # On each next increment the offset by 10 
            request.session['offset'] += 10
            # data = LogsHolder.objects.all().order_by('-id')
        
        elif request.POST.get("previous"):
            if request.session['offset'] == 0:
                data = LogsHolder.objects.all().order_by('-id')[:10]
                data = data[int(request.session.get("offset")):][:10]
                return render(request, "dashboard/viewall.html", {
                    "data": data
                })
            request.session['offset'] -= 10
            # data = LogsHolder.objects.all().order_by('-id')            
    # Return first 10 latest responses from the database on default
    if counter == 1:
        request.session['offset'] = 0
    # Set the default response to the latest 10 responses
    if len(globaldata) == 0:
        data = LogsHolder.objects.all().order_by('-id')
        globaldata = data
    # Limit the response to 10 per page
    data = globaldata[int(request.session.get("offset")):][:10]
    if len(data) < 10:
        hide = True
    else:
        hide = False
    totalCount = len(globaldata)
    for i in data:
        print(i.timeLocal)
    return render(request, "dashboard/viewall.html", {

        "data": data,
        "hide": hide,
        "totalCount": totalCount,
        "start": int(int(request.session.get("offset")) + 1),
        "end": int(int(request.session.get("offset")) + len(data)),
        "noOutput": noOutput,
        "totalData": globaldata,
        "pathToFolder": request.session.get("source")
    })

def index(request):
    # Complete the insertion of the data and return to dashboard
    with open('./api/rules/rules.conf') as rules:

        pathToFolder = request.session.get('source')

        return render(request, "dashboard/index.html", {'pathToFolder': pathToFolder, 'rules':rules })

def threats(request):
    return render(request, "dashboard/threats.html")

def viewerror(request):
    data =  error_logs.objects.all()

    return render(request,"dashboard/viewerror.html", {'data': data})