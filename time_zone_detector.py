from datetime import *
from dateutil.tz import *

print(datetime.now(tzlocal())) # local time

print(datetime.now(tzlocal()).tzname()) # name of the region
