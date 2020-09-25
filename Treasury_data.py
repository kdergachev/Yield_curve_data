# -*- coding: utf-8 -*-

import requests as rq
from lxml import html
from bs4 import BeautifulSoup as bs
import datetime
import pandas as pd
import os
import numpy as np


def __get_factors(terms):

    result = []
    for i in terms:
        term = i.split(" ")
        if term[1] == "mo":
            result.append(int(term[0])/12)
        elif term[1] == "yr":
            result.append(int(term[0]))
        else:
            print("!!!unrecognised term!!!")
    return result

def get_all_yields(how="plain"):

    """how: "plain" or "corresponding" """

    #get the table element from html of the site
    req = rq.get((r"https://www.treasury.gov/resource-center/data-chart-center"
                  + r"/interest-rates/Pages/TextView.aspx?data=yieldAll"))

    tree = bs(req.text, features="lxml")
    tree = tree.find("table", {'class': 't-chart'})
    #parse the table
    result = {}
    for i in tree.findAll("tr"):
        data = []
        #go through each row and get all entries, replace N/A with nan and try to convert to float
        for j in (i.findAll("td") + i.findAll("th")):
            if "N/A" in j.text:
                value = np.nan
            else:
                try:
                    value = float(j.text)/100
                except:
                    value = j.text
            data.append(value)
        #entry for the dict which will become the data frame
        result[data[0]] = data[1:]
    #final tweaks to the data frame
    result = pd.DataFrame.from_dict(result, "index")
    result.columns = result.loc["Date", :]
    result = result.drop("Date")
    result.index = pd.to_datetime(result.index)
    if how == "corresponding":
        factors = __get_factors(result.columns)
        for i in range(len(result.columns)):
            # turn into APR first
            result.iloc[:, i] = (1 + result.iloc[:, i]/2)**2 - 1
            # then multiply/divide to get to proper term
            result.iloc[:, i] = result.iloc[:, i] * factors[i]
    return result

# TODO: add interpolation

if __name__ == "__main__":
    test = get_all_yields(how="corresponding")



