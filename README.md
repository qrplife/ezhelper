# ezhelper
This program helps ezstream feeding paths to audio tracks on demand.
The database holds the track catalog and rules for maintaining track, title, and artist separation.

https://www.icecast.org/ezstream/

Configure ezstream to use this program as a source with these entries in ezstream.conf
```
<filename>/home/station/ezhelper.py</filename>
<playlist_program>1</playlist_program>
```

Yes, ezhelper.py must have its executable bit set.
