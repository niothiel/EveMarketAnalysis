from bson.code import Code
from pymongo import MongoClient
from pprint import pprint

def get_orders_in_jita():
	db = MongoClient().evec

	map = Code(
		'function() {'
		'   var x = this.volremain;'
		#'   var key = {'
		#'       orderid: this.orderid'
		#'       typeid: this.typeid,'
		#'       bid: this.bid,'
		#'       regionid: this.regionid,'
		#'       systemid: this.systemid,'
		#'       stationid: this.stationid'
		#'   };'
		'   var value = {'
		#'       regionid: this.regionid,'
		#'       systemid: this.systemid,'
		#'       stationid: this.stationid,'
		#'       typeid: this.typeid,'
		#'       bid: this.bid,'
		#'       price: this.price,'
		'       '
		'       minvolume: x,'
		'       maxvolume: x'
		'   };'
		'   emit(this.orderid,value);'
		'}'
	)

	reduce = Code(
		'function(key, values) {'
			'var res = values[0];'
			'var sumprice = 0.0;'
			'for(var i = 1; i < values.length; i++) {'
			'   if(values[i].minvolume < res.minvolume)'
			'       res.min = values[i].minvolume;'
			'   if(values[i].maxvolume > res.maxvolume)'
			'       res.maxvolume = values[i].maxvolume;'
			'   sumprice += values[i].price;'
			'}'
			'res.price = sumprice / values.length;'
			'return res;'
		'}'
	)
	if 'testdump_inter' in db.collection_names():
		db.testdump_inter.drop()

	results = db.testdump.map_reduce(map, reduce, out='testdump_inter')
	for result in results.find():
		print result

def main():
	get_orders_in_jita()
	return

	client = MongoClient()
	db = client.evec

	map = Code(
		'function() {'
		'   var x = this.volremain;'
		'   emit({orderid:this.orderid,typeid:this.typeid},{min:x, max:x});'
		'}'
	)

	reduce = Code(
		'function(key, values) {'
			'var res = values[0];'
			'for(var i = 1; i < values.length; i++) {'
			'   if(values[i].min < res.min)'
			'       res.min = values[i].min;'
			'   if(values[i].max > res.max)'
			'       res.max = values[i].max;'
			'}'
			'return res;'
		'}'
	)

	map2 = Code(
		'function() {'
		'   var difference = this.value.max - this.value.min;'
		'   if(difference > 0)'
		'       emit(this[\'_id\'][\'typeid\'], {soldvolume: difference});'
		'}'
	)

	reduce2 = Code(
		'function(key, values) {'
		'   var sum = 0;'
		'   values.forEach(function(v) {'
		'       sum += v.soldvolume;'
		'   });'
		'   return {soldvolume: sum};'
		'}'
	)

	#if 'testdump_inter' in db.collection_names():
	#	db.testdump_inter.drop()
	#result = db.testdump.map_reduce(map, reduce, out='testdump_inter', query={'regionid': 10000002})

	#if 'testdump_final' in db.collection_names():
	#	db.testdump_final.drop()
	#result = db.testdump_inter.map_reduce(map2, reduce2, 'testdump_final')
	#for doc in result.find():
	#	print doc

	for record in db.testdump_final.find():
		record.update(record['value'])
		del record['value']
		print record

		db.testdump_final.save(record)

	'''
	# Benchmark for element iteration.
	print 'Starting iteration, element count:', db.testdump_final.count()
	n = 0
	for doc in db.testdump_final.find():
		n += 1
		if n % 100 == 0:
			print n
	'''

if __name__ == '__main__':
	main()