#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

import os.path
import time
import json
import sys

import xbmc
import xbmcaddon
import xbmcgui


def decode_utf8(_string):
    if sys.version_info < (3, 0):
        return _string.decode('utf-8')
    else:
        return _string


ADDON_ID='plugin.video.nakamori'
addon = xbmcaddon.Addon(id=ADDON_ID)
profileDir = addon.getAddonInfo('profile')
profileDir = decode_utf8(xbmc.translatePath(profileDir))

# create profile dirs
if not os.path.exists(profileDir):
    os.makedirs(profileDir)

db_file = os.path.join(profileDir, 'cache.db')

# connect to db
db_connection = database.connect(db_file)
db_cursor = db_connection.cursor()

# create table
try:
    db_cursor.execute("CREATE TABLE IF NOT EXISTS [cache] ([url] TEXT NULL, [json] TEXT NULL, [created] FLOAT NULL);")
except:
    pass

# close connection
db_connection.close()


def get_cached_data():
    """
    Search for Search History inside db
    :return: list of used search terms
    """
    items=[]
    try:
        db_connection = database.connect(db_file)
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT url, json, created FROM cache")
        faves = db_cursor.fetchall()
        for a_row in faves:
            if len(a_row) > 0:
                items.append(a_row)
    except:
        pass

    db_connection.close()
    return items


def get_data_from_cache(url):
    items = ''
    url = str(url)
    try:
        db_connection = database.connect(db_file)
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT json FROM cache WHERE url=?", (url,))
        items = db_cursor.fetchone()
        items = json.loads(items[0])
    except:
        pass
    return items


def add_cache(url, json):
    """
    Add 'url' with 'json'
    :param url: url you want to cache
    :param json: json respond
    :return:
    """
    date = time.time()
    db_connection = database.connect(db_file)
    db_cursor = db_connection.cursor()
    db_cursor.execute("INSERT INTO cache (url, json, created) VALUES (?, ?, ?)", (url, json, date))
    db_connection.commit()
    db_connection.close()


def remove_cache(params):
    """
    Remove single term from Search History
    :param params:
    :return:
    """
    db_connection = database.connect(db_file)
    db_cursor = db_connection.cursor()
    try:
        if params["extras"] == "single-delete":
            db_cursor.execute("DELETE FROM cache WHERE url=?", (params['name'],))
    except:
        db_cursor.execute("DELETE FROM cache")
    db_connection.commit()
    db_connection.close()


def check_in_database(term):
    """
    Check if 'term' is inside database
    :param term: string that you check for
    :return: True if exist in database, False if not
    """
    items = ''
    try:
        db_connection = database.connect(db_file)
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT created FROM cache WHERE url=?", (term,))
        items = db_cursor.fetchone()
        items = items[0]
    except:
        pass
    return items


def clear_cache(params):
    do_clean = xbmcgui.Dialog().yesno("Confirm Delete", "Are you sure you want to Clear CACHE?")
    if do_clean:
        remove_cache(params)
        xbmc.executebuiltin('Container.Refresh')
