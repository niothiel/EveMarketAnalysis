EveMarketAnalysis
=================

A not-so-small (anymore) analysis tool that I am developing to help find profitable items to trade in Eve Online.

It is my first foray into web development with python, and any kind of significant database work.

Requirements:

* sqlalchemy
* flask
* flask-wtf
* Eve Static Data

Design Notes
------------

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