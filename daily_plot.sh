#!/bin/bash
#===========================================================================
# daily_plot.sh
#
# Get daily data from mysql database and plot with gnuplot.
#===========================================================================
MYSQL_DIR="/var/lib/mysql/thermo_data/"
HOME_DIR="/home/pi/rpi-thermo/"
PLOT_DIR=""$HOME_DIR"plots/"
DATA_FILE="temp.dat"
CMD_FILE=""$HOME_DIR"plot_temps"
if [ $# -eq 1 ]; then
  today=$(date --date="$1" +'%Y-%m-%d')
else
  today=$(date --date='today' +'%Y-%m-%d')
fi
PLOT_FILE=""$PLOT_DIR""$today".png"
yesterday=$(date --date="$today-1 day" +'%Y-%m-%d')
tomorrow=$(date --date="$today+1 day" +'%Y-%m-%d')
cmd="SELECT * FROM data WHERE datetime \
     BETWEEN '$today' AND '$tomorrow' \
     INTO OUTFILE '$DATA_FILE';"
echo "$cmd"
sudo rm -f "$MYSQL_DIR""$DATA_FILE"
mysql -u thermo -pthermo thermo_data -e "$cmd"
sudo mv -f "$MYSQL_DIR""$DATA_FILE" "$HOME_DIR".
sudo chown pi:pi "$HOME_DIR""$DATA_FILE"
gnuplot -e "plot_title='"$today"'; data_file='"$HOME_DIR""$DATA_FILE"';plot_file='"$PLOT_FILE"'" "$CMD_FILE"
rm -f "$HOME_DIR""$DATA_FILE"