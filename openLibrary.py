# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 11:22:01 2020

@author: sarah
"""
from copy import deepcopy
import json
import pandas as pd
import requests
import time

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


def getData(keys, api):
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




if __name__ == '__main__':
    isbns = list()
    worksLinks = list()
    baseLink = "https://openlibrary.org/"
    keywords = ['guitar', 'physics', 'python']
    style = ".json"

    isbns = list(set(findIsbn(keywords)))
    booksDF = formatData(getData(isbns, 'isbn/')).drop_duplicates().reset_index()
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
                 'description.type', 'table_of_contents.type.key',
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

    authorsDF.to_csv(outAuthors, index=False)
    booksDF.to_csv(outBooks, index=False)
    bridgeDF.to_csv(outBridge, index=False)
