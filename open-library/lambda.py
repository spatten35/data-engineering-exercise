#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 03 11:22:01 2023

@author: sarah
"""
import boto3
from copy import deepcopy
import decimal
import json
import pandas as pd
import requests
import time
import os
import sys
from datetime import datetime
import logging


def crossJoin(left, right):
    """

    Parameters
    ----------
    left : TYPE
        Original data line
    right : TYPE
        Nested data that needs to be flattened

    Returns
    -------
    newRows : LIST
        The result rows from cartesian product.

    Logic
    -----
        Do a cartesian prduct to get all the nested data to flatten out
        so that it will be easier to convert to CSV file later

    """
    newRows = []
    for leftRow in left:
        for rightRow in right:
            tempRow = deepcopy(leftRow)
            for key, value in rightRow.items():
                tempRow[key] = value
            newRows.append(deepcopy(tempRow))
    return newRows


def findIsbn(searchTerms):
    """

    Parameters
    ----------
    searchTerms : LIST
        List of terms to search OpenLibrary for using the 'title'

    Returns
    -------
    bookIsbns : LIST
        List of ISBNs to find out more data from

    Logic
    -----
    Only the first 100 objects are included in the response for a search
    Each book object has a list of ISBNs that could be useful
    If the 'doc' has an ISBN key, the list of ISBNs is added
    to the running list of ISBNs


    """
    findBooks = "https://openlibrary.org/search.json?title="
    bookIsbns = list()
    for s in searchTerms:
        req = requests.get(findBooks + s)
        for book in json.loads(req.text)['docs']:
            if 'isbn' in book:
                bookIsbns += book['isbn']
    return bookIsbns


def flattenList(data):
    """

    Parameters
    ----------
    data : LIST
        DESCRIPTION.

    Yields
    ------
        Each element of the list

    Logic
    -----
        Move list to being flat object rather than each entry getting a new line
        'subjects' in the booksDF was originally a list, but each subject of the book
        getting its own line doesn't make sense

    """
    for elem in data:
        if isinstance(elem, list):
            yield from flattenList(elem)
        else:
            yield elem


def formatData(objs):
    """

    Parameters
    ----------
    objs : LIST of dictionaries
        List of ISBNs used as the key for /isbn API

    Returns
    -------
    pd.DataFrame : Pandas Dataframe
        A flattened version of the input JSON. Allowing for easier viewing
        of data.

    Logic
    -----
        Check format of data to determine how to flatten into single rows
        rather than keeping nested dicts and lists

    """
    def flattenJson(data, prev_heading=''):
        if isinstance(data, dict):
            rows = [{}]
            for key, value in data.items():
                rows = crossJoin(rows, flattenJson(value, prev_heading + '.' + key))
        elif isinstance(data, list):
            rows = []
            for i in range(len(data)):
                [rows.append(elem) for elem in flattenList(flattenJson(data[i], prev_heading))]
        else:
            rows = [{prev_heading[1:]: data}]
        return rows

    return pd.DataFrame(flattenJson(objs))


def handle_data_type(obj):
    """
    Convert decimal.Decimal objects into float for JSON serialization.
    """
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def getData(keys, api, baseLink):
    """

    Parameters
    ----------
    keys : LIST
        List of ISBNs used as the key for /isbn API
    api : STRING
        Which API path should be used:
            isbn/
            authors/
            books/
            works/

    Returns
    -------
    books : LIST
        List of book dictionaries from the /isbn API that redirects to /books

    Logic
    -----
        Access the /isbn API to get a list of book dictionaries

    """
    data = list()
    linkFormat = '.json'
    for key in keys:
        try:
            req = requests.get(baseLink + api + key + linkFormat)
            data.append(json.loads(req.text))
        except Exception as e:
            print(e)
    return data


def writeToS3(bucket, key, data):
    """
    Parameters
    ----------
    bucket : is a concat of bucket, date (YYYY/MM/DD), and client (i.e. google);
        this should be from the metadata table
    key : 
    data : should be a list full of dictionaries; added handle_data_type to handle floats

    Returns
    -------
    None.

    """
    s3_client = boto3.client("s3", region_name=os.environ["AWS_REGION"])
    s3_client.put_object(
        Body=data, Bucket=bucket, Key=key
    )


def handler(event, context):
    isbns = list()
    baseLink = "https://openlibrary.org/"
    keywords = ['bowling']

    isbns = list(set(findIsbn(keywords)))
    booksDF = formatData(getData(isbns, 'isbn/', baseLink=baseLink)).drop_duplicates().reset_index()
    booksDF.dropna(subset=['authors.key'], inplace=True)
    booksDF['authors.key'] = booksDF['authors.key'].apply(lambda x: x.split('/')[-1] if isinstance(x, str)  else None)
    authorsDF = formatData(getData(booksDF['authors.key'].unique(), 'authors/')).drop_duplicates().reset_index()

    # Create bridge between books and authors
    bridgeDF = booksDF[['key', 'authors.key']].copy().drop_duplicates()

    # Change column names and strip off unneeded info
    # key columns are formatted /api/keyValue
    # By splitting on '/' we'll get an array of ["", "api", "keyValue"]
    # in which we only care about the last position
    bridgeDF['key'] = bridgeDF['key'].apply(lambda x: x.split('/')[-1])
    bridgeDF.rename(columns={'key':'bookKey', 'authors.key':'authorsKey'}, inplace=True)

    # Need to drop columns
    dropAuths = ['index', 'last_modified.type', 'type.key', 'created.type',
                 'bio.type']
    authorsDF.drop(dropAuths, axis=1, inplace=True)

    dropBooks = ['index', 'last_modified.type', 'type.key', 'notes.type',
                 'description.type',
                 'first_sentence.type', 'created.type', 'works.key',
                 'authors.key']
    booksDF.drop(dropBooks, axis=1, inplace=True)


    # Format key columns / remove all but the actual key

    authorsDF['key'] = authorsDF['key'].apply(lambda x: x.split('/')[-1] if isinstance(x, str)  else None)
    booksDF['key'] = booksDF['key'].apply(lambda x: x.split('/')[-1] if isinstance(x, str)  else None)
    booksDF['languages.key'] = booksDF['languages.key'].apply(lambda x: x.split('/')[-1] if isinstance(x, str)  else None)


    # Use book Key and author Key

    outAuthors = 'authors' + time.strftime("%Y%m%d-%H%M%S") + '.csv'
    outBooks = 'books' + time.strftime("%Y%m%d-%H%M%S") + '.csv'
    outBridge = 'bridge' + time.strftime("%Y%m%d-%H%M%S") + '.csv'


    # Set up to output to S3
    today = datetime.today()
    bucket = "open-library-dummy-bucket"
    authorsKey = '/'.join(["authors", today.year, today.month, today.day, outAuthors])
    booksKey = '/'.join(["books", today.year, today.month, today.day, outBooks])
    bridgeKey = '/'.join(["bridge", today.year, today.month, today.day, outBridge])

    authors = authorsDF.to_csv()
    books = booksDF.to_csv()
    bridge = bridgeDF.to_csv()

    writeToS3(bucket=bucket, key=authorsKey, data=authors)
    writeToS3(bucket=bucket, key=booksKey, data=books)
    writeToS3(bucket=bucket, key=bridgeKey, data=bridge)

