# snpScrape

Basic script to retrieve the constituents of the S&P500 from the Wikipedia page (https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) before parsing each entry and using the ticker symbol to then obtain 5 years of pricing data for each company from Yahoo Finance (e.g. http://finance.yahoo.com/q/hp?s=MMM&a=01&b=1&c=2011&d=04&e=18&f=2016&g=d).

The script creates the file prices.csv (~65MB) that can then be used for analysis, it has the following fields:-

ticker,date,open,high,low,close,volume,adjclose,sector,subsector

i.e.

MMM,"May 18, 2016",166.5,167.88,165.75,166.88,1619000,166.88,Industrials,Industrial Conglomerates



