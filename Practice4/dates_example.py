#1 Subtract five days from current date
from datetime import datetime, timedelta

today = datetime.now()
five_days_ago = today - timedelta(days=5)

print("Current date:", today)
print("Five days ago:", five_days_ago)
print()


#2 Print yesterday, today, tomorrow
from datetime import datetime, timedelta

today = datetime.now().date()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)

print("Yesterday:", yesterday)
print("Today:", today)
print("Tomorrow:", tomorrow)
print()


#3 Drop microseconds from datetime
from datetime import datetime

now = datetime.now()
now_no_microseconds = now.replace(microsecond=0)

print("With microseconds:", now)
print("Without microseconds:", now_no_microseconds)
print()


#4 Calculate difference between two dates in seconds
from datetime import datetime

date1 = datetime(2026, 2, 22, 12, 0, 0)
date2 = datetime(2026, 2, 21, 6, 30, 0)

difference = date1 - date2
seconds = difference.total_seconds()

print("Difference in seconds:", seconds)
print()