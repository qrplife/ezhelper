#!/usr/bin/python3

# ezstream feeder - This program is called by ezstream when it needs to know the next track to play.
# The sqlite3 database contains the track catalog and rules for maintaining track, title, and artist separation.
# 
# The program needs to execute quickly and return only the path to an audio file on stdout every time it is invoked.
# If there is any deviation or exception then ezstream falls over.
#
# This code has been used to generate dynamic "playlists" (one track at a time) for online radio stations that have been on the air for years without interruption.


import sqlite3
import random
import datetime
import time
timerstart = time.time()

def getTrackLog(log,index,value):
    tracklog = []
    for e in log:
        if e[index]==value:
            tracklog.append(e)
    return tracklog


# audio root
audioroot="/home/station/audio/"

# setup some important times
# time now in seconds
dt = datetime.datetime.now()
year = int(dt.strftime("%Y"))
month = int(dt.strftime("%m"))
day = int(dt.strftime("%d"))
hour = int(dt.strftime("%H"))
now = int(dt.strftime("%s"))

# 24 hours ago
last24 = now - (24 * 60 * 60)

# setup repeat intervals for default random mode
mode = "RANDOM"
category = "DEFAULT"
trackRepeat = 5 * 60 # 5 minutes
artistRepeat = 2 * 60 # 2 minutes
titleRepeat = 3 * 60 # 3 minutes

# load all tracks from db
db = "/home/station/tracks.sqlite3"
def getTracksByCategory(category):
    tracklist = []
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        sql = "SELECT * FROM tracks as t INNER JOIN track_categories as c ON c.track_id=t.id WHERE c.category=?"
        params = (category,)
        cur.execute(sql,params);
        tracklist = cur.fetchall()        
        sql = "SELECT * FROM log WHERE lastplay > ? ORDER BY lastplay DESC"
        params = (last24 * 5,)
        cur.execute(sql,params);
        log = cur.fetchall()
        sql = "SELECT trackrepeat,artistrepeat,titlerepeat FROM categories WHERE name=?"
        params = (category,)
        cur.execute(sql,params)
        repeats = cur.fetchall()
        trackRepeat = repeats[0][0]
        artistRepeat = repeats[0][1]
        titleRepeat = repeats[0][2]
    except:
        pass
    finally:
        conn.close()

    return tracklist,log,trackRepeat,artistRepeat,titleRepeat

def getEvent(time):
    events=[]
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM events ORDER BY hour,minute,second ASC")
        events = cur.fetchall()
    except:
        pass
    finally:
        conn.close()

    for event in events:
        #compute start time, end time (start+maxwait)
        starthour = hour
        eventhour = int(event[3])
        if eventhour > 0:
            starthour=eventhour
            
        start = int(datetime.datetime(year,month,day,starthour,int(event[4]),int(event[5])).strftime("%s"))
        end = start + int(event[6])
        lastplay = int(event[7])
        #has this event already played?
        if start > lastplay:
            # are we after the start time and before the end time?
            if start <= now and now <= end:
                return tuple(event)
        
    return None

# serve a track to stdout
trackServed = False
serveAttempt = 0

while not trackServed:

    event = None
    # two types of event are supported: play a specific TRACK or play a random select from a specific CATEGORY
    # for events to play a specific file just return that file path on stdout
    #
    # otherwise for events to play from a folder then load the folder rules, filter the tracklist by folder
    # then run the random selection code below
    event = getEvent(now)
    
    if event:
        if event[1]=="CATEGORY":
            category = event[2]
        
    if mode == "RANDOM":
        # filter tracks based on category
        tracks,log,trackRepeat,artistRepeat,titleRepeat = getTracksByCategory(category)
        serveAttempt += 1
        # todo: dont get into an infiteloop when rule prevents a track from serving
        if serveAttempt > len(tracks):
            # todo: adjust the limits so that a track can be served. probably should record limits in a file or table
            break
        
        track = random.choice(tracks)
        track_id = track[0]
        # check the track interval
        trackLog = getTrackLog(log,0,track_id)
        if len(trackLog) > 0:
            trackLastPlay = trackLog[0][4]
            lastPlayDelta = now - trackLastPlay
        
            if lastPlayDelta < trackRepeat:
                continue
        
        track_title = track[1]
        # check the title interval
        titleLog = getTrackLog(log,1,track_title)
        if len(titleLog) > 0:
            titleLastPlay = titleLog[0][4]
            lastPlayDelta = now - titleLastPlay

            if lastPlayDelta < titleRepeat:
                continue
           
        artist = track[2]
        # check the artist interval
        artistLog = getTrackLog(log,2,artist)
        if len(artistLog) > 0:
            artistLastPlay = artistLog[0][4]
            lastPlayDelta = now - artistLastPlay

            if lastPlayDelta < artistRepeat:
                continue

        # if we've made it this far, then the track is playable according to the rules
        filepath = track[3]

    #this is the only stdout from the program
    print(audioroot+filepath)

    timerend = time.time()
    trackServed = True
    # write the served track to the log table
    if trackServed:
        try:
            with open("timing.txt","a") as t:
                t.write("filename: "+filepath+" served in: "+str(timerend-timerstart)+"\n")

            conn = sqlite3.connect(db)
            cur = conn.cursor()
            sql = "INSERT INTO log VALUES (?, ?, ?, ?, ?,?)"
            params = (track_id,track_title,artist,filepath,now,serveAttempt)
            cur.execute(sql,params)
            if event:
                sql = "UPDATE events SET lastplay=? WHERE id=?"
                params = (now,event[0])
                cur.execute(sql,params)
            conn.commit()
        except:
            pass
        finally:
            conn.close()
        
        
    




