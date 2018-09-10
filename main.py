import datetime
import subprocess
import time

import pandas
import schedule

SAMPLE_FREQ_MINS = 1

cmd = "dig +noall +answer +stats +retry=0 +nofail google.com @8.8.8.8".split()
data = {}

def get_sample():
    timestamp = datetime.datetime.now()
    process = subprocess.run(cmd, text=True, capture_output=True)
    out_lines = process.stdout.split('\n')
    try:
        answer = out_lines[0].split()
        response_time = int(out_lines[1].split()[3])
        datapoint = {'domain': answer[0],
                     'response_time': response_time,
                     'record_type': answer[3],
                     'ip': answer[4]
                     }
        data[timestamp] = datapoint
        print("{ts} - {d}".format(ts=timestamp, d=datapoint))
    except:
        print("{ts} - SAMPLE FAILED!".format(ts=timestamp))
        print(out_lines)

def write_out():
    df = pandas.DataFrame(data).transpose()
    name = "dns_sanity_results_retry_{d.month}_{d.day}_{d.hour}".format(d=datetime.datetime.now())
    df.to_csv("{name}.csv".format(name=name))

schedule.every(SAMPLE_FREQ_MINS).minutes.do(get_sample)
schedule.every(4).hours.do(write_out)

print("{ts} - Digging {c[3]} {c[4]} every {mins} minutes.".format(c=cmd,
                                                                  mins=SAMPLE_FREQ_MINS,
                                                                  ts=datetime.datetime.utcnow().isoformat()))

while True:
    schedule.run_pending()
    time.sleep(1)
