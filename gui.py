from PyQt4.QtGui import *
from request import getItems
import PyQt4
import sys

class MainView(QMainWindow):
    def __init__(self):
        super(MainView, self).__init__()
        self.initUI()
        self.setCullValues()
        
        #self.items = getItems()
    
    def refresh(self):
        self.items = getItems(callbackFunc= lambda pct: self.statusBar().showMessage('Retrieving item prices: %.0f%%' % (pct * 100)))
        self.updateTable()
        self.statusBar().showMessage('Update completed!')
        
    def setCullValues(self):
        # Eventually will have to retain old settings
        self.minProfitEdit.setValue(15)
        self.maxProfitEdit.setValue(75)
        self.maxInvestmentEdit.setValue(5000000)
        self.minOrdersEdit.setValue(120)
        self.maxOrdersEdit.setValue(6000)
        self.minPriceEdit.setValue(90000)
        
    def itemsFilter(self, item):
        if item.priceDifference < self.minProfitEdit.value():
            return False
        elif item.priceDifference > self.maxProfitEdit.value():
            return False
        elif item.buyPrice > self.maxInvestmentEdit.value():
            return False
        elif item.soldOrders < self.minOrdersEdit.value():
            return False
        elif item.soldOrders > self.maxOrdersEdit.value():
            return False
        elif item.buyPrice < self.minPriceEdit.value():
            return False
        
        if item.buyPrice > item.sellPrice:
            return False
        elif item.buyPrice < 1:
            return False
        elif item.sellPrice < 1:
            return False
        elif item.soldOrders < 1:
            return False
        elif item.volumeDifference > 75:
            return False

        return True
    
    def updateTable(self):
        # Disable sorting as this screws everything up while adding data.
        self.table.setSortingEnabled(False)
        
        # Filter out the crap
        self.items = filter(self.itemsFilter, self.items)
        
        viewedItems = len(self.items)
        self.table.setRowCount(viewedItems)
        tempItems = self.items[:viewedItems]
        
        row = 0
        for item in tempItems:
            name = QTableWidgetItem(str(item.name))
            buyPrice = QTableWidgetItem()
            sellPrice = QTableWidgetItem()
            profit = QTableWidgetItem()
            totalSold = QTableWidgetItem()
            
            # Weird hack to enable sorting by int (What the fuck, Qt?)
            buyPrice.setData(PyQt4.QtCore.Qt.DisplayRole, item.buyPrice)
            sellPrice.setData(PyQt4.QtCore.Qt.DisplayRole, item.sellPrice)
            profit.setData(PyQt4.QtCore.Qt.DisplayRole, item.priceDifference)
            totalSold.setData(PyQt4.QtCore.Qt.DisplayRole, item.soldOrders)
            
            # Populate with typeId for retrieval
            typeId = item.typeId
            name.setData(PyQt4.QtCore.Qt.UserRole, typeId)
            buyPrice.setData(PyQt4.QtCore.Qt.UserRole, typeId)
            sellPrice.setData(PyQt4.QtCore.Qt.UserRole, typeId)
            profit.setData(PyQt4.QtCore.Qt.UserRole, typeId)
            totalSold.setData(PyQt4.QtCore.Qt.UserRole, typeId)
            
            self.table.setItem(row, 0, name)
            self.table.setItem(row, 1, buyPrice)
            self.table.setItem(row, 2, sellPrice)
            self.table.setItem(row, 3, profit)
            self.table.setItem(row, 4, totalSold)
            row += 1
        
        self.table.setSortingEnabled(True)
    
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

def main():
    app = QApplication(sys.argv)
    mainView = MainView()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()