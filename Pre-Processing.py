from obspy import read
from obspy.clients.fdsn import Client
from obspy import read_inventory
import os
import glob

# -----------------------------
# Settings
# -----------------------------
os.chdir("/home/shirish/Desktop/SHIRISH/LOCAL/XR/NEW")
pre_filt = (0.005, 0.01, 45, 50)  # pre-filter for remove_response
freqmin = 1
freqmax = 5

# Loop over all SAC files in directory
for sac_file in glob.glob("*.SAC"):
    # Determine RESP file: e.g., RESP.<network>.<station>.<channel>
    parts = sac_file.split(".")
    if len(parts) < 3:
        print(f"Skipping invalid SAC file name: {sac_file}")
        continue
    sta = parts[1]
    ch = parts[2]
    inv_file = f"RESP.XR.{sta}.{ch}"  # adjust prefix if needed

    if not os.path.exists(inv_file):
        print(f"Inventory file {inv_file} not found, skipping {sac_file}")
        continue

    try:
        st = read(sac_file)
        inv = read_inventory(inv_file)

        for tr in st:
            # ---------------------
            # Preprocessing
            # ---------------------
            tr.detrend("demean")               # rmean
            tr.detrend("linear")               # rtr
            tr.taper(max_percentage=0.05, type="cosine")  # taper
            tr.filter("bandpass", freqmin=freqmin, freqmax=freqmax,
                      corners=4, zerophase=True)       # BP N 4 C 1 5

            # ---------------------
            # Remove instrument response
            # ---------------------
            tr.remove_response(inventory=inv, output="VEL", pre_filt=pre_filt)

            # ---------------------
            # Save as .SAC.inst
            # ---------------------
            out_file = sac_file + ".inst"
            tr.write(out_file, format="SAC")
            print(f"Saved {out_file}")

    except Exception as e:
        print(f"Failed to process {sac_file}: {e}")
