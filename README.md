# IRIS-Data-Download
#################################################################################################

Code for donwloading waveform data from IRIS

#################################################################################################

1. The process begins by downloading station metadata from the IRIS Gmap tool at https://ds.iris.edu/gmap. Save the output in TXT format as a file named 'sta' and ensure all header lines are removed before proceeding.

2. Next, use the sta_make.sh script to reformat the metadata. You must modify the network name in the script (e.g., changing 'XF' to your specific network) before running it. This step removes pipe delimiters and prepares the station list for the Python environment.

3. To generate the event catalog, use ISC_catalog_download.py. You are required to set the directory path on line 6, adjust the depth and magnitude ranges on lines 8 through 10, and update the network name on line 12. The script will output station-specific files named {station}.event.csv.

4. Consolidate these files by running make_eventid.sh after updating the network name (line 3) within the script. This generates ALL_EVENT.dat and ALL_STA.dat for data management, as well as a GMT script named region.sh. You must apply execution permissions to region.sh to plot your event distribution map.

5. For data retrieval, configure obspy_download_iris.py by verifying the path on line 12, the network on line 13, and the channel settings on line 17. Before setting the channel, check the IRIS website to confirm which channels (e.g., BHZ, HHZ) are available for your specific stations. Define the recording window using t1 for the start time and t2 for the end time relative to the event origin; for example, setting t2 = ev_time + 800 captures an 800-second record.

6. The workflow concludes with Pre-Processing.py, which prepares the waveforms for analysis. This script automates instrument response removal, detrending, and frequency filtering to ensure the data is research-ready.
