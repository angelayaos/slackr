import datetime 
from datetime import timezone
finishing_time = datetime.timedelta(seconds=50) 
time_now = datetime.datetime.now()
now = time_now.timestamp()
print(now)
dt = finishing_time + time_now
time_finish = dt.timestamp()
print(time_finish)
classtype = type(time_finish)
print(classtype)
print("***********************")
time_now = datetime.datetime.now()
now = time_now.timestamp()
time_finish = time_finish
active = True
print(time_finish - now)
