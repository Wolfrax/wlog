Title: rsyslog daemon filling syslog
Author: Mats Melander
Date: 2020-10-07
Modified: 2020-10-07
Tags: Linux, Raspberry
Category: Technologies
Summary: rsyslog daemon is recurrently adding entries to /var/log/syslog ("rsyslogd-2007: action 'action 18'")

** rsyslog
[ryslog](https://www.rsyslog.com/) is a logging system used in several Linux distributions, including raspbian.

I noticed that on one of my Raspberrys (not all) I had recurrent log entries of type

```text
Oct  7 18:59:38 rpi1 rsyslogd-2007: action 'action 18' suspended, next retry is Wed Oct  7 19:01:08 2020 [try http://www.rsyslog.com/e/2007 ]
```
    
After some investigations, (it is discussed in this [thread](https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=134971#p898539))
I found out that the root cause is that rsyslogd tries to pipe messages to `/dev/xconsole`.

The problem basically is, that no program is reading from `/dev/xconsole`, so the pipe runs full and rsyslog (correctly) 
logs this issue. So this is expected behaviour, but I want to get rid of the messages in `/var/log/syslog`.

The fix is to comment out the following lines in `/etc/rsyslog.conf`:

```text
#daemon.*;mail.*;\
#	news.err;\
#	*.=debug;*.=info;\
#	*.=notice;*.=warn	|/dev/xconsole
```
    
Then restart the rsyslog daemon

```bash
$ sudo systemctl restart rsyslog
```

Should then be Ok.


