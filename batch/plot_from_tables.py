import argparse
import pandas as pd
from matplotlib import pyplot as plt

opts = { \
     "marklist" : ['+', '.', '+', '.', 'v', '<', '>', 'd', 'x', '^'],
     "colorlist" : ['g', 'g', 'r', 'r', 'b', 'm', 'pink', 'k', 'c', 'orange'],
     "linetype" : ['-', '--', '-.', ':', '--', '-.', '--',':'],
     "linewidth" : 0.75,
     "marksize" : 7,
     "markedgewidth" : 1 \
     } 

parser = argparse.ArgumentParser(
    description = "Plot timing comparison of batch problem")
parser.add_argument('files', nargs='+', help = "Files to read from")
parser.add_argument('--log', help = "For log y axis",
        action="store_true")
args = parser.parse_args()

device_dict = { "hip":"Mi100", "cuda":"V100" }

i = 0
plt.close()
for filen in args.files:
    df = pd.read_csv(filen, sep=' ')
    if args.log:
        plt.semilogy(df["batch size"], df["solve time (s)"], lw=opts['linewidth'], \
                ls=opts['linetype'][i], color=opts['colorlist'][i], \
                marker=opts['marklist'][i], ms=opts['marksize'], \
                mew=opts['markedgewidth'], \
                label=df.at[0,"processor"] + "," + df.at[0,"solver type"] + ","
                    + df.at[0,"matrix format"]
                )
    else:
        plt.plot(df["batch size"], df["solve time (s)"], lw=opts['linewidth'], \
                ls=opts['linetype'][i], color=opts['colorlist'][i], \
                marker=opts['marklist'][i], ms=opts['marksize'], \
                mew=opts['markedgewidth'], \
                label=df.at[0,"processor"] + "," + df.at[0,"solver type"] + ","
                    + df.at[0,"matrix format"]
                )
    i += 1

plt.xlabel("Batch size")
plt.legend()
plt.ylabel("Time (s)")
if args.log:
    plt.grid('on', which='both')
else:
    plt.grid('on')
plt.savefig("timings." + "png", dpi=200, bbox_inches='tight')
