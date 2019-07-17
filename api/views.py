from django.shortcuts import render
from django.http import JsonResponse
from index.models import daily_bandwidth
from dashboard.models import LogsHolder, error_logs
from django.db.models import Q
from django.contrib.gis.geoip2 import GeoIP2
from urllib.parse import unquote
from datetime import datetime, timedelta
from functools import reduce
import calendar
import os
import re
import pandas as pd
from decouple import config


def statuscodehits(request):
    data = {}

    # To retrive all the status codes present in the log
    apisList = []
    apis = LogsHolder.objects.values('status').distinct()
    for status in apis:
        apisList.append(status['status'])

    # Get the count of each status codes in the log
    statusCodeHits = []
    for status in apisList:
        temp = {}
        temp['status'] = int(status)
        temp['hits'] = int(LogsHolder.objects.filter(status=int(status)).count())
        statusCodeHits.append(temp)

    statusCodeHits = sorted(statusCodeHits, key=lambda x: x['hits'], reverse=True)

    data = {
        "statuscodehits": statusCodeHits,
    }
    return JsonResponse(data)

def error_graph(request):
    dbdata = error_logs.objects.all().values()
    message = dbdata.distinct('message')
    label_data = [data['message'] for data in message]
    count = [dbdata.filter(message = _).count() for _ in label_data]

    data = {
        'label': label_data,
        'count' : count
    }
    return JsonResponse(data)


def statuscodeips(request, statuscode):
    data = {}

    # Get the count of each status codes in the log
    try:
        statuscodeips = []
        ips = LogsHolder.objects.filter(status=statuscode).values('remoteAddr').distinct()
        for ip in ips:
            temp = {}
            temp['ip'] = str(ip['remoteAddr'])
            temp['count'] = LogsHolder.objects.filter(status=statuscode, remoteAddr=str(ip['remoteAddr'])).count()
            statuscodeips.append(temp)

        statuscodeips = sorted(statuscodeips, key=lambda x: x['count'], reverse=True)
    except:
        statuscodeips = "Not Found"

    data = {
        "statuscodeips": statuscodeips,
    }
    return JsonResponse(data)


def statuscodepercent(request):
    data = {}

    # To retrive all the status codes present in the log
    statusList = []
    statusCode = LogsHolder.objects.values('status').distinct()
    for status in statusCode:
        statusList.append(status['status'])

    # Get the percent of each status codes in the log
    statusCodePercent = []
    totalHits = 0
    for status in statusList:
        temp = {}
        temp['status'] = int(status)
        temp['percent'] = float(LogsHolder.objects.filter(status=int(status)).count())
        totalHits += temp['percent']
        statusCodePercent.append(temp)

    for status in statusCodePercent:
        status['percent'] = round((status['percent'] / totalHits) * 100, 2)

    statusCodePercent = sorted(statusCodePercent, key=lambda x: x['percent'], reverse=True)

    # Format the result by 200, 404, others
    payload = {
        'success': [],
        'error': [],
        'servererror': [],
        'others': []
    }
    # impTotal = 0
    valueSuccess = 0
    valueError = 0
    valueServerError = 0
    othersTotal = 0

    for status in statusCodePercent:
        if status['status'] in range(200, 400):
            payload['success'].append(status)
            valueSuccess += float(status['percent'])
        elif status['status'] in range(400, 500):
            payload['error'].append(status)
            valueError += float(status['percent'])
        elif status['status'] in range(500, 600):
            payload['servererror'].append(status)
            valueServerError += float(status['percent'])
        else:
            payload['others'].append(status)
            othersTotal += float(status['percent'])

    # payload['othersTotal'] = round(100 - impTotal, 2)
    payload['valueSuccess'] = valueSuccess
    payload['valueError'] = valueError
    payload['valueServerError'] = valueServerError
    payload['valueOthers'] = othersTotal

    data = {
        "statuscodepercent": payload,
    }
    return JsonResponse(data)


