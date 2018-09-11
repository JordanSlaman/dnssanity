import datetime
import logging
import subprocess
import time

import pandas
import schedule

SAMPLE_FREQ_MINS = 5
WRITE_FREQ_HOURS = 12

logger = logging.getLogger("dns_sanity")
logger.setLevel(logging.INFO)

fh = logging.FileHandler('results.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

logger.addHandler(fh)
logger.addHandler(ch)


cmd = "dig +noall +answer +stats +retry=0 +nofail google.com @8.8.8.8".split()
data = {}

# cmd = "dig +noall +answer +stats +retry=0 +nofail www.sometimestimeout.com @172.16.124.209".split()

def get_sample():
    timestamp = datetime.datetime.now()
    process = subprocess.run(cmd, text=True, capture_output=True)
    out_lines = process.stdout.split('\n')

    datapoint = {'domain': cmd[6],
                 'record_type': None,
                 'resolver': cmd[7]}

    if ";; connection timed out; no servers could be reached" in out_lines:
        elapsed = datetime.datetime.now() - timestamp
        datapoint['response_time'] = int(elapsed.total_seconds() * 1000)
        datapoint['rcode'] = "TIMEOUT"
    else:
        if ";; Warning: query response not set" in out_lines[0]:
            out_lines.pop(0)
        answer = out_lines[0].split()
        datapoint['response_time'] = int(out_lines[1].split()[3])
        datapoint['record_type'] = answer[3]
        datapoint['rcode'] = "NOERROR"

    data[timestamp] = datapoint
    logger.debug("{ts} - {d}".format(ts=timestamp, d=datapoint))


def write_out():
    df = pandas.DataFrame(data).transpose()
    now = datetime.datetime.now()
    name = "dns_sanity_results_{d.month}_{d.day}_{d.hour}".format(d=now)
    df.to_csv("{name}.csv".format(name=name))
    logger.debug("{ts} - Writing out {hours} hours of records to file: {name}.csv".format(ts=now,
                                                                                          hours=WRITE_FREQ_HOURS,
                                                                                          name=name))


schedule.every(SAMPLE_FREQ_MINS).minutes.do(get_sample)
schedule.every(WRITE_FREQ_HOURS).hours.do(write_out)

logger.info("{ts} - Digging {c} every {mins} minutes.".format(c=cmd,
                                                              mins=SAMPLE_FREQ_MINS,
                                                              ts=datetime.datetime.utcnow()))

while True:
    schedule.run_pending()
    time.sleep(1)
