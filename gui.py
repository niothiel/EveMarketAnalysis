from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
from market.marketbuilder import getItems
from util import formatIsk
from market.evecentral import EveCentral
import PyQt4
import sys

class PriceListWindow(QDialog):
	def __init__(self, parent, typeId):
		QDialog.__init__(self, parent)
		self.typeId = typeId

		self.initUI()

	def initUI(self):
		mainLayout = QVBoxLayout(self)
		mainWidget = QWidget(self)
		mainWidget.setLayout(mainLayout)

		minProfit = QLabel('Min. Profit:')

		self.minProfitEdit = QDoubleSpinBox()
		self.minProfitEdit.setAccelerated(True)
		self.minProfitEdit.setMaximum(10000000000)

		maxProfit = QLabel('Max Profit:')

		self.maxProfitEdit = QDoubleSpinBox()
		self.maxProfitEdit.setAccelerated(True)
		self.maxProfitEdit.setMaximum(10000000000)

		maxInvestment = QLabel('Max Investment:')

		self.maxInvestmentEdit = QDoubleSpinBox()
		self.maxInvestmentEdit.setAccelerated(True)
		self.maxInvestmentEdit.setMaximum(10000000000)

		minOrders = QLabel('Min Orders:')

		self.minOrdersEdit = QDoubleSpinBox()
		self.minOrdersEdit.setAccelerated(True)
		self.minOrdersEdit.setMaximum(10000000000)

		maxOrders = QLabel('Max Orders:')

		self.maxOrdersEdit = QDoubleSpinBox()
		self.maxOrdersEdit.setAccelerated(True)
		self.maxOrdersEdit.setMaximum(10000000000)

		minPrice = QLabel('Min Price:')

		self.minPriceEdit = QDoubleSpinBox()
		self.minPriceEdit.setAccelerated(True)
		self.minPriceEdit.setMaximum(10000000000)

		columnNames = ['Name', 'Buy (Isk)', 'Sell (Isk)', 'Profit (%)', 'Total Sold']
		table = QTableWidget(2, len(columnNames), self)
		table.setHorizontalHeaderLabels(columnNames)
		table.verticalHeader().hide()
		table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		table.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.table = table

		refreshButton = QPushButton('Refresh')

		form = QFormLayout()
		form.addRow('Min. Profit:', self.minProfitEdit)
		form.addRow('Max Profit:', self.maxProfitEdit)

		grid = QGridLayout()
		grid.addWidget(minProfit, 0, 0)
		grid.addWidget(self.minProfitEdit, 0, 1)
		grid.addWidget(maxProfit, 1, 0)
		grid.addWidget(self.maxProfitEdit, 1, 1)
		grid.addWidget(maxInvestment, 2, 0)
		grid.addWidget(self.maxInvestmentEdit, 2, 1)
		grid.addWidget(minOrders, 3, 0)
		grid.addWidget(self.minOrdersEdit, 3, 1)
		grid.addWidget(maxOrders, 4, 0)
		grid.addWidget(self.maxOrdersEdit, 4, 1)
		grid.addWidget(minPrice, 5, 0)
		grid.addWidget(self.minPriceEdit, 5, 1)

		mainLayout.addLayout(grid)
		#mainLayout.addLayout(form)
		mainLayout.addWidget(table)
		mainLayout.addWidget(refreshButton)

		self.setCentralWidget(mainWidget)
		self.setGeometry(100, 100, 800, 500)
		self.setWindowTitle('Eve Market Analyzer')
		self.statusBar().showMessage('Status Bar')
		self.show()

class FormattedWidgetItem(QTableWidgetItem):
	# Types for the fields
	T_ISK = 0
	T_NUMBER = 1
	T_PERCENT = 2
	T_OTHER = 3

	def __init__(self, item, type, get_data_func):
		super(FormattedWidgetItem, self).__init__()
		self.item = item
		self.type = type
		self.get_data_func = get_data_func

	def __getData(self):
		return self.get_data_func(self.item)

	def data(self, p_int):
		if p_int == Qt.DisplayRole:
			data = self.__getData()

			if self.type == FormattedWidgetItem.T_ISK:
				return formatIsk(data)
			elif self.type == FormattedWidgetItem.T_NUMBER:
				return '%.0f' % data
			elif self.type == FormattedWidgetItem.T_PERCENT:
				print data
				return '%.1f%%' % data
			else:
				return data
		else:
			return QTableWidgetItem.data(self, p_int)

	# Another weird hack for sorting data. Sorts based on item (order) attribute
	def __lt__(self, other):
		return self.__getData() < other.__getData()

