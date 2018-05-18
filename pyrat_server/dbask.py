# -*- coding: utf-8 -*-


from django.db import connection, InterfaceError


def db_fetchall(query):
    try:
        dbquery = connection.cursor()
        dbquery.execute(query)
    except InterfaceError:
        dbquery.close()
        dbquery = connection.cursor()
        dbquery.execute(query)
    return dbquery.fetchall()


def db_fetchone(query):
    try:
        dbquery = connection.cursor()
        dbquery.execute(query)
    except InterfaceError:
        dbquery.close()
        dbquery = connection.cursor()
        dbquery.execute(query)
    return dbquery.fetchone()


def db_update(query):
    try:
        dbquery = connection.cursor()
        dbquery.execute(query)
    except InterfaceError:
        dbquery = connection.cursor()
        dbquery.execute(query)