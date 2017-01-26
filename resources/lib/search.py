#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

import os.path

import xbmc
import xbmcaddon

ADDON_ID='plugin.video.nakamori'
addon = xbmcaddon.Addon(id=ADDON_ID)
profileDir = addon.getAddonInfo('profile')
profileDir = xbmc.translatePath(profileDir).decode("utf-8")

# create profile dirs
if not os.path.exists(profileDir):
    os.makedirs(profileDir)

db_file = os.path.join(profileDir, 'search.db')

# connect to db
db_connection = database.connect(db_file)
db_cursor = db_connection.cursor()

# create table
try:
    db_cursor.execute("CREATE TABLE IF NOT EXISTS search (search_term);")
except:
    pass

# close connection
db_connection.close()


def get_search_history():
    """
    Search for Search History inside db
    :return: list of used search terms
    """
    items=[]
    try:
        db_connection = database.connect(db_file)
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT search_term FROM search")
        faves = db_cursor.fetchall()
        for a_row in faves:
            if len(a_row) > 0:
                items.append(a_row)
    except:
        pass
    
    db_connection.close()
    return items


def add_search_history(keyword):
    """
    Add 'keyword' to Search History
    :param keyword: term to add to db
    :return:
    """
    db_connection = database.connect(db_file)
    db_cursor = db_connection.cursor()
    db_cursor.execute("INSERT INTO search (search_term) VALUES (?)", (keyword,))
    db_connection.commit()
    db_connection.close()


def remove_search_history(params):
    """
    Remove single term from Search History
    :param params:
    :return:
    """
    db_connection = database.connect(db_file)
    db_cursor = db_connection.cursor()
    db_cursor.execute("DELETE FROM search WHERE search_term=?", (params['name'],))
    db_connection.commit()
    db_connection.close()


def check_in_database(term):
    """
    Check if 'term' is inside database
    :param term: string that you check for
    :return: True if exist in database, False if not
    """
    db_connection = database.connect(db_file)
    db_cursor = db_connection.cursor()
    db_cursor.execute("SELECT search_term FROM search WHERE search_term=?", (term,))
    data = db_cursor.fetchall()
    if len(data) == 0:
        return False
    return True
