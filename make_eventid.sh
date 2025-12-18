#!/bin/sh -x

file=XR

cat *csv |sed 's/\r$//' | sort -u | awk -F, '{gsub(/-/," ",$1); print $1,$2,$3,$4,$5,$6}' > ee
#cat event | awk -F, '{gsub(/-/," ",$1); print $1,$2,$3,$4,$5,$6}'>ee

cat ee|awk '{print $1$2$3$4}'|awk -F: '{print $1$2$3}'|awk -F. '{print $1}'>eventid
paste ee eventid|awk '{print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10}'>event.dat
cat event.dat | awk '{print $NF, $5, $6, $7, $8, $9}' | sort -u | tail -n +2 > ALL_EVENT.dat

cat $file | awk '{print $2,$7,$8}'>ALL_STA.dat

min_lat=`cat ALL_EVENT.dat | sort -k2n | head -2| awk '{print $2}' | awk 'NR==2'`
max_lat=`cat ALL_EVENT.dat | sort -k2n | tail -1| awk '{print $2}'`
min_lon=`cat ALL_EVENT.dat | sort -k3n | head -2| awk '{print $3}' | awk 'NR==2'`
max_lon=`cat ALL_EVENT.dat | sort -k3n | tail -1| awk '{print $3}'`

# Write GMT script to a file called region.sh
cat <<EOF> region.sh
#!/bin/bash -x

region=-R$min_lon/$max_lon/$min_lat/$max_lat
projection=-JM6i

gmt begin Region pdf
	gmt set MAP_FRAME_TYPE plain
	gmt basemap \$projection \$region -B -BWStr
	cat ALL_EVENT.dat | awk '{print \$3,\$2,\$4,\$5*3.1}' | gmt plot \$region \$projection -Scp -Cjet -W0.4,"#164444" -t55
	cat ALL_STA.dat | awk '{print \$3,\$2}' | gmt plot \$region \$projection -Si0.50 -Gred -W1 -t5
	gmt coast \$region \$projection -Wfaint -Df -A0/0/1 -W0.3
gmt end show
EOF