# Return the Unique API hits
def apihits(request, offset):
    data = {}

    # To retrive all the apis present in the log
    apisList = []
    apis = LogsHolder.objects.values('request').distinct()
    for api in apis:
        try:
            apistr = api['request'].split(" ")[1]
            if apistr not in apisList:
                apisList.append(apistr)
        except:
            pass

    # Get the percent of each status codes in the log
    apihits = []
    for api in apisList:
        temp = {}
        temp['request'] = str(api)
        temp['hits'] = int(LogsHolder.objects.filter(request__contains=str(api)).count())
        apihits.append(temp)

    apihits = sorted(apihits, key=lambda x: x['hits'], reverse=True)

    # Limit the results
    apihits = apihits[offset:][:10]

    data = {
        "apihits": apihits
    }
    return JsonResponse(data)


def unauthorizedips(request, offset):
    data = {}

    # Get the ips of unauthorizedips
    unauthorizedipsList = []
    unauthorizedips = LogsHolder.objects.filter(authorizedUser=False).values('remoteAddr')
    for ip in unauthorizedips:
        if str(ip['remoteAddr']) not in unauthorizedipsList:
            unauthorizedipsList.append(str(ip['remoteAddr']))

    # Get the count and the ipaddress
    payload = []
    for ip in unauthorizedipsList:
        temp = {}
        temp['hits'] = int(LogsHolder.objects.filter(remoteAddr=ip).count())
        temp['ip'] = ip
        payload.append(temp)

    # Sort the list according to the hits
    payload = sorted(payload, key=lambda x: x['hits'], reverse=True)

    # Return according to the offset
    payload = payload[int(offset):][:10]

    data = {
        "unauthorizedips": payload,
    }

    return JsonResponse(data)


def authorizedips(request, offset):
    data = {}

    # Get the ips of unauthorizedips
    authorizedipsList = []
    authorizedips = LogsHolder.objects.filter(authorizedUser=True).values('remoteAddr')
    for ip in authorizedips:
        if str(ip['remoteAddr']) not in authorizedipsList:
            authorizedipsList.append(str(ip['remoteAddr']))

    # Get the count and the ipaddress
    payload = []
    for ip in authorizedipsList:
        temp = {}
        temp['hits'] = int(LogsHolder.objects.filter(remoteAddr=ip).count())
        temp['ip'] = ip
        payload.append(temp)

    # Sort the list according to the hits
    payload = sorted(payload, key=lambda x: x['hits'], reverse=True)

    # Return according to the offset
    payload = payload[int(offset):][:10]

    data = {
        "authorizedips": payload,
    }

    return JsonResponse(data)


def hitcounts(request):
    data = {}

    # Get this month's hitcount
    year = datetime.today().year
    month = datetime.today().month
    _, numDays = calendar.monthrange(year, month)
    firstDay = datetime(year, month, 1)
    lastDay = datetime(year, month, numDays)
    lastDay = lastDay.replace(hour=23, minute=59, second=59)
    hitcountsMonth = LogsHolder.objects.filter(timeLocal__range=(firstDay, lastDay)).count()

    # Get today's hitcount
    today = datetime.today()
    todayStart = today.replace(hour=00, minute=00, second=00)
    todayEnd = today.replace(hour=23, minute=59, second=59)
    hitcountsToday = LogsHolder.objects.filter(timeLocal__range=(todayStart, todayEnd)).count()

    # Overall hitcount
    hitcountsOverall = LogsHolder.objects.all().count()

    data = {
        "hitcounts": {
            "today": int(hitcountsToday),
            "month": int(hitcountsMonth),
            "overall": int(hitcountsOverall)
        }
    }

    return JsonResponse(data)


