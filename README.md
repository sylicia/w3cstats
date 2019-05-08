# w3cstats

## Overview

This tool is developped to parse log files in W3C format. It shows a summary
of the traffic every 10 seconds and raise an alert when the traffic average
exceeds a threshold during 2 minutes. Alerts are recovered when the average is
under the threshold during 2 minutes.

Available scripts are in [scripts](./scripts) directory

## Script: read-file

```bash
Usage:
    read-file -h | --help
    read-file [-s <threshold>] [-l <log_file>]

Options:
    -h, --help                                  Show this screen.
    -s <threshold>, --threshold <threshold>     Raise an alert when traffic
                                                exceeds the threshold
                                                [Default: 10]
    -l <log_file>, --logfile <log_file>         Logfile to read
                                                [Default: /tmp/access.log]
```
