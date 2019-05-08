#! /usr/bin/env bash

export LC_TIME=C

LOG_FILE="$(dirname $0)/access.log"

function write_log(){
  echo "$1 [$(date "+%d/%b/%Y:%H:%M:%S %z")] $2" >> $LOG_FILE
}

function gen_lines() {
  csv_file="${1}"              # Source file to generate the log lines
  interval_line="${2:-1}"      # Delay between lines
  times="${3:-15}"             # times to run
  interval_read="${4:-0}"      # interval between file reads in seconds
  # default set to have a flat traffic during 1 minute

  count=0
  for i in $(seq "$times"); do
    while read -r line; do
      if [[ $line =~ .*,.* ]]; then
        write_log "${line%,*}" "${line#*,}"
      else
        write_log "${line}"
      fi
      [ "$interval_line" -ge 1 ] &&
        [ $(( count % 5 )) -eq 0 ] &&
        sleep "$interval_line"
      count=$(( $count + 1 ))
    done < "$csv_file"
    [ "$interval_read" -ge 1 ] && sleep "$interval_read"
  done
}

echo "$(date) - Traffic with http errors unders threshold"
gen_lines "$(dirname $0)/valid-logs-errors.csv" 1 1
# Should obtain something like following in the summary
# | Top errors
# |   - /api : 50.00%

echo "$(date) - Traffic under threshold"
gen_lines "$(dirname $0)/valid-logs.csv"
# No alert expected, should obtain:
# --- Summary: 2019-05-08 16:54:10
# | Global metrics:
# | -  Hits: 10 (1/s)
# | -  Size: 897.0 (90/s)
# | Top hits
# |   - /api : 5
# |   - /login : 3
# |   - /report : 1
# |   - / : 1
# | Top errors: No error detected ;)


echo "$(date) - High traffic"
gen_lines "$(dirname $0)/valid-logs.csv" 0 120 1
# Should obtain this:
# High traffic generated an alert - hits = 10, triggered at 2019-05-08 17:26:00+02:00

echo "$(date) - Traffic under threshold"
gen_lines "$(dirname $0)/valid-logs.csv" 1 30
# Should obtain this:
# Clear alert triggered at 2019-05-08 17:26:00+02:00 - hits = 1, recovered at 2019-05-08 17:28:00+02:00

echo "$(date) - Invalid lines"
gen_lines "$(dirname $0)/invalid-logs.csv" 1 1
# Should obtain this:
# [w3cstats WARNING] Invalid Line: 127.0.0.1 - localhost [08/May/2019:17:45:22 +0200] "GET /login HTTP/1.0"
