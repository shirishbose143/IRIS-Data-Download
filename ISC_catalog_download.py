import requests
import csv
from datetime import datetime, timedelta
import os

os.chdir("/home/shirish/SHIRISH/SN_DATA/XQ/NEW")

minmag, maxmag = 1, 10
mindist, maxdist = 0, 1
mindep, maxdep = 0, 50

with open("XQ") as f:
    for line in f:
        parts = line.split()
        if len(parts) < 8:
            continue

        sta, date_s, date_e, stla, stlo = parts[1], parts[2], parts[4], parts[6], parts[7]

        # Convert dates
        s = datetime.strptime(date_s, "%d-%m-%Y").strftime("%Y-%m-%d")
        e = datetime.strptime(date_e, "%d-%m-%Y").strftime("%Y-%m-%d")

        if s == e:  # avoid zero-length interval
            e = (datetime.strptime(e, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

        url = (f"https://www.isc.ac.uk/fdsnws/event/1/query?"
               f"starttime={s}&endtime={e}&minmagnitude={minmag}&maxmagnitude={maxmag}&"
               f"latitude={stla}&longitude={stlo}&minradius={mindist}&maxradius={maxdist}&"
               f"mindepth={mindep}&maxdepth={maxdep}&format=text")

        r = requests.get(url)
        lines = r.text.splitlines()

        events = []
        for line in lines:
            if line.startswith("#"):
                continue
            cols = line.split("|")
            if len(cols) > 11 and cols[2] and cols[3] and cols[4] and cols[10] and cols[11]:
                time = cols[1].replace("T", " ")
                events.append([time, cols[2], cols[3], f"{float(cols[4]):.4f}", f"{float(cols[10]):.1f}", cols[9].lower()])

        # Save only if events exist
        if events:
            with open(f"{sta}.event.csv", "w", newline="") as out:
                writer = csv.writer(out)
                writer.writerows(events)

        print(f"Station {sta}: {len(events)} events downloaded")
