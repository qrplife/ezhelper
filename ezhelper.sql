-- This is the schema for tracks.sqlite
--
-- You need to manage the track id values, the are not autoincrement.
-- The filepath columns are paths relative to the "audioroot" value set in ezhelper.py
CREATE TABLE tracks (id integer primary key,title text,artist text,filepath text);
CREATE TABLE log (track_id,track_title text, artist text, filepath text, lastplay datetime, iteration integer);
CREATE TABLE track_categories (track_id integer, category text);
CREATE TABLE events (id integer primary key, type text, value text, hour integer, minute integer, second integer, maxwait integer, lastplay datetime);
CREATE TABLE categories (id integer primary key, name text, trackrepeat integer, artistrepeat integer, titlerepeat integer);