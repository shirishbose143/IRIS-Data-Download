#!/bin/sh -x

filename='sta'

while IFS='|' read -r field1 field2 latitude longitude field5 field6 start_date end_date; do
    # Extracting date and time from ISO 8601 format
    start_date=$(date -d "$start_date" +'%d-%m-%Y %H:%M:%S')
    end_date=$(date -d "$end_date" +'%d-%m-%Y %H:%M:%S')

    # Outputting the converted format
    echo "$field1 $field2 $start_date $end_date $latitude $longitude">>XF
done < "$filename"

