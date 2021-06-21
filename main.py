import glob
import os
import pandas as pd
from datetime import datetime
import time
import numpy as np

from pywebio.input import file_upload
from pywebio.output import *
from pywebio.platform.flask import webio_view
from pywebio import start_server
from flask import Flask
from pandas import ExcelWriter
from PIL import Image

# functions created for program
from webIO import userXLSXUpload as webIO_upload
from rowsIndex import createIndex as idx

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
    content = idx(content)

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

    fvo = failed.loc[(Purchase < FVO)]
    ao = failed.loc[(Purchase < AO)]
    ch = failed.loc[(Purchase < CH)]


    passed = df.loc[(Purchase > FVO) |
                     (Purchase > AO) |
                     (Purchase > CH)]

    return failed, passed, fvo, ao, ch

def main():
    failed, passed, fvo, ao, ch = create_df()
    output = 'output.xlsx'

    img = Image.open('image001.png')
    put_image(img)

    passed_count = len(passed)
    failed_count = len(failed)
    validation_count = passed_count + failed_count

    put_text('\n')
    put_text('Please find your downloaded file in the documents: ' + output)
    put_text('\n')

    put_text('Audit Count: ' + str(validation_count))
    put_text('Pass Count: ' + str(passed_count))
    put_text('Fail Count: ' + str(failed_count))
    put_text('\n')

    put_table([
        ['Department', 'Fail Count', 'Row'],
        ['FVO', len(fvo), list(fvo['Row'])],
        ['AO', len(ao), list(ao['Row'])],
        ['CH', len(ch), list(ch['Row'])]
    ])

    put_html('<h3>List of Failed Tests</h3>')
    put_table([
            ['Row', 'Merchant Name', 'Purchase Date', 'PO Item Text'],
            [failed['Row'].to_string(index=False),
             failed['Merchant Name'].to_string(index=False),
             failed['Purchase Date'].to_string(index=False),
             failed['PO Item Text'].to_string(index=False)],
        ])

    img2 = Image.open('image008.png')
    img3 = Image.open('image009.png')

    put_text('\n \n \n \n')
    put_image(img2, width='75px')
    put_image(img3, width='75px')

    #writer = pd.ExcelWriter(output)

    #failed.to_excel(writer, sheet_name='failed')
    #passed.to_excel(writer, sheet_name='passed')

    #writer.save()

app.add_url_rule('/', 'webio_view', webio_view(main),
                 methods=['GET', 'POST', 'OPTIONS'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()

    start_server(main,port=args.port, auto_open_webbrowser=True)