def linegraphhits(request, period):
    data = {}

    if period == "year":
        # Get the start and end day as datetime object of every month
        currentYear = datetime.today().year
        noOfDaysInMonthList = []
        if calendar.isleap(currentYear):
            noOfDaysInMonthList = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            noOfDaysInMonthList = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        # hitlist400 to get the hit count in current year
        hitlist404 = []
        hitlist200 = []
        hitlistOthers = []
        hitlistTotal = []
        for idx, last in enumerate(noOfDaysInMonthList):
            firstDay = datetime.today().replace(month=int(idx + 1), day=(1), hour=0, minute=0, second=0)
            lastDay = datetime.today().replace(month=int(idx + 1), day=(last), hour=23, minute=59, second=59)
            count404 = int(LogsHolder.objects.filter(status=str(404), timeLocal__range=(firstDay, lastDay)).count())
            count200 = int(LogsHolder.objects.filter(status=str(200), timeLocal__range=(firstDay, lastDay)).count())
            countOthers = int(
                int(LogsHolder.objects.filter(timeLocal__range=(firstDay, lastDay)).count()) - (count200 + count404))
            hitlist404.append(count404)
            hitlist200.append(count200)
            hitlistOthers.append(countOthers)
            hitlistTotal.append(count200 + count404 + countOthers)

        data = {
            "linegraphhits": [
                {
                    "label": "Total Hits",
                    "borderColor": "rgba(0,0,0)",
                    "backgroundColor": "rgba(0,0,0,0.1)",
                    "data": hitlistTotal
                },
                {
                    "label": "Status code 200",
                    "borderColor": "rgba(124,252,0)",
                    "backgroundColor": "rgba(124,252,0,0.1)",
                    "data": hitlist200
                },
                {
                    "label": "Status Code 404",
                    "borderColor": "rgba(255,0,0)",
                    "backgroundColor": "rgba(255,0,0,0.1)",
                    "data": hitlist404
                },
                {
                    "label": "Other Status Codes",
                    "borderColor": "rgba(255,255,0)",
                    "backgroundColor": "rgba(255,255,0,0.1)",
                    "data": hitlistOthers
                }
            ]
        }

    elif period == "week":

        today = datetime.today()

        # Hitlist to get in the current month
        hitlist404 = []
        hitlist200 = []
        hitlistOthers = []
        hitlistTotal = []
        labels = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=int(i))
            labels.append(day.date())
            datStart = day.replace(hour=0, minute=0, second=0)
            dayEnd = day.replace(hour=23, minute=59, second=59)
            count404 = int(LogsHolder.objects.filter(status=str(404), timeLocal__range=(datStart, dayEnd)).count())
            count200 = int(LogsHolder.objects.filter(status=str(200), timeLocal__range=(datStart, dayEnd)).count())
            countOthers = int(
                int(LogsHolder.objects.filter(timeLocal__range=(datStart, dayEnd)).count()) - (count200 + count404))
            hitlist404.append(count404)
            hitlist200.append(count200)
            hitlistOthers.append(countOthers)
            hitlistTotal.append(count200 + count404 + countOthers)

        data = {
            "linegraphhits": [
                {
                    "label": "Total Hits",
                    "borderColor": "rgba(0,0,0)",
                    "backgroundColor": "rgba(0,0,0,0.1)",
                    "data": hitlistTotal
                },
                {
                    "label": "Status code 200",
                    "borderColor": "rgba(124,252,0)",
                    "backgroundColor": "rgba(124,252,0,0.1)",
                    "data": hitlist200
                },
                {
                    "label": "Status Code 404",
                    "borderColor": "rgba(255,0,0)",
                    "backgroundColor": "rgba(255,0,0,0.1)",
                    "data": hitlist404
                },
                {
                    "label": "Other Status Codes",
                    "borderColor": "rgba(255,255,0)",
                    "backgroundColor": "rgba(255,255,0,0.1)",
                    "data": hitlistOthers
                }
            ],
            "labels": labels
        }

    return JsonResponse(data)


# def threatips(request):
#     data = {}
#     threats = {
#         "sql_server_shell_command_injection" : [],
#         "os_command_shell_injection" : [],
#         "remote_file_inclusion" : [],
#         "session_corruption" : [],
#         "broken_authentication" : [],
#         "insecure_object_refrence_intrusion" : [],
#         "script_inclusion_detection_xss_attack" : [],
#         "inclusion_of_img_tags" : [],
#         "shell_code_intrusion" : [],
#         "directory_traversal_attack" : [],
#     }
#     rulesPath = "./../logpro/api/rules/rules.conf"
#     rulesPath = os.path.abspath(rulesPath)

#     dbdata = LogsHolder.objects.all().values("request", "remoteAddr")
#     with open(rulesPath) as rules:
#         for dbdatum in dbdata:
#             z = str(dbdatum['request'])
#             for rule in rules:
#                 if re.findall(rule.split(":")[1], z):
#                     threats[rule.split(":")[0]].append(dbdatum['remoteAddr'])

