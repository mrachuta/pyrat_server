## Project name
pyrat - python remote acess tool - server app.

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Using](#using)
* [Thanks](#thanks)

## General info
During business trip, IT-Helpdesk (from my company) helped me to install some software on my business laptop (I have no admin permissions).  
I wondered, how this is possible, that they still can connect to my PC, even if I was behind two NAT's.   
The port 80 was the key.

This tool was created for training purposes only, never was and will be used as unwanted software (there is no hidding, autostart of script etc).

Main goals for server:

a) simple, lightweight code (still in progress :))))),  
b) more work should be performed on server side than on client side,  
c) keeping data encoded, during transfering via port 80,  
d) very simple visual layer, with useful JS code.

If you will ask why Django was used without models (pure SQL queries - maybe for someone no sense): author started learning Django from totally wrong side.
Models should be implemented for more flexible code and typical Django functional. Unfortunatelly, 
the power of Models was first seen at finish of development of this app. Maybe in next versions Models will be implemented.

## Technologies
* Backend: Python3,
* Frontend: HTML,
* Scripts: JavaScript and JQuery library,
* Database: PostgreSQL

Code was tested on following platforms:
* Windows 8.1 (PL-PL) (x64) with Python 3.7.1
* Windows 8.1 (EN-US) (x64) with Python 3.6.4
* Ubuntu 16.04.1 LTS (GNU/Linux 2.6.32-openvz-042stab125.5-amd64 x86_64) with Python 3.5.2

Used libraries:
Package and version  
* certifi         2018.4.16
* chardet         3.0.4    
* Django          2.0.6    
* django-freshly  0.1.2    
* idna            2.7      
* pip             18.0     
* psycopg2        2.7.4    
* psycopg2-binary 2.7.4    
* pytz            2018.4   
* requests        2.19.1   
* setuptools      40.2.0   
* urllib3         1.23     
* uWSGI           2.0.17   
* wheel           0.31.1   

## Setup

1. Set free database for example on https://elephantsql.com/ with table *users2* contains following structure:


| num | name          | typ                  | notnull | comment | primary_key |
|-----|---------------|----------------------|---------|---------|-------------|
| 1   | id            | integer              | true    | null    | true        |
| 2   | det_mac       | text                 | true    | null    | false       |
| 3   | det_os        | text                 | true    | null    | false       |
| 4   | det_name      | text                 | true    | null    | false       |
| 5   | det_int_ip    | text                 | true    | null    | false       |
| 6   | det_ext_ip    | text                 | true    | null    | false       |
| 7   | uniqueid      | character varying(6) | false   | null    | false       |
| 8   | command       | text                 | false   | null    | false       |
| 9   | result        | text                 | false   | null    | false       |
| 10  | last_activity | text                 | false   | null    | false       |
| 11  | la_diff       | text                 | false   | null    | false       |
| 12  | files         | text                 | false   | null    | false       |

2. Install required packages.
3. Create file *secrets* in the same directory as settings.py, with following data (without < and >):
```
<secret_key>
<database_name>
<database_user>
<database_password>
<database_host>
```
This is suficient to set Django developer server.  
If you will try to set server as production enviroment, uWSGI is recommended.

## Using

To run:

```
python manage.py runserver
```

And open in browser following adress:
```
http://127.0.0.1:8000/index/
```

Information how to use app, is available in index page - button "CLICK FOR HELP"  
Don't forget to connect at least one client, to check how whole enviroment works:  
https://github.com/mrachuta/pyrat_client

## Thanks

Thanks to my girlfriend for her patience when I was coding.  
Of course a lot of thanks to all users from Stackoverflow, whose source codes helped me in my project.
