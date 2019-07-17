# logmon
Logmon is a simple yet intuitive Django based server monitoring web application designed for server admins to get in and out report of the server through the log files, given as an input to the web app.
___
## Installation
Begin by installing `Python` and `pip` on your computer.

Using pip to install Pipenv and its dependencies,

    pip install pipenv

Create a virtual environment and install the dependencies with the given pipfile,

    pipenv install

After the installation go ahead and run this command to run the server,

    python manage.py runserver

or,

    python manage.py runserver [IP_ADDRESS]:[PORT]

___

## Usage
After running the server successfully, go to,

    localhost:[PORT]/index

![alt text][index]

Paste / Type your logs folder path in the input and submit,

Now you will be redirected to the dashboard page.

(or)

If you already done that, go to 

    localhost:[PORT]/dadshboard


![alt text][dashboard1]

You can download the CSV files for Success, Client Errors and Server Errors by clicking the respective gauges.

![alt text][dashboard16]

You can see the IP address heat map, generated on the basis of the access location.
You can search any IP using the search option provided in the heat map.

![alt text][dashboard15]

In Hits based graph, You can see the yearly and weekly hits counts of each status codes and total hits.

![alt text][dashboard17]

These are the  bar charts showing monthly and hourly bandwidth consumption.

![alt text][dashboard3]
![alt text][dashboard4]
![alt text][dashboard5]

A Chart is showing the error counts.

The table below is listing the top 10 IP that consumed high amount of bandwidths.

![alt text][dashboard7]

The left panel is clickable and if you click the status code tab, which will show the IP Addresses and count of them in that status code.

![alt text][dashboard9]

![alt text][dashboard10]

Hit count tab will show the following
* Total hit count
* Current month's hit count
* Today's hit Count

![alt text][dashboard11]

Users Tab will show the new users and already accessed users.

![alt text][dashboard12]

API hits will show the API and the number of hits.

![alt text][dashboard13]

Bots tab will show the total count of bots and bots IP and the Http User Agent that is used by the bot.

The following bots are identified by this project,


* APIs-Google
* AdSense-Google
* AdsBot-Google-Mobile
* AdsBot
* Googlebot-Images
* Googlebot-News
* Googlebot-video
* Googlebot
* Google_Bot_Smartphone
* Google-Mediapartners
* AdsBot-Google-Mobile-Apps
* FeedFetcher
* Google-Bot
* Google_Speaker
* Microsoft_Bot
* Microsoft_Bing
* Microsoft_Mobile
* Facebook_Bot
* Sogou_Web_Spider
* Baidu_Spider
* Proximic_Spider
* IPIP.NET-crawler


![alt text][dashboard14]

On the nav bar you can go to these pages,
* View all
* View all errors
* Threats

View all page will show all the details from the `access.log`.

![alt text][viewall]

You can search for anything from the viewall page, and also you can download the whole log by clicking Download as CSV button.

![alt text][viewallsearch]

View all error will show all the errors fetched from `error.log` file.

![alt text][viewallerrors]

Threats will show the threat name and IP's that tried and attacked.

The following threats can be identified by this project

* sql_injection
* sql_server_shell_command_injection
* remote_file_inclusion
* session_corruption
* broken_authentication
* insecure_object_refrence_intrusion
* script_inclusion_detection_xss_attack
* inclusion_of_img_tags
* directory_traversal_attack
* shellsock_vulnerability


![alt text][threats]


[index]: ./images/index.png "index page"
[threats]: ./images/threats.png
[viewall]: ./images/viewall.png
[viewallerrors]: ./images/viewallerrors.png
[viewallsearch]: ./images/viewallsearch.png
[dashboard1]: ./images/dashboard(1).png
[dashboard2]: ./images/dashboard(2).png
[dashboard3]: ./images/dashboard(3).png
[dashboard4]: ./images/dashboard(4).png
[dashboard5]: ./images/dashboard(5).png
[dashboard6]: ./images/dashboard(6).png
[dashboard7]: ./images/dashboard(7).png
[dashboard9]: ./images/dashboard(9).png
[dashboard10]: ./images/dashboard(10).png
[dashboard11]: ./images/dashboard(11).png
[dashboard12]: ./images/dashboard(12).png
[dashboard13]: ./images/dashboard(13).png
[dashboard14]: ./images/dashboard(14).png
[dashboard15]: ./images/dashboard(15).png
[dashboard16]: ./images/dashboard(16).png
[dashboard17]: ./images/dashboard(17).png

It is in development, for any quries contact:

Aakash Nilavan : `nilavanaakash@gmail.com`

Anish Tiwari : `tiwari1999anish@gmail.com`

Hesen Nivas : `hesennivas@gmail.com`