class MainView(QMainWindow):
	def __init__(self):
		super(MainView, self).__init__()
		self.initUI()
		self.setCullValues()

		#self.items = getItems()

	def refresh(self):
		self.statusBar().showMessage('Retrieving item prices: 0%')
		#self.items = getItems(callbackFunc= lambda pct: self.statusBar().showMessage('Retrieving item prices: %.0f%%' % (pct * 100)))

		#skill_books = []
		#with open('asdf.csv', 'r') as fin:
		#	for line in fin:
		#		skill_books.append(int(line))

		#print len(skill_books), skill_books
		#self.items = getItems(skill_books)
		self.items = EveCentral.getPrices()
		self.updateTable()
		self.statusBar().showMessage('Update completed!')

	def setCullValues(self):
		# Eventually will have to retain old settings
		self.minProfitEdit.setValue(10)
		self.maxProfitEdit.setValue(105)
		self.maxInvestmentEdit.setValue(20000000)
		self.minOrdersEdit.setValue(120)
		self.maxOrdersEdit.setValue(6000)
		self.minPriceEdit.setValue(500000)

	def itemsFilter(self, item):
		priceDifference = 0
		if item.buy.volume <> 0 and item.buy.max <> 0 and item.sell.volume <> 0 and item.sell.min <> 0:
			priceDifference = abs(item.buy.max - item.sell.min) / item.buy.max * 100

		if priceDifference < self.minProfitEdit.value():
			return False
		elif priceDifference > self.maxProfitEdit.value():
			return False
		elif item.buy.max > self.maxInvestmentEdit.value():
			return False
		elif item.sell.volume < self.minOrdersEdit.value():
			return False
		elif item.sell.volume > self.maxOrdersEdit.value():
			return False
		elif item.buy.max < self.minPriceEdit.value():
			return False

		if item.buy.max > item.sell.min:
			return False
		elif item.buy.max < 1:
			return False
		elif item.sell.min < 1:
			return False
		elif item.all.volume < 1:
			return False
		#elif item.volumeDifference > 75:
		#    return False

		return True

	def updateTable(self):
		# Disable sorting as this screws everything up while adding data.
		self.table.setSortingEnabled(False)

		# Filter out the crap
		self.items = filter(self.itemsFilter, self.items.itervalues())

		viewedItems = len(self.items)
		self.table.setRowCount(viewedItems)
		tempItems = self.items[:viewedItems]

		row = 0
		for item in tempItems:
			name = QTableWidgetItem(str(item.name))

			buyPrice = FormattedWidgetItem(item, FormattedWidgetItem.T_ISK, lambda item: item.buy.max)
			sellPrice = FormattedWidgetItem(item, FormattedWidgetItem.T_ISK, lambda item: item.sell.min)
			print abs(item.buy.max - item.sell.min) / float(item.buy.min)
			profit = FormattedWidgetItem(item, FormattedWidgetItem.T_PERCENT, lambda item: (abs(item.buy.max - item.sell.min) / float(item.buy.min)))
			totalSold = FormattedWidgetItem(item, FormattedWidgetItem.T_NUMBER, lambda item: item.all.volume)
			ranking = FormattedWidgetItem(item, FormattedWidgetItem.T_NUMBER, lambda item: abs(item.sell.min - item.buy.max) / item.sell.min)

			# Populate with typeId for retrieval
			typeId = item.id
			name.setData(PyQt4.QtCore.Qt.UserRole, typeId)
			buyPrice.setData(PyQt4.QtCore.Qt.UserRole, typeId)
			sellPrice.setData(PyQt4.QtCore.Qt.UserRole, typeId)
			profit.setData(PyQt4.QtCore.Qt.UserRole, typeId)
			totalSold.setData(PyQt4.QtCore.Qt.UserRole, typeId)
			ranking.setData(PyQt4.QtCore.Qt.UserRole, typeId)

			self.table.setItem(row, 0, name)
			self.table.setItem(row, 1, buyPrice)
			self.table.setItem(row, 2, sellPrice)
			self.table.setItem(row, 3, profit)
			self.table.setItem(row, 4, totalSold)
			self.table.setItem(row, 5, ranking)
			row += 1

		self.table.setSortingEnabled(True)
		self.table.sortItems(3, Qt.DescendingOrder)
		self.table.resizeColumnsToContents()
		self.table.resizeRowsToContents()

	def initUI(self):
		mainLayout = QVBoxLayout(self)
		mainWidget = QWidget(self)
		mainWidget.setLayout(mainLayout)

		minProfit = QLabel('Min. Profit:')

		self.minProfitEdit = QDoubleSpinBox()
		self.minProfitEdit.setAccelerated(True)
		self.minProfitEdit.setMaximum(10000000000)

		maxProfit = QLabel('Max Profit:')

		self.maxProfitEdit = QDoubleSpinBox()
		self.maxProfitEdit.setAccelerated(True)
		self.maxProfitEdit.setMaximum(10000000000)

		maxInvestment = QLabel('Max Investment:')

		self.maxInvestmentEdit = QDoubleSpinBox()
		self.maxInvestmentEdit.setAccelerated(True)
		self.maxInvestmentEdit.setMaximum(10000000000)

		minOrders = QLabel('Min Orders:')

		self.minOrdersEdit = QDoubleSpinBox()
		self.minOrdersEdit.setAccelerated(True)
		self.minOrdersEdit.setMaximum(10000000000)

		maxOrders = QLabel('Max Orders:')

		self.maxOrdersEdit = QDoubleSpinBox()
		self.maxOrdersEdit.setAccelerated(True)
		self.maxOrdersEdit.setMaximum(10000000000)

		minPrice = QLabel('Min Price:')

		self.minPriceEdit = QDoubleSpinBox()
		self.minPriceEdit.setAccelerated(True)
		self.minPriceEdit.setMaximum(10000000000)

		columnNames = ['Name', 'Buy (Isk)', 'Sell (Isk)', 'Profit (%)', 'Total Sold', 'Ranking']
		table = QTableWidget(2, len(columnNames), self)
		table.setHorizontalHeaderLabels(columnNames)
		table.verticalHeader().hide()
		table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		table.setSelectionBehavior(QAbstractItemView.SelectRows)
		table.cellDoubleClicked.connect(self.onDoubleClick)
		self.table = table

		refreshButton = QPushButton('Refresh')
		refreshButton.clicked.connect(self.refresh)

		form = QFormLayout()
		form.addRow('Min. Profit:', self.minProfitEdit)
		form.addRow('Max Profit:', self.maxProfitEdit)

		grid = QGridLayout()
		grid.addWidget(minProfit, 0, 0)
		grid.addWidget(self.minProfitEdit, 0, 1)
		grid.addWidget(maxProfit, 1, 0)
		grid.addWidget(self.maxProfitEdit, 1, 1)
		grid.addWidget(maxInvestment, 2, 0)
		grid.addWidget(self.maxInvestmentEdit, 2, 1)
		grid.addWidget(minOrders, 3, 0)
		grid.addWidget(self.minOrdersEdit, 3, 1)
		grid.addWidget(maxOrders, 4, 0)
		grid.addWidget(self.maxOrdersEdit, 4, 1)
		grid.addWidget(minPrice, 5, 0)
		grid.addWidget(self.minPriceEdit, 5, 1)

		mainLayout.addLayout(grid)
		#mainLayout.addLayout(form)
		mainLayout.addWidget(table)
		mainLayout.addWidget(refreshButton)

		self.setCentralWidget(mainWidget)
		self.setGeometry(100, 100, 800, 500)
		self.setWindowTitle('Eve Market Analyzer')
		self.statusBar().showMessage('Status Bar')
		self.show()

	def onDoubleClick(self, row, col):
		print "Clicked cell:", row, col

		typeId = self.table.item(row, col).data(Qt.UserRole).toInt()[0]
		print typeId

		priceWindow = PriceListWindow(self, typeId)
		priceWindow.exec_()

def main():
	app = QApplication(sys.argv)
	mainView = MainView()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()