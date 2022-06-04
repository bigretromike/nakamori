# -*- coding: utf-8 -*-

from sqlite3 import dbapi2 as database
import os.path
import time
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
from lib.kodi_utils import debug

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
    _db_cursor.execute('CREATE TABLE IF NOT EXISTS [cache] ([url] TEXT unique, [data] BLOB NULL, [created] FLOAT);')
    _db_cursor.execute('CREATE TABLE IF NOT EXISTS [last] ([id] INTEGER unique, [url] TEXT);')
    _db_cursor.execute('INSERT INTO last (id, url) VALUES (1, "");')
    _db_connection.commit()
except:
    pass

# close connection
_db_connection.close()


def get_last():
    items = None
    try:
        db_connection = database.connect(db_file)
        db_cursor = db_connection.cursor()
        db_cursor.execute('SELECT url FROM last WHERE id=1')
        items = db_cursor.fetchone()[0]
    except:
        pass
    return items


def set_last(url: str):
    db_connection = database.connect(db_file)
    db_cursor = db_connection.cursor()
    db_cursor.execute('UPDATE last set url = ? where id = 1', (url, ))
    db_connection.commit()
    db_connection.close()


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
        db_cursor.execute('SELECT url, data, created FROM cache')
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
        db_cursor.execute('SELECT data, created FROM cache WHERE url=?', (url,))
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
    if '/watch' not in url:
        date = time.time()
        db_connection = database.connect(db_file)
        db_cursor = db_connection.cursor()
        db_cursor.execute('INSERT INTO cache (url, data, created) VALUES (?, ?, ?)', (url, json_body, date))
        db_connection.commit()
        db_connection.close()
        if '/api/ep' not in url:
            set_last(url)


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


def try_cache(url_in):
    debug(f'=== cache lookup: {url_in} ===')
    db_row = get_data_from_cache(url_in)
    if db_row is not None:
        valid_until = int(addon.getSetting('expireCache'))
        expire_second = time.time() - float(db_row[1])
        debug(f'=== is cache expiring: {expire_second} > {valid_until} ===')
        if expire_second > valid_until:
            # expire, get new date
            remove_cache(url_in)
            return False, None
        else:
            return True, db_row[0]
    return False, None
