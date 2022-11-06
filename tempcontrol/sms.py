from datetime import datetime
from .config import SMS_OUTBOX

# gammu file backend filename template:
# OUT<priority><date>_<time>_<serial>_<recipient>_<note>.<ext>

def send_sms(to_number, message, serial = 1):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{SMS_OUTBOX}OUTA{timestamp}_{serial}_{to_number}_msg.txt'
    f = open(filename, 'w')
    f.write(message)
    f.close()
    
