#!python
# Copyright 2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""

Thanks to Maarek for first inspiration
http://forum.ubuntu-fr.org/viewtopic.php?id=415396

"""

from __future__ import print_function
from __future__ import unicode_literals


"""

sqlite_master : ['type', 'name', 'tbl_name', 'rootpage', 'sql']

- TagTable: 
  - name : name of the tag (e.g. "blog")
  - photo_id_list : comma-separated list of photo ids

CREATE TABLE PhotoTable (
id INTEGER PRIMARY KEY, 
filename TEXT UNIQUE NOT NULL, 
width INTEGER, 
height INTEGER, 
filesize INTEGER, 
timestamp INTEGER, 
exposure_time INTEGER, 
orientation INTEGER,
original_orientation INTEGER, 
import_id INTEGER, 
event_id INTEGER,
transformations TEXT, 
md5 TEXT, 
thumbnail_md5 TEXT, 
exif_md5 TEXT,
time_created INTEGER,
flags INTEGER DEFAULT 0,
rating INTEGER DEFAULT 0,
file_format INTEGER DEFAULT 0,
title TEXT,
backlinks TEXT,
time_reimported INTEGER,
editable_id INTEGER DEFAULT -1,
metadata_dirty INTEGER DEFAULT 0,
developer TEXT,
develop_shotwell_id INTEGER DEFAULT -1,
develop_camera_id INTEGER DEFAULT -1,
develop_embedded_id INTEGER DEFAULT -1,
comment TEXT)


CREATE TABLE VideoTable (id INTEGER PRIMARY KEY, filename TEXT UNIQUE
NOT NULL, width INTEGER, height INTEGER, clip_duration REAL,
is_interpretable INTEGER, filesize INTEGER, timestamp INTEGER,
exposure_time INTEGER, import_id INTEGER, event_id INTEGER, md5 TEXT,
time_created INTEGER, rating INTEGER DEFAULT 0, title TEXT, backlinks
TEXT, time_reimported INTEGER, flags INTEGER DEFAULT 0 , comment TEXT)

"""

import os
import shutil
import codecs
from os.path import expanduser
import sqlite3

from argh import dispatch_command, arg, CommandError


def chop(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]
    return s


def schema(conn, tableName):
    cursor = conn.cursor()
    sql = "SELECT sql FROM sqlite_master WHERE type='table' AND name='%s'"
    sql = sql % tableName
    print(sql)
    cursor.execute(sql)
    row = cursor.fetchone()
    return row['sql']


def show_tables(conn):
    cursor = conn.cursor()
    sql = "SELECT name FROM sqlite_master WHERE type='table'"
    print(sql)
    cursor.execute(sql)
    return [row['name'] for row in cursor.fetchall()]


def get_photos(conn, tags):
    cursor = conn.cursor()
    li = ','.join(["'{0}'".format(t) for t in tags])
    where = "name in ({0})".format(li)
    sql = "SELECT photo_id_list FROM TagTable WHERE {0}".format(where)
    # sql = "SELECT photo_id_list FROM TagTable WHERE name = '%s'" % tagname

    photo_ids = set()
    video_ids = set()

    cursor.execute(sql)
    for row in cursor:
        for photo_id in row[str("photo_id_list")].split(","):
            if photo_id:
                if photo_id.startswith('thumb'):
                    photo_id = int(photo_id[5:], 16)
                    photo_ids.add(photo_id)

                elif photo_id.startswith('video-'):
                    photo_id = int(photo_id[6:], 16)
                    video_ids.add(photo_id)
                else:
                    raise Exception("Invalid photo_id %r" % photo_id)

    if len(photo_ids):
        li = ','.join([str(i) for i in photo_ids])
        sql = "SELECT id, filename FROM PhotoTable WHERE id IN ({0})"
        sql = sql.format(li)
        sql += " ORDER BY exposure_time"
        cursor.execute(sql)
        for row in cursor:
            yield row[1]


RSTLINE = """.. sigal_image:: %s\n"""


@dispatch_command
@arg('tags', help="One ore more Shotwell tags. "
     "The listed pictures must have *at least* one of them.")
@arg('-t', '--target_root',
     help='Where to export tagged pictures and videos.')
@arg('-l', '--shotwell_lib',
     help='Your Shotwell library directory')
@arg('-d', '--shotwell_db',
     help='Your Shotwell database file')
def main(target_root=None,
         shotwell_lib=expanduser("~/Pictures/"),
         shotwell_db=expanduser("~/.local/share/shotwell/data/photo.db"),
         *tags):
    """Copy tagged photos and videos from shotwell photo database to a target
filesystem."""

    if target_root:
        if not os.path.exists(target_root):
            raise CommandError(
                "Target directory %s does not exist!" % target_root)

    conn = sqlite3.connect(shotwell_db)
    conn.row_factory = sqlite3.Row

    if False:  # I used this to discover the database structure.
        yield show_tables(conn)
        yield schema(conn, 'TagTable')
        yield schema(conn, 'PhotoTable')
        yield schema(conn, 'VideoTable')
        return

    if len(tags) == 0:
        raise CommandError("Must specify at least one tag!")

    targets = []
    for orig in get_photos(conn, tags):
        if target_root:
            target = chop(orig, shotwell_lib)
            target = target.lower()
            targets.append(target)
            target = os.path.join(target_root, target)
            if os.path.exists(target):
                yield "{0} exists".format(target)
            else:
                dn = os.path.dirname(target)
                if not os.path.exists(dn):
                    yield "{0} created".format(dn)
                    os.makedirs(dn)
                yield "{0} copied".format(target)
                shutil.copyfile(orig, target)
        else:
            yield orig

    conn.close()

    if target_root:
        targets.sort()
        fn = os.path.join(target_root, 'index.rst')
        rstfile = codecs.open(fn, "w", encoding="utf-8")
        for t in targets:
            rstfile.write(RSTLINE % t)
        rstfile.close()
