# -*- coding: utf-8 -*-
"""
Created on Wed May 18 10:51:50 2016

@author: cameronsim
"""

import requests
from bs4 import BeautifulSoup
import numpy as np
import datetime
import csv

CONTITUENTS_SITE = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
YAHOO_SITE_URL = "http://finance.yahoo.com/q/hp?s="
OUTPUT_FILE_NAME="prices.csv"
#locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )

def snpCompanies():
    """ Scrap list of S&P 500 constituents from Wikipedia and return list of symbols 
    """
    r = requests.get(CONTITUENTS_SITE)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table', {'class': 'wikitable sortable'})
    list=[]    
    
    for row in table.findAll('tr'):
        col=row.findAll('td')
        
        if len(col) > 0:

            ticker=col[0].find('a').string.strip()
            name=col[1].find('a').string.strip()
            sector=col[3].string.strip()
            subSector=col[4].string.strip()
            
            #accounts for multiple a links in the column (i.e. <a>London</a>, <a>United Kingdom</a>)
            try:
                location=col[5].string.strip().split(',')
                town=location[0]
                state=location[1]
            except:
                location=col[5].findAll('a')
                town=location[0].string.strip()

                # Some towns like Washington D.C don't have states
                if len(location)>1:
                    state=location[1].string.strip()
                else:
                    state=town

            list.append({
                'ticker':ticker,
                'name':name,
                'sector':sector,
                'subSector':subSector,
                'town':town,
                'state':state 
            })

    return list


def scrapeYahooWithUrl(url=None, ticker=None):
    """ Scrapes pricing data from Yahoo Finance given a specific url """
    print "scrapeYahooWithUrl : " + url
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    table_outer = soup.find('table', {'class': 'yfnc_datamodoutline1'})
    
    try:    
    
        table_inner = table_outer.findAll('table') 
        
        col_headers=['ticker']
        formats = [np.dtype('a12'),np.dtype('a12'),np.dtype('float16'),
                   np.dtype('float16'),np.dtype('float16'),np.dtype('float16'),
                   np.dtype('int32'),np.dtype('float16')]    
        
        # Get the column headers (date, open, close, high, low, etc)
        for th in table_inner[0].findAll('th',{'class': 'yfnc_tablehead1'}) :
            col_headers.append(th.string.strip())
            
        dtype = dict(names = col_headers, formats=formats)
        
        results=[]    
            
        for row in table_inner[0].findAll('tr'):
            col=row.findAll('td',{'class': 'yfnc_tabledata1'})
            if len(col)>2:
                date=col[0].string.strip()
                open=float(str(col[1].string.strip()).translate(None,','))
                high=float(str(col[2].string.strip()).translate(None,','))
                low=float(str(col[3].string.strip()).translate(None,','))
                close=float(str(col[4].string.strip()).translate(None,','))
                volume=int(str(col[5].string.strip()).translate(None,','))
                adjclose=float(str(col[6].string.strip()).translate(None,','))
                
                values=np.array([(ticker,date,open,high,low,close,volume,adjclose)],dtype=dtype)
                
                results.append(values)
        
        return np.array(results, dtype=dtype)
    except:
        #print "unable to retrieve data for ticker:"+ticker+ " and url:"+url
        """ Thrown when no more rows are on the web page """
        pass
    

def pricingForTicker(ticker=None, startDate=None, endDate=None):
    """ iterate over the paging and get the 5 year pricing data for a given ticker"""    
        
    lastTickerDate=endDate
    resultsPerPage=66
    pagingCount=0
    
    pagingUrl=YAHOO_SITE_URL+ticker+'&a='+str(startDate.day)+'&b='+str(startDate.month)+'&c='+str(startDate.year)+\
    '&d='+str(endDate.day)+'&e='+str(endDate.month)+'&f='+str(endDate.year)+'&z=66&y='
    
    totalResults=[]
    
    while lastTickerDate > startDate:
        
        results=scrapeYahooWithUrl(url=pagingUrl+str(pagingCount), ticker=ticker)
    
        if results is not None:
            dateStringForLastRow=results[len(results)-1][0][1]
            lastTickerDate=datetime.datetime.strptime(dateStringForLastRow, "%b %d, %Y").date()
            totalResults.append(results)
        else:
            break
        
        pagingCount=pagingCount+resultsPerPage
   
    return totalResults

        
def createPricesFile(companyList=None, startDate=None, endDate=None):
    """ Iterates over the list of companies scraped from Wikipedia 
        and for each one, calls @pricingForTicker() with the start and end dates 
    """
    
    with open(OUTPUT_FILE_NAME,"w") as output:
        csv_out=csv.writer(output)
        csv_out.writerow(['ticker','date','open','high','low','close','volume','adjclose','sector','subsector'])

        for t in companyList:
            results=pricingForTicker(ticker=t['ticker'], startDate=startDate, endDate=endDate)        
            for page in results:
                for row in page:
                    csv_out.writerow(tuple(row[0])+(t['sector'], t['subSector']))


if __name__ == "__main__":
    companiesList=snpCompanies()

    startDate = datetime.date(2011,1,1)
    endDate = datetime.datetime.today().date()
    createPricesFile(companyList=companiesList,startDate=startDate, endDate=endDate)
    
    # TEST METHOD CALL FOR ONE STOCK
    #createPricesFile(companyList=[{"ticker":"GOOG","sector":"Technology","subSector":"computers"}],startDate=startDate, endDate=endDate)
    
    print "completed"





            