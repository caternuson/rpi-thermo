#!/bin/bash
#===========================================================================
# daily_plot.sh
#
# Get daily data from mysql database and plot with gnuplot.
#===========================================================================
if [ $# -eq 1 ]; then
  today=$(date --date="$1" +'%Y-%m-%d')
else
  today=$(date --date='today' +'%Y-%m-%d')
fi
yesterday=$(date --date="$today-1 day" +'%Y-%m-%d')
tomorrow=$(date --date="$today+1 day" +'%Y-%m-%d')
cmd="SELECT * FROM data WHERE datetime \
     BETWEEN '$today' AND '$tomorrow' \
     INTO OUTFILE 'temp.dat';"
#echo "$cmd"
mysql -u thermo -pthermo thermo_data -e "$cmd"
sudo mv /var/lib/mysql/thermo_data/temp.dat /home/pi/rpi-thermo/.
sudo chown pi:pi /home/pi/rpi-thermo/temp.dat
gnuplot -e "plot_title='"$today"'" plot_temps
mv -f temp.png /home/pi/rpi-thermo/plots/"$today".png
rm -f /home/pi/rpi-thermo/temp.dat