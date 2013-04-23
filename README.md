EveMarketAnalysis
=================

Quick analysis tool I wrote to find profitable items to trade in Eve Online

Requirements:

PyQt4
MySQLdb

Optionally, you will require an installation of MySQL somewhere for finer-grained order information.


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
			Jita -> TVN-FM -> Amarr -> Rens -> Dodixie -> Hek

	Trade Route finder...

Design Decisions:
	Language
	Database

Historial Design:
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
		* Num orders* and *demand*

Statistics research
How to model Supply vs Demand?
In Game Browser upload to Eve Central for up-to-date information.