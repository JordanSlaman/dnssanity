import os

import pandas
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

folders = ['vsphere', 'aws']

for fold in folders:
    files = os.listdir(fold)

    # filter only reply
    files = [fn for fn in files if 'retry' in fn]

    df = None
    for fn in files:
        if df is None:
            df = pandas.read_csv('{fold}/{fn}'.format(fold=fold, fn=fn), index_col=0, parse_dates=True)
        else:
            df.append(pandas.read_csv('{fold}/{fn}'.format(fold=fold, fn=fn), index_col=0, parse_dates=True))
    df['response_time'].plot(ax=ax)

plt.title("dig google.com @8.8.8.8 response time (ms)")
plt.xlabel('timestamp')
plt.ylabel('ms')
plt.legend(folders)
fig.set_size_inches(18.5, 10.5)
fig.autofmt_xdate()
fig.savefig("out.png".format())
