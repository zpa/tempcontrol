#!/bin/bash

PID=`sudo pidof gammu-smsd`
echo gammu-smsd running with PID $PID
echo suspending gammu-smsd...
sudo kill -s SIGUSR1 $PID
sleep 1
echo testing modem...
MODEM_RESPONSE=`
(
minicom -D /dev/ttyS0 <<endOfScript
AT
endOfScript
)
`
if [ $? -eq 0 ]
 then
  echo "modem is alive"
 else
  echo "modem did not boot properly, rebooting system"
  sudo reboot -f
fi
echo restarting gammu-smsd...
sudo kill -s SIGUSR2 $PID
echo done
