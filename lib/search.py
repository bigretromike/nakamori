# -*- coding: utf-8 -*-

from sqlite3 import dbapi2 as database
import os.path
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs


addon = xbmcaddon.Addon(id='plugin.video.nakamori')
profileDir = addon.getAddonInfo('profile')
profileDir = xbmcvfs.translatePath(profileDir)

# create profile dirs
if not os.path.exists(profileDir):
    os.makedirs(profileDir)

db_file = os.path.join(profileDir, 'search.db')

# connect to db
init_connection = database.connect(db_file)
init_cursor = init_connection.cursor()

# create table
try:
    init_cursor.execute('CREATE TABLE IF NOT EXISTS search (search_term TEXT, fuzzy INTEGER, tag INTEGER);')
except:
    pass

# close connection
init_connection.close()


def get_search_history():
    """
    Search for Search History inside db
    :return: list of used search terms
    """
    items = []
    db_connection = None
    try:
        db_connection = database.connect(db_file)
        db_cursor = db_connection.cursor()
        db_cursor.execute('SELECT search_term, fuzzy, tag FROM search ORDER BY ROWID DESC')
        faves = db_cursor.fetchall()
        for a_row in faves:
            items.append(a_row)
    except:
        pass
    finally:
        if db_connection is not None:
            db_connection.close()
    return items


def add_search_history(query: str, fuzzy: int, tag: int):
    """
    Add 'keyword' to Search History
    :param query: term to add to db
    :param fuzzy:
    :param tag:
    :return:
    """
    db_connection = database.connect(db_file)
    db_cursor = db_connection.cursor()
    db_cursor.execute('INSERT INTO search (search_term, fuzzy, tag) VALUES (?, ?, ?)', (query, fuzzy, tag))
    db_connection.commit()
    db_connection.close()


def remove_search_history(query: str, fuzzy: int, tag: int):
    """
    Remove single term from Search History
    :param query:
    :param fuzzy
    :param tag
    :return:
    """
    db_connection = database.connect(db_file)
    db_cursor = db_connection.cursor()

    if query is not None:
        db_cursor.execute('DELETE FROM search WHERE search_term=? and fuzzy=? and tag=?', (query, fuzzy, tag))
    else:
        db_cursor.execute('DELETE FROM search')

    db_connection.commit()
    db_connection.close()


def check_in_database(term: str, fuzzy: int, tag: int):
    """
    Check if 'term' is inside database
    :param term: string that you check for
    :param fuzzy:
    :param tag:
    :return: True if exist in database, False if not
    """
    db_connection = database.connect(db_file)
    db_cursor = db_connection.cursor()
    db_cursor.execute('SELECT Count(search_term) FROM search WHERE search_term=? and fuzzy=? and tag=?', (term, fuzzy, tag))
    data = db_cursor.fetchone()
    return data[0] > 0


def clear_search_history():
    do_clean = xbmcgui.Dialog().yesno('Confirm Delete', 'Are you sure you want to delete ALL search terms?')
    if do_clean:
        remove_search_history(None, 0, 0)
        xbmc.executebuiltin('Container.Refresh')
