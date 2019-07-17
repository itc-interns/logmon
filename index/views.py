from django.shortcuts import render, redirect
from dashboard.models import LogsHolder,error_logs
from .models import daily_bandwidth
import pandas as pd
import re
import glob
from xopen import xopen
import shutil
import os
import time
from datetime import datetime

# Create your views here.
def index(request):
    flag = 0
    if request.method == 'POST':
        request.session['source'] = request.POST.get('source')
        source =request.POST.get('source')
        print(request.session.get('source'))
        if os.path.exists(str(request.session.get('source'))):
            flag = 0
            start_time = time.time()
            # Insert data from log into database
            source_dir = request.session['source']
            if os.path.exists(source_dir):
                files = glob.iglob(os.path.join(source_dir, "access.log.*.gz"))

                for i in files:
                    with xopen(i, 'rb') as f_in:
                        with open(i + '.log', 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
            else:
                print("IOError: [Errno 2] No such file or directory: '" + source_dir + "'")

            hourly = {'00': 0, '01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0,
                      '11': 0, '12': 0, '13': 0, '14': 0, '15': 0, '16': 0, '17': 0, '18': 0, '19': 0, '20': 0, '21': 0,
                      '22': 0, '23': 0}
            tangent = 0
            conf = '$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"'
            regex = ''.join(
                '(?P<' + g + '>.*?)' if g else re.escape(c)
                for g, c in re.findall(r'\$(\w+)|(.)', conf))
                
            files = glob.iglob(os.path.join(source_dir, "access.log.*.gz.log"))

            for filepath in files:

                raw_data = open(filepath, "r", encoding="utf8")
                authorizedusers = []
                
                for idx, i in enumerate(raw_data):
                    m = re.match(regex, i)

                    #Find the authorized users
                    authorized = re.findall('(.*\d) - - .*POST.*200 \d{1,}', i)
                    if len(authorized):
                        authorizedip = str(authorized[0])
                        if authorizedip not in authorizedusers:
                            authorizedusers.append(authorizedip)
                
                # Temp Area
                
                # print(authorizedusers)
                # temp = LogsHolder.objects.filter(authorizedUser = True).distinct()
                # for i in temp:
                #     if i.remoteAddr in authorizedusers:
                #         print("True")

                # Temp Area

                    payload = m.groupdict()
                    # 'daily bandwidth



                    print(hourly)
                    data = LogsHolder()
                    data.remoteAddr = payload['remote_addr']
                    data.remoteUser = payload['remote_user']   
                    
                    # Convert time in logformat to time in python datetime format and store it in db
                    timeLocalstr = str(payload['time_local'])
                    timeLocal = datetime.strptime(timeLocalstr, '%d/%b/%Y:%H:%M:%S %z')
                    timeLocal = timeLocal.replace(tzinfo = None)
                    data.timeLocal = timeLocal        

                    data.request = payload['request']
                    data.status = payload['status']
                    data.bodyBytesSent = payload['body_bytes_sent']
                    data.httpReferer = payload['http_referer']
                    data.httpUserAgent = payload['http_user_agent']
                    
                    # Check and add the authorized column value
                    if str(payload['remote_addr']) in authorizedusers:
                        data.authorizedUser = True
                    else:
                        data.authorizedUser = False
                    
                    if(LogsHolder.objects.filter(remoteAddr = payload['remote_addr'], remoteUser = payload['remote_user'], timeLocal = timeLocal, request = payload['request'], status = payload['status'], bodyBytesSent = payload['body_bytes_sent'], httpReferer = payload['http_referer'], httpUserAgent = payload['http_user_agent']).count() == 0):
                        data.save()
                        tangent = 1
                        hourly[payload['time_local'].split(":")[1]] += int(payload['body_bytes_sent'])

            # ' error log storing in db'
            conf = "$date $time [$level] $pid#$tid: '$message'"
            regex = ''.join(
                '(?P<' + g + '>.*?)' if g else re.escape(c)
                for g, c in re.findall(r'\$(\w+)|(.)', conf))

            files = glob.iglob(os.path.join(source_dir, "error.log"))

            for filepath in files:

                raw_data = open(filepath, "r", encoding="utf8")
                for idx, i in enumerate(raw_data):
                    m = re.match(regex, i)
                    errorlog = m.groupdict()
                    data = error_logs()
                    data.date = errorlog['date'].replace('/','-')
                    data.time = errorlog['time']
                    data.level = errorlog['level']
                    data.pid = errorlog['pid']
                    data.tid = errorlog['tid']
                    try:
                        data.message = errorlog['message'].split(",")[0]
                        data.client = errorlog['message'].split(",")[1].split(":")[1].strip()
                        data.request = errorlog['message'].split(",")[3].split(":")[1].strip()
                    except:
                        data.message =errorlog['message']
                        data.client = "-"
                        data.request = "-"
                    data.save()


                if tangent:
                    if daily_bandwidth.objects.all().count() == 0:
                        for k, v in hourly.items():
                            data = daily_bandwidth()
                            data.day = k
                            data.bandwidth = v
                            data.save()
                    else:
                        data = daily_bandwidth.objects.all()

                        for _ in data:
                            print(hourly[_.day])
                            hourly[_.day] = int(hourly[_.day]) + int(_.bandwidth)

                        for k, v in hourly.items():
                            data = daily_bandwidth()
                            data.day = k
                            data.bandwidth = v
                            data.save()
            print("----%s seconds ----" % (time.time() - start_time))
            return redirect('dashboard')
        else:
            print("lolbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbiiiiiiiiiiiiiiiiiiii")
            flag = 1
            # return redirect('')
    return render(request, "index/index.html", {'flag': flag})