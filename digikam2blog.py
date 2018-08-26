#!python
# Copyright 2017 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""

Thanks to Maarek for first inspiration
http://forum.ubuntu-fr.org/viewtopic.php?id=415396

Change history:

- 2015-09-19 accept non-ascii tags
- 2015-12-04 new command-line options `before` and `after`

"""

from __future__ import print_function
#from __future__ import unicode_literals
import six
import os
from os.path import expanduser
import time
from time import mktime
from datetime import datetime
from dateutil import parser
from unipath import Path
import shutil
import codecs
import sqlite3

from argh import dispatch_command, arg, CommandError

"""

sqlite_master : ['type', 'name', 'tbl_name', 'rootpage', 'sql']

AlbumRoots
Albums
Images
ImageHaarMatrix
ImageInformation
ImageMetadata
VideoMetadata
ImagePositions
ImageComments
ImageCopyright
Tags
TagsTree
ImageTags
ImageProperties
Searches
DownloadHistory
Settings
ImageHistory
ImageRelations
TagProperties
ImageTagProperties

CREATE TABLE Images
                            (id INTEGER PRIMARY KEY,
                            album INTEGER,
                            name TEXT NOT NULL,
                            status INTEGER NOT NULL,
                            category INTEGER NOT NULL,
                            modificationDate DATETIME,
                            fileSize INTEGER,
                            uniqueHash TEXT,
                            UNIQUE (album, name))
CREATE TABLE Tags
                            (id INTEGER PRIMARY KEY,
                            pid INTEGER,
                            name TEXT NOT NULL,
                            icon INTEGER,
                            iconkde TEXT,
                            UNIQUE (name, pid))
CREATE TABLE ImageTags
                            (imageid INTEGER NOT NULL,
                            tagid INTEGER NOT NULL,
                            UNIQUE (imageid, tagid))
CREATE TABLE ImageMetadata
                            (imageid INTEGER PRIMARY KEY,
                            make TEXT,
                            model TEXT,
                            lens TEXT,
                            aperture REAL,
                            focalLength REAL,
                            focalLength35 REAL,
                            exposureTime REAL,
                            exposureProgram INTEGER,
                            exposureMode INTEGER,
                            sensitivity INTEGER,
                            flash INTEGER,
                            whiteBalance INTEGER,
                            whiteBalanceColorTemperature INTEGER,
                            meteringMode INTEGER,
                            subjectDistance REAL,
                            subjectDistanceCategory INTEGER)

CREATE TABLE Albums
                            (id INTEGER PRIMARY KEY,
                            albumRoot INTEGER NOT NULL,
                            relativePath TEXT NOT NULL,
                            date DATE,
                            caption TEXT,
                            collection TEXT,
                            icon INTEGER,
                            UNIQUE(albumRoot, relativePath))

CREATE TABLE ImageProperties
                            (imageid  INTEGER NOT NULL,
                            property TEXT    NOT NULL,
                            value    TEXT    NOT NULL,
                            UNIQUE (imageid, property))
CREATE TABLE ImageHistory
                            (imageid INTEGER PRIMARY KEY,
                             uuid TEXT,
                             history TEXT)

