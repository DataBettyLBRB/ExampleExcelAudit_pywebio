import glob
import os
import pandas as pd
from datetime import datetime
import time
import numpy as np

from pywebio.input import file_upload
from webIO import userXLSXUpload as webIO_upload
from pywebio.output import *
from pywebio.platform.flask import webio_view
from pywebio import start_server
from flask import Flask
from pandas import ExcelWriter

import argparse

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

    failed = df.loc[(Purchase < FVO) |
                     (Purchase < AO) |
                     (Purchase < CH)]

    passed = df.loc[(Purchase > FVO) |
                     (Purchase > AO) |
                     (Purchase > CH)]

    return failed, passed

def main():
    failed, passed = create_df()
    directory = os.path.expanduser('~/Documents')
    output = directory + '/output.xlsx'

    put_text('Please find your downloaded file in the documents folder: ' + output)
    put_text('\n')

    put_table([
            ['Merchant Name', 'Purchase Date', 'PO Item Text'],
            [failed['Merchant Name'].to_string(index=False),
             failed['Purchase Date'].to_string(index=False),
             failed['PO Item Text'].to_string(index=False)],
        ])

    writer = pd.ExcelWriter(output)

    failed.to_excel(writer, sheet_name='failed')
    passed.to_excel(writer, sheet_name='passed')

    writer.save()

app.add_url_rule('/', 'webio_view', webio_view(main),
                 methods=['GET', 'POST', 'OPTIONS'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()

    start_server(main,port=args.port, auto_open_webbrowser=True)
