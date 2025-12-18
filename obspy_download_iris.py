#!/usr/bin/env python3
import os
import pandas as pd
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
# from obspy.io.xseed import Parser

# -----------------------------
# User settings
# -----------------------------
os.chdir("/home/shirish/SHIRISH/PLUTO/Rajiya")
xr_file = "IC"  # Station info
client = Client("IRIS")

# -----------------------------
# Helper to parse DD-MM-YYYY to UTCDateTime
# -----------------------------
def parse_datetime(day_str, time_str):
    dd, mm, yyyy = day_str.split("-")
    dt_str = f"{yyyy}-{mm}-{dd} {time_str}"  # YYYY-MM-DD HH:MM:SS
    return UTCDateTime(dt_str) 

# -----------------------------
# Read XR station file
# -----------------------------
stations = []
with open(xr_file, "r") as f:
    for line in f:
        net, sta, start_d, start_t, end_d, end_t, lat, lon = line.split()
        starttime = parse_datetime(start_d, start_t)
        endtime   = parse_datetime(end_d, end_t)
        stations.append({
            "network": net,
            "station": sta,
            "starttime": starttime,
            "endtime": endtime,
            "latitude": float(lat),
            "longitude": float(lon)
        })

# -----------------------------
# Loop over stations
# -----------------------------
for st in stations:
    # event_file = f"{st['station']}.event.csv"
    event_file = "event1.dat"
    if not os.path.exists(event_file):
        print(f"Event file {event_file} not found, skipping {st['station']}.")
        continue

    # Read event catalog
    df = pd.read_csv(event_file, header=None)
    df.columns = ["time", "lat", "lon", "depth", "mag", "type"]

    # Add station info to each event
    df["network"] = st["network"]
    df["station"] = st["station"]
    df["station_lat"] = st["latitude"]
    df["station_lon"] = st["longitude"]

    # Loop over each event
    for i, row in df.iterrows():
        ev_time = UTCDateTime(row["time"])
        if not (st["starttime"] <= ev_time <= st["endtime"]):
            continue  # Skip events outside station time window

        # Request window: 1 min before, 10 min after origin
        t1 = ev_time - 0
        t2 = ev_time + 800

        try:
            # Download waveforms
            st_data = client.get_waveforms(
                network=st["network"],
                station=st["station"],
                location="*",
                channel="B??",  # Adjust if needed
                starttime=t1, endtime=t2
            )

            # Update SAC headers and save
            for tr in st_data:
                o = float(ev_time - tr.stats.starttime)

                # Snap to the sample grid (prevents 59.999999 vs 60.0 issues)
                dt = tr.stats.delta
                o = round(o / dt) * dt

                # 1) Set reference (NZ*) to the origin time
                # tr.stats.starttime = t1
                tr.stats.sac = {}
                
                # Station info
                tr.stats.sac.kstnm = st["station"]
                tr.stats.sac.knetwk = st["network"]
                tr.stats.sac.stla = st["latitude"]
                tr.stats.sac.stlo = st["longitude"]
                tr.stats.sac.stel = 0
                # Event info
                tr.stats.sac.evla = row["lat"]
                tr.stats.sac.evlo = row["lon"]
                tr.stats.sac.evdp = row["depth"]
                tr.stats.sac.mag = row["mag"]
                tr.stats.sac.o = 0.0        # O marker = 0 s at origin (like CHNHDR O GMT ...)
                tr.stats.sac.b = -o         # Begin time relative to origin
                tr.stats.sac.iztype = 9     # IZTYPE = IO (zero is origin time)
                # Save SAC
                sac_name = f"{ev_time.strftime('%Y%m%d%H%M%S')}.{tr.stats.station}.{tr.stats.channel}.SAC"
                tr.write(sac_name, format="SAC")
                print(f"Saved {sac_name}")

        except Exception as e:
            print(f"Failed for {st['station']} {ev_time}: {e}")
    # Download RESP for only the channels you have
    if 'st_data' in locals() and st_data:
        channels_downloaded = set(tr.stats.channel for tr in st_data)
        for ch in channels_downloaded:
            resp_file = f"RESP.{st['network']}.{st['station']}.{ch}"
            try:
                client.get_stations(
                    network=st["network"],
                    station=st["station"],
                    location="*",
                    channel=ch,
                    starttime=st["starttime"],
                    endtime=st["endtime"],
                    level="response",
                    filename=resp_file
                )
                print(f"✅ Downloaded RESP: {resp_file}")
            except Exception as e:
                print(f"⚠️ Failed to download RESP for {st['station']} {ch}: {e}")
    else:
        print("⚠️ Skipping RESP download — 'st_data' not defined or empty.")