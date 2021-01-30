# NOTE:  Use second example below.
import datetime
from datetime import timedelta

datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
date1 = '1963-09-15 12:00:00.000'  # Some previous datetime.datetime.now() stamp in a text file
date2 = str(datetime.datetime.now())   #date2 = '2020-08-06 20:57:28.067' for example
diff = datetime.datetime.strptime(date2, datetimeFormat)\
    - datetime.datetime.strptime(date1, datetimeFormat)
 
print("Difference:", str(diff))
diffStr = str(diff)
diffParts=diffStr.split(":")
daysHours = diffParts[0]
minutes = diffParts[1]  # minutes
seconds = diffParts[2]  # seconds

print("Time Elapsed is ", daysHours, "Hours, ", minutes, " minutes, " , seconds, " seconds")

print("From now: ", datetime.datetime.now())

#Difference: 20781 days, 1:22:10.068396
#Time Elapsed is  20781 days, 1 Hours,  22  minutes,  10.068396  seconds
#From now:  2020-08-07 13:22:10.156159

#===================================================

from dateutil.relativedelta import relativedelta
# Also needs import datetime, but already have above.

strDateStamp = str(datetime.datetime.now()).split(".")
strDateStamp = strDateStamp[0]
print(strDateStamp)

#a = '2020-08-07 12:00:56'  # Would be now
#b = '1963-09-15 12:00:00'  # Older date
a = strDateStamp
b = '2019-07-04 12:00:00'  

start = datetime.datetime.strptime(a, '%Y-%m-%d %H:%M:%S')
ends = datetime.datetime.strptime(b, '%Y-%m-%d %H:%M:%S')

diff = relativedelta(start, ends)

print("Time elapsed is %d years %d month %d days %d hours %d minutes %d seconds" % (diff.years, diff.months, diff.days, diff.hours, diff.minutes, diff.seconds))

