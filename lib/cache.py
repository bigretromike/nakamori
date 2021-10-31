# -*- coding: utf-8 -*-

from sqlite3 import dbapi2 as database
import os.path
import time
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

addon = xbmcaddon.Addon('plugin.video.nakamori')
profileDir = addon.getAddonInfo('profile')
profileDir = xbmcvfs.translatePath(profileDir)

# create profile dirs
if not os.path.exists(profileDir):
    os.makedirs(profileDir)

db_file = os.path.join(profileDir, 'cache.db')

# connect to db
_db_connection = database.connect(db_file)
_db_cursor = _db_connection.cursor()

# create table
try:
    _db_cursor.execute('CREATE TABLE IF NOT EXISTS [cache] ([url] TEXT NULL, [json] TEXT NULL, [created] FLOAT NULL);')
except:
    pass

# close connection
_db_connection.close()


def get_cached_data():
    """
    Search for Search History inside db
    :return: list of used search terms
    """
    items = []
    db_connection = None
    try:
        db_connection = database.connect(db_file)
        db_cursor = db_connection.cursor()
        db_cursor.execute('SELECT url, json, created FROM cache')
        faves = db_cursor.fetchall()
        for a_row in faves:
            if len(a_row) > 0:
                items.append(a_row)
    except:
        pass

    db_connection.close()
    return items


def get_data_from_cache(url):
    items = None
    url = str(url)
    try:
        db_connection = database.connect(db_file)
        db_cursor = db_connection.cursor()
        db_cursor.execute('SELECT json, created FROM cache WHERE url=?', (url,))
        items = db_cursor.fetchone()
    except:
        pass
    return items


def add_cache(url, json_body):
    """
    Add 'url' with 'json'
    :param url: url you want to cache
    :param json_body: json respond
    :return:
    """
    date = time.time()
    db_connection = database.connect(db_file)
    db_cursor = db_connection.cursor()
    db_cursor.execute('INSERT INTO cache (url, json, created) VALUES (?, ?, ?)', (url, json_body, date))
    db_connection.commit()
    db_connection.close()


def remove_cache(url=None):
    """
    Remove single term from Search History
    :param url:
    :return:
    """
    db_connection = database.connect(db_file)
    db_cursor = db_connection.cursor()
    if url is not None:
        db_cursor.execute('DELETE FROM cache WHERE url=?', (url,))
    else:
        db_cursor.execute('DELETE FROM cache')
    db_connection.commit()
    db_connection.close()


def clear_cache(params):
    do_clean = xbmcgui.Dialog().yesno('Confirm Delete', 'Are you sure you want to Clear CACHE?')
    if do_clean:
        remove_cache(params)
        xbmc.executebuiltin('Container.Refresh')
