# get filepath
def getFiles(path):
    return glob.glob(path)


def dateConversion(column):
    return column.astype('datetime64[ns]')


if __name__ == '__main__':
    import glob
    import os
    import pandas as pd
    from datetime import datetime
    import time
    import numpy as np

    filepath = '/Users/bettychitty/Desktop/Automation_Project'
    files = getFiles(filepath + '/*.xlsx')

    for f in files:
        read = pd.read_excel(f)

        frame = read[~read['PO Item Text'].str.contains('#', na=False)]
        df = pd.DataFrame(frame)

        unknown = read[read['PO Item Text'].str.contains('#', na=False)]

        Purchase = df['Purchase Date']
        FVO = df['FVO Approval Date']
        AO = df['AO Approval Date']
        CH = df['CH Approval Date']

        df['FVO Approval Date'] = dateConversion(FVO)
        df['AO Approval Date'] = dateConversion(AO)
        df['CH Approval Date'] = dateConversion(CH)


        results = df.loc[(Purchase < FVO) |
                     (Purchase < AO) |
                     (Purchase < CH)]

        print(results)