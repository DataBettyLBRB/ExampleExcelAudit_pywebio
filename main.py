import glob
import os
import pandas as pd
from datetime import datetime
import time
import numpy as np
import re

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

pd.set_option('display.max_row', 3000)
pd.set_option('display.min_rows', 3000)
pd.set_option('display.width', 700)
pd.set_option('display.max_columns', 10)
pd.set_option('display.expand_frame_repr', True)

app = Flask(__name__)


# get files from filepath
def getFiles(path):
    return glob.glob(path)


# convert strings to dates
def dateConversion(column):
    return column.astype('datetime64[ns]')


def increment_greater_than(col):
    if col > 1000:
        return round(col/1000)*1000
    else:
        return 0


def personal_items(col):
    if col == 'AMAZON':
        return 1
    if col == 'SUPPLIES':
        return 1
    if col == 'BOOK':
        return 1
    if 'AIRPODS' in col:
        return 1
    if 'AMAZON - SUPPLIES' in col:
        return 1
    if 'AMAZON SUPPLIES' in col:
        return 1
    if 'APPLE WATCH' in col:
        return 1
    if 'PHONE CASE' in col:
        return 1
    if 'CASES FOR' in col:
        return 1
    if 'OTTERBOX' in col:
        return 1
    if 'PHONE COVER' in col:
        return 1
    if 'Not assigned' in col:
        return 1
    if 'REOCCURRING' in col:
        return 1
    if re.search('AMAZON - SUPPLIES*', col):
        return 1
    if re.search('OFFICE SUPPLIES*', col):
        return 1
    if re.search('CHARGER*', col):
        return 1
    if re.search('^MISC*', col):
        return 1
    else:
        return 0


def main():
    content = webIO_upload()
    content = idx(content)

    frame = content[~content['PO Item Short Text'].str.contains('Not assigned', na=False)]
    returns = content[content['PO Item Short Text'].str.contains('Not assigned', na=False)]

    df = pd.DataFrame(frame)

    df['increment'] = [increment_greater_than(col['$']) for idx, col in df.iterrows()]
    df['personal_purchase_flag'] = [personal_items(col['PO Item Short Text']) for idx, col in df.iterrows()]

    increment_greater = df[df['increment'] > 0]
    increment_count = len(increment_greater[increment_greater['increment'] > 0])
    increment_cost = increment_greater['$'].sum()

    increment_group1 = pd.DataFrame(increment_greater.groupby(['increment'])['Row'].count().reset_index())
    increment_group1.columns = ['increment', 'count']
    increment_group1['increment'] = increment_group1['increment'].values.astype(str)

    increment_group2 = pd.DataFrame(increment_greater.groupby(['increment'])['Row']
                                    .apply(list)).reset_index()
    increment_group2['increment'] = increment_group2['increment'].values.astype(str)
    increment_group = pd.merge(increment_group1, increment_group2, on='increment')

    personal_greater_than = df[df['personal_purchase_flag'] > 0]
    personal_count = len(personal_greater_than[personal_greater_than['personal_purchase_flag'] > 0])
    personal_cost = personal_greater_than['$'].sum()

    Purchase = df['Transaction Date']
    FVO = df['FVO Approval Date']
    AO = df['AO Approval Date']
    CH = df['CH Approval Date']

    Purchase = dateConversion(Purchase)
    FVO = dateConversion(FVO)
    AO = dateConversion(AO)
    CH = dateConversion(CH)

    failed_dates = df.loc[(Purchase < FVO) |
                    (Purchase < AO) |
                    (Purchase < CH)]

    fvo = failed_dates.loc[(Purchase < FVO)]
    ao = failed_dates.loc[(Purchase < AO)]
    ch = failed_dates.loc[(Purchase < CH)]

    df.loc[(Purchase < FVO) | (Purchase < AO) | (Purchase < CH), 'data_validation'] = 1
    df.loc[(Purchase >= FVO) & (Purchase >= AO) & (Purchase >= CH), 'data_validation'] = 0

    passed = df.loc[(df['increment'] == 0) & (df['personal_purchase_flag'] == 0) & (df['data_validation'] == 0)]
    failed = df.loc[(df['increment'] != 0) | (df['personal_purchase_flag'] != 0) | (df['data_validation'] != 0)]

    img = Image.open('image001.png')
    put_image(img)

    validation_count = len(df)
    passed_count = len(passed)
    failed_count = len(failed)

    put_text('Audit Count: ' + str(validation_count))
    put_text('Passed Validations Count: ' + str(passed_count))
    put_text('Flagged Validations Count: ' + str(failed_count))
    put_text('\n')

    put_html('<h3>Flagged Count For Each Test</h3>')
    put_table([
        ['Reason', 'Count', 'Cost'],
        ['Validation Dates', len(failed_dates), round(sum(df['$']))],
        ['Personal Purchases', personal_count, personal_cost],
        ['Purchase > $1,000', increment_count, round(increment_cost)]
    ])

    put_html('<h3>Flagged Greater than $1,000 by Increment</h3>')
    put_table([
        ['Increment', 'Count', 'Rows'],
        [increment_group['increment'].to_string(index=False),
         increment_group['count'].to_string(index=False),
         increment_group['Row'].to_string(index=False)]
    ])

    put_html('<h3>Flagged For Validation Dates</h3>')
    put_html('<h6>For transactions purchased prior to approval from (FVO, AO, CH)</h6>')
    put_table([
        ['Department', 'Fail Count', 'Row'],
        ['FVO', len(fvo), list(fvo['Row'])],
        ['AO', len(ao), list(ao['Row'])],
        ['CH', len(ch), list(ch['Row'])]
    ])

    put_html('<h3>List of Failed Tests</h3>')

    img2 = Image.open('image008.png')
    img3 = Image.open('corinth.png')

    put_text('\n')
    put_image(img2, width='85px')
    put_image(img3, width='225px')

    # writer = pd.ExcelWriter(output)

    # failed.to_excel(writer, sheet_name='failed')
    # passed.to_excel(writer, sheet_name='passed')

    # writer.save()


app.add_url_rule('/', 'webio_view', webio_view(main),
                 methods=['GET', 'POST', 'OPTIONS'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()

    start_server(main, port=args.port, auto_open_webbrowser=True)
