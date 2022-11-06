#!/usr/bin/python3
import sys
import gammu

if len(sys.argv) != 3:
	print('less than 2 cmdline arguments')
	print('usage: simulate_incoming_sms.py <sender> <text>')
	exit(1)

sm = gammu.StateMachine()
sm.ReadConfig()
sm.Init()

sender = sys.argv[1]
text = sys.argv[2]

print(f'sender: {sender}')
print(f'text: {text}')

message = {
	"Text": text,
	"SMSC": {"Location" : 1},
	"Number": sender,
	"Folder": 1
}

sm.AddSMS(message)

