#!/bin/bash

PID=`sudo pidof gammu-smsd`
echo gammu-smsd running with PID $PID
echo suspending gammu-smsd...
sudo kill -s SIGUSR1 $PID
echo querying gsm time...
GSMTIME=`
(
python <<endOfScript
import gammu
sm = gammu.StateMachine()
sm.ReadConfig(Filename='/etc/gammu-smsdrc')
sm.Init()
dt = sm.GetDateTime()
print(dt.isoformat())
endOfScript
)
`
echo GSM time is $GSMTIME
echo setting local time...
sudo timedatectl set-time "`echo $GSMTIME | sed 's/T/\ /'`"
echo restarting gammu-smsd...
sudo kill -s SIGUSR2 $PID
echo done
