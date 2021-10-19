import argparse
import numpy as np
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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description = "Plot timing comparison of batch problem")
    parser.add_argument('files', nargs='+', help = "Files to read from")
    #parser.add_argument('--base_columns', nargs='+', help = "Columns that determine each base case (1 set of boxes for each)")
    #parser.add_argument('--base_values', nargs='+', help = "Value in the base_column corresponding to base case")
    parser.add_argument('--log', help = "For log y axis",
            action="store_true")
    args = parser.parse_args()
   
    plt.close()
    fig,ax1 = plt.subplots()
        
    df = pd.read_csv(args.files[0], sep=' ')
    basevalsdf = df.loc[df['processor'] == 'skylake']
    basevals = df['solve time (s)'].to_numpy()
    cases = df['case name'].unique()
    nplots = len(cases)
    processors = df['processor'].unique()
    x = np.arange(len(processors))
    width=0.24
    print("Will make " + str(nplots) + " plots for " + str(cases))
    #for iplot in range(nplots):
    #    dfplot = df.loc[df['case name'] == cases[iplot]]
    #    #dfplot.boxplot(by='processor', ax=ax1, width=0.8*width, positions=x + iplot*width)
    #    dfplot.boxplot(column=['solve time (s)'], by='processor', ax=ax1)
    df.boxplot(column=['solve time (s)'], by=['processor','case name'], ax=ax1)
    plt.tight_layout()
    plt.show()
    
    #plt.xlabel("Batch size")
    #plt.legend()
    #plt.ylabel("Time (s)")
    #if args.log:
    #    plt.grid('on', which='both')
    #else:
    #    plt.grid('on')
    #plt.savefig("timings." + "png", dpi=200, bbox_inches='tight')