#     data = {
#         "threatips": threats
#     }

#     return JsonResponse(data)

def threatips(request):
    start = datetime.today()
    data = {}
    # Extract and store the rules in a list from conf
    rulesPath = "./../logpro/api/rules/rules.conf"
    rulesPath = os.path.abspath(rulesPath)
    allRules = []
    with open(rulesPath) as rules:
        for rule in rules:
            try:
                allRules.append(rule.strip())
            except:
                allRules = rule.strip()
    payload = []
    distinctIps = LogsHolder.objects.all().values("remoteAddr").distinct("remoteAddr")

    dictPayload = {}
    for distinctIp in distinctIps:
        print(distinctIp["remoteAddr"])
        specificRequests = LogsHolder.objects.filter(remoteAddr = distinctIp["remoteAddr"]).values("request", "status").distinct()
        for specificRequest in specificRequests:
            for rule in allRules:
                print(str((config(str(rule).strip()))))
                if re.findall(str((config(str(rule).strip()))), str(specificRequest["request"])):
                    try:
                        if dictPayload[distinctIp['remoteAddr']]:
                            dictPayload[distinctIp["remoteAddr"]]['count'] += 1
                            if dictPayload[distinctIp["remoteAddr"]]['attacked'] == False:
                                temp["attacked"] = True if LogsHolder.objects.filter(remoteAddr = distinctIp["remoteAddr"], request = specificRequest["request"], status = "200").count() else False
                    except:
                        temp = {}
                        temp["ip"] = distinctIp['remoteAddr']
                        temp["threat"] = str(rule)
                        temp["count"] = LogsHolder.objects.filter(remoteAddr = distinctIp["remoteAddr"], request = str(specificRequest["request"])).count()
                        temp["attacked"] = True if LogsHolder.objects.filter(remoteAddr = distinctIp["remoteAddr"], request = specificRequest["request"], status = "200").count() else False
                        dictPayload[distinctIp["remoteAddr"]] = temp

    for v in dictPayload.values():
        payload.append(v)

    # Sort according to the number of counts
    payload.sort(key = lambda x:x['count'], reverse = True)

    print(datetime.now() - start)

    data = {
        "threatips":payload
    }

    return JsonResponse(data)


def heatmaplocations(request):
    geoip2 = GeoIP2()
    data = {}
    latitude = []
    longitude = []
    result_dict = []

    data = LogsHolder.objects.all().values("remoteAddr")

    for datum in data:
        lat, lng = geoip2.lat_lon(datum['remoteAddr'])
        latitude.append(lat)
        longitude.append(lng)

    df = pd.DataFrame({'latitude': latitude, 'longitude': longitude})
    result = df.groupby(['latitude', 'longitude']).size().reset_index()

    for index, row in result.iterrows():
        content = {
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'count': row[0]

        }
        result_dict.append(content)

    data = {
        "heatmaplocations": result_dict,
    }

    return JsonResponse(data)


