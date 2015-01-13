# twitter_gleaning

This is a generic version of my Snowpocalypse visualization; a dynamically scaling, interactive histogram & image gallery in D3. 

twitter_nopw.py - Python script for querying the Twitter API and storing results in a DB. This starts with the most recent results and works its way backwards in time. Currently setup to track #cxnats OR @AustinCityParks OR @usacycling.

gleanView.html - D3.js visualization of the twitter results that dynamically changes the histogram based on how many entries are in the dat file

cxnats.csv - sample data file for D3. This visualizes the response to the cancellation of the US National Cyclocross race in Austin, TX on Jan 10 2015. Check the header of this file for the field names expected by gleanView.html
