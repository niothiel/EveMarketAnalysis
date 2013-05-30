Eve Market Analysis
===================

A not-so-small (anymore) analysis tool that I am developing to help find profitable items to trade in Eve Online.
It is currently focused on day-trading with plans to add arbitage trading much like Eve-Central.

It is my first foray into web development with python, and any kind of significant database work.

Setup
-----
Make sure you have the following installed on your system:
* Python 2.7
* virtualenv
* pip
Directions for installing these is beyond the scope of this README, if you need any help please contact me directly.

Next, open up a terminal to the folder with the source code and execute the following:
### On Windows
```
# Create a virtual environment.
virtualenv env

# Activate the virtual environment.
env\Scripts\activate.bat

# Install required dependencies.
pip install -r requirements.txt
```

### On Linux
```
# Create a virtual environment.
virtualenv env

# Activate the virtual environment.
source env/Scripts/activate

# Install required dependencies.
pip install -r requirements.txt
```

Finally, you will need the latest eve static data in SQLITE form. This should contain all the tables from the CCP Fan Toolkit located [here](http://community.eveonline.com/community/fansites/toolkit/)

Hint: You can probably find the right sqlite database here: http://pozniak.pl/wp/?page_id=530

Run
---
After having run through the setup (Make sure you have the Eve sqlite database!), use one of the options below.

### On Windows
Open a shell in this directory, then run:
```
env\Scripts\activate.bat
python run.py
```

### On Linux
Open a shell in this directory, then run:
```
source env/Scrips/activate
python run.py
```

Once the program is started, you can navigate to [http://localhost:5000](http://localhost:5000) to check it out. Note that the price information for the trader will not be available until all of the price data has been pulled, which usually takes ~9 minutes due to Eve Central's service being slow.

Design Notes
------------
Here I have the (rough) roadmap for where I want this project to go.

Goal:
	Get rich in Eve Online through market trading.

	Types of Trade:
		Day Trading (0.01 Game)
		Long Term Trading (Trend Prediction)
		Transportation:
			Buy at A, Sell at B
			Bring Supply to Demanding Regions

	Current information:
		Buy:
			Max Buy Price
			[Min Buy Price]
			[Average Buy Price]
			Number of Buy Orders
			Number of Items to be Bought
		Sell:
			Min Sell Price
			[Max Sell Price]
			[Average Sell Price]
			Number of Sell Orders
			Number of Items to be Sold
		Time of Update
		Historical information (Volume Bought/Sold)

	Historical information:
		Buy:
			Max Buy Price
			Min Buy Price
			Average Buy Price
			Median Buy Price
			Standard Deviation
			Volume Bought
			[5%?]
		Sell:
			Max Sell Price
			Min Sell Price
			Average Sell Price
			Median Sell Price
			Standard Deviation
			Volume Sold
			[5%?]
		Aggregate fields:
			[Outlier Support]
		Time Granularity: Daily

	Scope of data:
		Station -> System -> Region
		Primary Foci:
			Jita -> Null Sec Hubs -> Amarr -> Rens -> Dodixie -> Hek

	Trade Route finder...

Historial Design
----------------
    What we have:
        orderid
        regionid
        systemid
        stationid
        typeid
        bid
        price
        minvolume
        volremain
        volenter
        issued
        duration
        rng
        reportedby
        reportedtime

    What we want:
        typeid
        stationid
        systemid
        regionid
        date
        maxbuyprice
        minbuyprice
        maxsellprice
        minsellprice
        avgbuyprice
        avgsellprice
        medbuyprice
        medsellprice
        buystddev
        sellstddev
        volbought
        volsold
        number of orders and demand
        * Num orders* and *demand*

Further Study
-------------
* Market statistics research
* Modelling Supply vs Demand
* In Game Browser integration for pulling orders