def statuscodecsv(request, category):
    data = {}
    statuscodecsv = []
    if category == 1:
        statusCodes = LogsHolder.objects.values("status").distinct()
        statuscodecsv.append(["IP Addresses"])
        successStatusCodes = []
        noOfSuccessStatusCodes = 0
        # Find the different success status codes and prepare the header for the csv implementation
        for statusCode in statusCodes:
            if 200 <= int(statusCode["status"]) < 400:
                noOfSuccessStatusCodes += 1
                successStatusCodes.append(int(statusCode["status"]))
                statuscodecsv[0].append("Status Code " + str(statusCode["status"]) + " Hit Counts")
        statuscodecsv[0].append("Total Hits")
        # Get the success ips for any of the given statuscodes and then append the counts for each status code
        successIps = LogsHolder.objects.filter(
            reduce(lambda x, y: x | y, [Q(status=status) for status in successStatusCodes])).values(
            "remoteAddr").distinct()
        for successIp in successIps:
            temp = []
            ip = successIp['remoteAddr']
            temp.append(ip)
            total = 0
            for successStatusCode in successStatusCodes:
                count = LogsHolder.objects.filter(remoteAddr=ip, status=successStatusCode).count()
                total += count
                temp.append(str(count))
            temp.append(str(total))
            statuscodecsv.append(temp)

        statuscodecsv[1:] = (sorted(statuscodecsv[1:], key=lambda x: int(x[noOfSuccessStatusCodes + 1]), reverse=True))


    elif category == 2:
        statusCodes = LogsHolder.objects.values("status").distinct()
        statuscodecsv.append(["IP Addresses"])
        errorStatusCodes = []
        noOferrorStatusCodes = 0
        # Find the different error status codes and prepare the header for the csv implementation
        for statusCode in statusCodes:
            if 400 <= int(statusCode["status"]) < 500:
                noOferrorStatusCodes += 1
                errorStatusCodes.append(int(statusCode["status"]))
                statuscodecsv[0].append("Status Code " + str(statusCode["status"]) + " Hit Counts")
        statuscodecsv[0].append("Total Hits")
        # Get the error ips for any of the given statuscodes and then append the counts for each status code
        errorIps = LogsHolder.objects.filter(
            reduce(lambda x, y: x | y, [Q(status=status) for status in errorStatusCodes])).values(
            "remoteAddr").distinct()
        for errorIp in errorIps:
            temp = []
            ip = errorIp['remoteAddr']
            temp.append(ip)
            total = 0
            for errorStatusCode in errorStatusCodes:
                count = LogsHolder.objects.filter(remoteAddr=ip, status=errorStatusCode).count()
                total += count
                temp.append(str(count))
            temp.append(str(total))
            statuscodecsv.append(temp)

        statuscodecsv[1:] = (sorted(statuscodecsv[1:], key=lambda x: int(x[noOferrorStatusCodes + 1]), reverse=True))

    elif category == 3:
        statusCodes = LogsHolder.objects.values("status").distinct()
        statuscodecsv.append(["IP Addresses"])
        serverErrorStatusCodes = []
        noOfserverErrorStatusCodes = 0
        # Find the different serverError status codes and prepare the header for the csv implementation
        for statusCode in statusCodes:
            if int(statusCode["status"]) >= 500:
                noOfserverErrorStatusCodes += 1
                serverErrorStatusCodes.append(int(statusCode["status"]))
                statuscodecsv[0].append("Status Code " + str(statusCode["status"]) + " Hit Counts")
        statuscodecsv[0].append("Total Hits")
        # Get the serverError ips for any of the given statuscodes and then append the counts for each status code
        serverErrorIps = LogsHolder.objects.filter(
            reduce(lambda x, y: x | y, [Q(status=status) for status in serverErrorStatusCodes])).values(
            "remoteAddr").distinct()
        for serverErrorIp in serverErrorIps:
            temp = []
            ip = serverErrorIp['remoteAddr']
            temp.append(ip)
            total = 0
            for serverErrorStatusCode in serverErrorStatusCodes:
                count = LogsHolder.objects.filter(remoteAddr=ip, status=serverErrorStatusCode).count()
                total += count
                temp.append(str(count))
            temp.append(str(total))
            statuscodecsv.append(temp)

        statuscodecsv[1:] = (
            sorted(statuscodecsv[1:], key=lambda x: int(x[noOfserverErrorStatusCodes + 1]), reverse=True))

    data = {
        "statuscodecsv": statuscodecsv
    }

    return JsonResponse(data)


def findlocation(request, location):
    geoip2 = GeoIP2()
    try:
        info = geoip2.city(str(location))

        city = info['city']
        continent = info['continent_name']
        country = info['country_name']

        data = {
            'city': city,
            'country': country,
            'continent': continent

        }
    except:
        data = {
            'city': 'Cannot find city',
            'country': 'Cannot find city',
            'continent': 'Cannot find city'
        }
    return JsonResponse(data)