"""


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
    lst = []
    for row in cursor.fetchall():
        if row:
            try:
                lst.append(row['name'])
            except IndexError:
                lst.append("no key 'name' in %r" % row.keys())
    return '\n'.join(lst)
    
            
    # for row in rows
    # return '\n'.join([row['name'] ])
    # return '\n'.join([str(x['name']) for x in cursor.fetchall()])
    # return "\n".join([row['name'] for row in cursor.fetchall() if row])


def get_photos(pics_root, conn, tags):
    """Yield a tuple (filename, ) per matching picture."""
    # encoding = "utf-8"
    cursor = conn.cursor()
    # li = ','.join(["'{0}'".format(t.decode(encoding)) for t in tags])
    li = ','.join([u"'{0}'".format(t) for t in tags])
    
    where = u'tagname in ({0})'.format(li)
    sql = u"""
    SELECT tag.name AS tagname, alb.albumRoot, alb.relativePath, 
       img.modificationDate, img.name AS imgname
    FROM ImageTags AS it 
    JOIN Images AS img ON img.id = it.imageid
    JOIN Tags AS tag ON tag.id = it.tagid
    JOIN Albums AS alb ON alb.id = img.album
    WHERE {0}
    ORDER BY img.modificationDate
    """.format(where)
    # print(sql)
    cursor.execute(sql)
    for row in cursor:
        # print("{} {} {} {}".format(row[0], row[1], row[2], row[3]))
        # print(row.keys())
        # fn = Path()
        if row['albumRoot'] != 1:
            raise Exception("albumRoot is {}".format(row['albumRoot']))
        # root = pics_root
        # fn = Path(root + row['relativePath'])
        # fn = fn.child(row['imgname'])
        # fn = fn.resolve()
        # if not fn.exists():
        #     raise Exception("Oops: {} doesn't exist".format(fn))
        fn = row['relativePath'] + '/' + row['imgname']
        if fn.startswith('/'):
            fn = fn[1:]
        yield fn, row['modificationDate']
    
    


RSTLINE = """.. sigal_image:: {0}\n"""


@dispatch_command
@arg('tags', help="One ore more Shotwell tags. "
     "The listed pictures must have *at least* one of them.")
@arg('-t', '--target_root',
     help='Where to export tagged pictures and videos.')
@arg('-p', '--pics_root',
     help='Your pictures directory')
@arg('-s', '--sigal_image',
     help='Output as sigal_image directives')
@arg('-b', '--before',
     help='Select photos taken before that time')
@arg('-a', '--after',
     help='Select photos taken after that time')
@arg('-d', '--digikam_db',
     help='Your Shotwell database file')
def main(target_root=None,
         pics_root=Path("~/Pictures/"),
         digikam_db=Path("~/Pictures/digikam4.db").expand_user(),
         sigal_image=False,
         before=None, after=None,
         *tags):
    """Export tagged photos and videos from a Shotwell photo database to a
    target filesystem or list them in different ways.
    See <https://github.com/lsaffre/shotwell2blog>.

    """

    if target_root:
        target_root = Path(target_root).expand_user()
        if not target_root.exists():
            raise CommandError(
                "Target directory %s does not exist!" % target_root)

    if pics_root:
        pics_root = Path(pics_root).expand_user()
        
    conn = sqlite3.connect(digikam_db)
    conn.row_factory = sqlite3.Row

    if False:  # I used this to discover the database structure.
        yield show_tables(conn)
        yield schema(conn, 'Images')
        yield schema(conn, 'Tags')
        yield schema(conn, 'ImageTags')
        yield schema(conn, 'ImageMetadata')
        yield schema(conn, 'ImageProperties')
        yield schema(conn, 'ImageHistory')
        return

    if len(tags) == 0:
        raise CommandError("Must specify at least one tag!")

    # tags = [six.text_type(t) for t in tags]
    # tags = [six.text_type(t).decode('utf8') for t in tags]
    tags = [' '.join(tags)]
    # tags = tags.decode('utf8')
    # multiple tags are not supported.

    if before is not None:
        before = parser.parse(before)
    if after is not None:
        after = parser.parse(after)
    targets = []
    photos = sorted(get_photos(pics_root, conn, tags), key=lambda x: x[0])
    for orig, time_created in photos:
        orig = Path(pics_root + orig)
        if not orig.exists():
            raise Exception("Image {} does not exist".format(orig))
        target = chop(orig, pics_root)
        if target.startswith('/'):
            raise Exception("Target {} ({}, {}) starts with /".format(
                target, orig, pics_root))
        target = target.lower()
        target = target.replace(" ", "_")
        targets.append(target)
        if target_root:
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
            t = parser.parse(time_created)
            # t = time_created
            # if t:
                # print(repr(t))
                # t = time.localtime(time_created)
                # t = datetime.fromtimestamp(mktime(t))
            # else:
            #     t = None
            if before is None or t <= before:
                if after is None or t >= after:
                    if sigal_image:
                        yield RSTLINE.format(target)
                    else:
                        # yield "{0}|{1}".format(t, orig)
                        yield orig

    conn.close()

    if target_root:
        fn = os.path.join(target_root, 'index.rst')
        rstfile = codecs.open(fn, "w", encoding="utf-8")
        for t in targets:
            rstfile.write(RSTLINE.format(t))
        rstfile.close()
