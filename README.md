# w3cstats

## Overview

This tool is developped to parse log files in W3C format. It shows a summary
of the traffic every 10 seconds and raise an alert when the traffic average
exceeds a threshold during 2 minutes. Alerts are recovered when the average is
under the threshold during 2 minutes.

Available scripts are in [scripts](./scripts) directory

## Script: watch-log

### Howto

```bash
Usage:
    watch-log -h | --help
    watch-log [-s <threshold>] [-l <log_file>]

Options:
    -h, --help                                  Show this screen.
    -s <threshold>, --threshold <threshold>     Raise an alert when traffic
                                                exceeds the threshold
                                                [Default: 10]
    -l <log_file>, --logfile <log_file>         Logfile to read
                                                [Default: /tmp/access.log]
```

### Alert test scenario

How to use it: Start the container by running `docker-compose up --build`

1. Use an already generated log file
  - The script will use the log file [./tests/access.log](./tests/access.log)
  - Expected result is: [./tests/result.log](./tests/result.log)
2. Use a live log generation:
  - Run `./tests/gen-logs.yml` (used to create [./tests/access.log](./tests/access.log))

To read a log file again from the begining, remove `./tests/access.log.offset`
