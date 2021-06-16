import glob
import os
import pandas as pd
from datetime import datetime
import time
import numpy as np

from webIO import userXLSXUpload as webIO_upload
from pywebio.output import *
from pywebio.platform.flask import webio_view
from pywebio import start_server
from flask import Flask

app = Flask(__name__)

# get files from filepath
def getFiles(path):
    return glob.glob(path)

# convert strings to dates
def dateConversion(column):
    return column.astype('datetime64[ns]')

def create_df():

    content = webIO_upload()

    frame = content[~content['PO Item Text'].str.contains('#', na=False)]
    df = pd.DataFrame(frame)

    unknown = content[content['PO Item Text'].str.contains('#', na=False)]

    Purchase = df['Purchase Date']
    FVO = df['FVO Approval Date']
    AO = df['AO Approval Date']
    CH = df['CH Approval Date']

    FVO = dateConversion(FVO)
    AO = dateConversion(AO)
    CH = dateConversion(CH)

    result = df.loc[(Purchase < FVO) |
                     (Purchase < AO) |
                     (Purchase < CH)]

    return result

def main():
    results = create_df()
    put_table([
            ['Merchant Name', 'Purchase Date', 'PO Item Text'],
            [results['Merchant Name'].to_string(index=False),
             results['Purchase Date'].to_string(index=False),
             results['PO Item Text'].to_string(index=False)],
        ])

app.add_url_rule('/', 'webio_view', webio_view(main),
                 methods=['GET', 'POST', 'OPTIONS'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()

    start_server(main,port=args.port)