def graphAreaData(request):
    data = {}

    # Get the start and end day as datetime object of every month
    currentYear = datetime.today().year
    noOfDaysInMonthList = []
    if calendar.isleap(currentYear):
        noOfDaysInMonthList = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        noOfDaysInMonthList = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # hitlist400 to get the hit count in current year
    MBFACTOR = float(1 << 20)
    monthBandwidth = []
    daily = []
    for idx, last in enumerate(noOfDaysInMonthList):
        firstDay = datetime.today().replace(month=int(idx + 1), day=(1), hour=0, minute=0, second=0)
        lastDay = datetime.today().replace(month=int(idx + 1), day=(last), hour=23, minute=59, second=59)
        bandwidth = LogsHolder.objects.filter(timeLocal__range=(firstDay, lastDay)).values("bodyBytesSent")
        bandwidthSum = sum([(lambda x: int(x['bodyBytesSent']))(x) for x in bandwidth])
        monthBandwidth.append(round(bandwidthSum / MBFACTOR, 2))

    hourBandwidth = []
    for i in range(24):
        firstTime = datetime.today().replace(hour=int(i), minute=0, second=0)
        lastTime = datetime.today().replace(hour=int(i), minute=59, second=59)
        bandwidth = LogsHolder.objects.filter(timeLocal__range=(firstTime, lastTime)).values("bodyBytesSent")
        bandwidthSum = sum([(lambda x: int(x['bodyBytesSent']))(x) for x in bandwidth])
        hourBandwidth.append(round(bandwidthSum / MBFACTOR, 2))

    data = daily_bandwidth.objects.all()
    for _ in data:
        daily.append(_.bandwidth)

    data = {
        "graphAreaData": {
            "monthlyBandwidthGraph": monthBandwidth,
            "hourlyBandwidthGraph": hourBandwidth,
            "daily": daily
        }
    }

    return JsonResponse(data)


def tableAreaData(request):
    data = {}

    highestBandwidthIpTable = []
    ipsList = []
    bandwidthIpTable = []
    MBFACTOR = float(1 << 20)

    ips = LogsHolder.objects.all().values("remoteAddr").distinct()
    for ip in ips:
        ipsList.append(ip['remoteAddr'])

    for ip in ipsList:
        bandwidthList = LogsHolder.objects.filter(remoteAddr=str(ip)).values("bodyBytesSent")
        bandwidthSum = sum([(lambda x: int(x['bodyBytesSent']))(x) for x in bandwidthList])
        bandwidthIpTable.append({
            "ipaddress": str(ip),
            "bandwidthSum": str(round(bandwidthSum / MBFACTOR, 2))
        })

    bandwidthIpTable.sort(key=lambda x: float(x["bandwidthSum"]), reverse=True)
    highestBandwidthIpTable = bandwidthIpTable[:10]

    data = {
        "tableAreaData": {
            "highestBandwidthIpTable": highestBandwidthIpTable,
            # "highestBandwidthIpTabl2e": apisList,

        }
    }

    return JsonResponse(data)


def errorlog(request, ip, req, time, date):
    req ="GET%20%2Fstatic%2Fvendor%2Fbootstrap%2Fjs%2Fpopper.js.map%20HTTP%2F1.1"
    req = '"' + unquote(req) + '"'
    print(req)
    print(ip,time,date)
    time= "23:06:45"
    date ="2019-06-17"
    ip ="49.205.222.133"
    distinctIps = error_logs.objects.filter(time=time, date=date, client=ip, request=req).values()

    data = {}
    for _ in distinctIps:
        data = _
    print(data)
    return JsonResponse(data)


def webrobots(request):
    bot_visitor = []
    dbdata = LogsHolder.objects.all().values("remoteAddr", "httpUserAgent").distinct('remoteAddr')
    rulesPath = "./../logpro/api/rules/bots.conf"
    rulesPath = os.path.abspath(rulesPath)
    count = 0
    with open(rulesPath) as rules:
        bot_name = [rule.strip() for rule in rules]
    for dbdatum in dbdata:
        for _ in bot_name:

            if re.findall(str((config(str(_)))), str(dbdatum['httpUserAgent'])):
                count += 1
                bot_visitor.append({'ip': dbdatum['remoteAddr'], 'useragent': dbdatum['httpUserAgent'], 'botname': _})

    data = {
        'count': count,
        'robots': bot_visitor
    }
    return JsonResponse(data)