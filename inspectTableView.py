# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt,QDate
from PyQt5.QtSql import *
from PyQt5.QtPrintSupport import QPrinter,QPrintDialog,QPageSetupDialog
import sqlite3
import xlrd
import xlwt
from xlwt import *
from jinja2 import Template
from addinspectDialog import addInspectDialog
from modInspectDialog import modInspectDialog
import datetime

from PyQt5.QtGui import QIcon

class InspectTableView(QWidget):
    queryCondition2 = "SELECT * FROM inspect"
    db = None

    def __init__(self):
        super(InspectTableView,self).__init__()
        self.resize(1000, 715)
        self.setWindowTitle("Check the statistics system")

        self.queryModel = None

        self.tableView = None

        self.currentPage = 0

        self.totalPage = 0
  
        self.totalRecord = 0
  
        self.pageRecord = 15
        self.printer = QPrinter()
        self.editor = QtWidgets.QTextEdit(self)
        self.editor.hide()
        self.setUpUI()

    def setUpUI(self):
        self.layout = QVBoxLayout()
        self.Hlayout2 = QHBoxLayout()
        self.Vlayout1 = QVBoxLayout()
        self.grid_layout = QGridLayout()

        # Hlayout1
        self.searchEdit = QLineEdit()
        self.searchEdit.setFixedHeight(32)
        self.font = QFont()
        self.font.setPixelSize(14)
        self.searchEdit.setFont(self.font)

        self.searchButton = QPushButton("") 
        self.searchButton.setFixedHeight(80)
        self.searchButton.setFixedWidth(80)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.searchButton.setIcon(icon)

        self.searchButton.setIconSize(QtCore.QSize(50, 50))

        self.displayLabel = QLabel("Rectification inspection record")
        font2 = QFont()
        font2.setPixelSize(25)
        self.displayLabel.setFont(font2)
        self.displayLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.condisionComboBox = QComboBox()
        searchCondision = ['Auditor', 'Rectification ', 'Location', 'Department ']
        self.condisionComboBox.setFixedHeight(32)
        self.condisionComboBox.setFont(self.font)
        self.condisionComboBox.addItems(searchCondision)
        
        self.grid_layout.addWidget(self.condisionComboBox,0,0,1,1)
        self.grid_layout.addWidget(self.searchEdit,0,1,1,21)
        
        # Hlayout2
        self.rbAll = QRadioButton('All',self)
        self.rbAll.setFont(self.font)
        
        self.rbAll.setChecked(True)
      
        self.rbAll.toggled.connect(self.rbclicked)
        self.dateStartLabel = QLabel("Start")
        self.dateStartLabel.setFont(self.font)
        self.dateEndLabel = QLabel("End")
        self.dateEndLabel.setFont(self.font)
        self.refreshInspectbtn = QPushButton("") 
        self.refreshInspectbtn.setToolTip("Refresh")
        self.refreshInspectbtn.setIcon(QIcon(QPixmap("images/inspect.png")))
        self.addInspectbtn = QPushButton("")
        self.addInspectbtn.setToolTip("Add")
        self.addInspectbtn.setIcon(QIcon(QPixmap("images/add.png")))
        self.updtaInspectbtn = QPushButton("")
        self.updtaInspectbtn.setToolTip("Update")
        self.updtaInspectbtn.setIcon(QIcon(QPixmap("images/alter.png")))
        self.delInspectbtn = QPushButton("")
        self.delInspectbtn.setToolTip("Delete")
        self.delInspectbtn.setIcon(QIcon(QPixmap("images/del.png")))
        self.prtInspectbtn = QPushButton("")
        self.prtInspectbtn.setToolTip("Print")
        self.prtInspectbtn.setIcon(QIcon(QPixmap("images/print2.png")))
        self.prtSetupbtn = QPushButton("")
        self.prtSetupbtn.setToolTip("Printer settings")
        self.prtSetupbtn.setIcon(QIcon(QPixmap("images/inspect.png")))
        self.impExcelbtn = QPushButton("") 
        self.impExcelbtn.setToolTip("Import Excel")
        self.impExcelbtn.setIcon(QIcon(QPixmap("images/input.png")))
        self.xptExcelbtn = QPushButton("") 
        self.xptExcelbtn.setToolTip("Export to Excel")
        self.xptExcelbtn.setIcon(QIcon(QPixmap("images/output.png")))
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.jumpToLabel = QLabel("Jump to")
        self.jumpToLabel.setFont(self.font)
        self.pageEdit = QLineEdit()
        self.pageEdit.setFixedWidth(30)
        self.pageEdit.setFont(self.font)
        s = "/" + str(self.totalPage) + "page"
        self.pageLabel = QLabel(s)
        self.pageLabel.setFont(self.font)
        self.jumpToButton = QPushButton("")
        self.jumpToButton.setToolTip("Jump")
        self.jumpToButton.setIcon(QIcon(QPixmap("images/jump.png")))
        self.prevButton = QPushButton("")
        self.prevButton.setToolTip("previous page")
        self.prevButton.setIcon(QIcon(QPixmap("images/pageup.png")))
        self.backButton = QPushButton("")
        self.backButton.setToolTip("next page")
        self.backButton.setIcon(QIcon(QPixmap("images/pagedown.png")))

        
        self.min_date = QDate.currentDate()
        self.max_date = QDate.currentDate()
        query = QSqlQuery()
        if not query.exec_('SELECT MIN(date) AS Min_Date,MAX(date) AS Max_Date from inspect'):
            query.lastError()
        else:
            while query.next():
                self.min_date = QDate.fromString(query.value(0),'yyyy/MM/dd')
                self.max_date = QDate.fromString(query.value(1),'yyyy/MM/dd')

      
        self.dateStartLabel.setFont(self.font)
        self.dateStartLabel.setFixedHeight(32)
        self.dateStartLabel.setFixedWidth(80)
        self.dateEndLabel.setFont(self.font)
        self.dateEndLabel.setFixedHeight(32)
        self.dateEndLabel.setFixedWidth(80)
        self.dateStartEdit = QDateTimeEdit(self.min_date, self)
        self.dateEndEdit = QDateTimeEdit(self.max_date, self)
        self.dateStartEdit.setEnabled(not self.rbAll.isChecked())
        self.dateEndEdit.setEnabled(not self.rbAll.isChecked())
        self.dateStartEdit.setFont(self.font)
        self.dateStartEdit.setFixedHeight(32)
        self.dateStartEdit.setFixedWidth(200)
        self.dateEndEdit.setFont(self.font)
        self.dateEndEdit.setFixedHeight(32)
        self.dateEndEdit.setFixedWidth(200)
        self.dateStartEdit.setMinimumDate(self.min_date)
        self.dateStartEdit.setMaximumDate(self.max_date)
        self.dateEndEdit.setMinimumDate(self.min_date)
        self.dateEndEdit.setMaximumDate(self.max_date)

        
        self.dateStartEdit.dateChanged.connect(self.onStartDateChanged)
        self.dateEndEdit.dateChanged.connect(self.onEndDateChanged)

       
        self.dateStartEdit.setCalendarPopup(True)
        self.dateEndEdit.setCalendarPopup(True)

        self.tableView = QTableView()
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.queryModel = QSqlQueryModel()
        self.searchButtonClicked()
        
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(self.refreshInspectbtn)
        Hlayout.addWidget(self.addInspectbtn)
        Hlayout.addWidget(self.updtaInspectbtn)
        Hlayout.addWidget(self.delInspectbtn)
        Hlayout.addWidget(self.prtInspectbtn)
        Hlayout.addWidget(self.prtSetupbtn)
        Hlayout.addWidget(self.impExcelbtn)
        Hlayout.addWidget(self.xptExcelbtn)
        Hlayout.addItem(spacerItem)
        Hlayout.addWidget(self.jumpToLabel)
        Hlayout.addWidget(self.pageEdit)
        Hlayout.addWidget(self.pageLabel)
        Hlayout.addWidget(self.jumpToButton)
        Hlayout.addWidget(self.prevButton)
        Hlayout.addWidget(self.backButton)
        widget = QWidget()
        widget.setLayout(Hlayout)
        widget.setFixedWidth(900)
        self.grid_layout.addWidget(self.rbAll,1,0,1,1)
        self.grid_layout.addWidget(self.dateStartLabel,1,1,1,1)
        self.grid_layout.addWidget(self.dateStartEdit,1,2,1,1)
        self.grid_layout.addWidget(self.dateEndLabel,1,20,1,1)
        self.grid_layout.addWidget(self.dateEndEdit,1,21,1,1)
        self.grid_layout.addWidget(self.searchButton,0,24,2,2)
        self.Hlayout2.addWidget(widget)

    
        self.dateStartEdit.setDisplayFormat("yyyy/MM/dd")
        self.dateEndEdit.setDisplayFormat("yyyy/MM/dd")
        
        self.tableView.setModel(self.queryModel)

        self.queryModel.setHeaderData(0, Qt.Horizontal, "Serial number")
        self.queryModel.setHeaderData(1, Qt.Horizontal, "Auditor")
        self.queryModel.setHeaderData(2, Qt.Horizontal, "Inspection")
        self.queryModel.setHeaderData(3, Qt.Horizontal, "Date")
        self.queryModel.setHeaderData(4, Qt.Horizontal, "Location")
        self.queryModel.setHeaderData(5, Qt.Horizontal, "Department")
        self.queryModel.setHeaderData(6, Qt.Horizontal, "Remarks")
        self.tableView.setColumnHidden(0, True)
        
        #self.layout.addLayout(self.Hlayout4)
        self.layout.addLayout(self.grid_layout)
        self.layout.addWidget(self.displayLabel)
        self.layout.addWidget(self.tableView)
        self.layout.addLayout(self.Hlayout2)
        self.setLayout(self.layout)

        self.searchButton.clicked.connect(self.searchButtonClicked)
        self.prevButton.clicked.connect(self.prevButtonClicked)
        self.backButton.clicked.connect(self.backButtonClicked)
        self.jumpToButton.clicked.connect(self.jumpToButtonClicked)
        self.searchEdit.returnPressed.connect(self.searchButtonClicked)

        self.childaddmeeting = addDialog()
        self.refreshInspectbtn.clicked.connect(self.rfs_row_data)
        self.addInspectbtn.clicked.connect(self.add_row_data)
        self.updtaInspectbtn.clicked.connect(self.mod_row_data)
        self.delInspectbtn.clicked.connect(self.del_row_data)
        self.prtInspectbtn.clicked.connect(self.prt_row_data)
        self.prtSetupbtn.clicked.connect(self.prt_setup_data)
        self.impExcelbtn.clicked.connect(self.imp_excel_data)
        self.xptExcelbtn.clicked.connect(self.xpt_excel_data)


    def validate_date(self,date_text):
        try:
            datetime.datetime.strptime(str(date_text), '%Y/%m/%d')
        except ValueError:
            return False
        return True
    
    @QtCore.pyqtSlot()
    def rbclicked(self):
        self.dateStartEdit.setEnabled(not self.rbAll.isChecked())
        self.dateEndEdit.setEnabled(not self.rbAll.isChecked())
        self.searchButtonClicked()

    @QtCore.pyqtSlot()
    def rfs_row_data(self):
        self.searchEdit.clear()
        self.dateStartEdit.setDate(self.min_date)
        self.dateEndEdit.setDate(self.max_date)
        self.condisionComboBox.setCurrentIndex(0)
        self.rbAll.setChecked(True)
        self.dateStartEdit.setEnabled(not self.rbAll.isChecked())
        self.dateEndEdit.setEnabled(not self.rbAll.isChecked())
        self.searchButtonClicked()


    @QtCore.pyqtSlot()
    def add_row_data(self):
        model = self.tableView.model()
        while(model.canFetchMore()):
            model.fetchMore()
        id = model.rowCount()
        addInspectDialog = addDialog()
        addInspectDialog.show()
        if(addInspectDialog.exec_() == 1):
            name = addInspectDialog.txtName.text().strip()
            inspDetils = addInspectDialog.txtInspect.text().strip()
            date = addInspectDialog.dateEdit.date().toString('yyyy/MM/dd')
            address = addInspectDialog.txtAddress.text().strip()
            joinDep = addInspectDialog.txtWithPeople.text().strip()
            remark = addInspectDialog.txtComment.text().strip()
            if name != "":
                query = QSqlQuery()
                query.exec_("INSERT INTO inspect(id,name,inspDetils,date,address,joinDep,remark) SELECT MAX(id) + 1,'{0}','{1}','{2}','{3}','{4}','{5}' FROM inspect".format(name,inspDetils,date,address,joinDep,remark))
                if addInspectDialog.dateEdit.date() < self.min_date:
                    self.min_date = addInspectDialog.dateEdit.date()
                    self.dateStartEdit.setMinimumDate(self.min_date)
                if addInspectDialog.dateEdit.date() > self.max_date:
                    self.max_date = addInspectDialog.dateEdit.date()
                    self.dateEndEdit.setMaximumDate(self.max_date)
                self.searchButtonClicked2()
                QMessageBox.question(self, "Success","The new check is successful!",QMessageBox.Ok)
        else:
            if addInspectDialog.dateEdit.date() < self.min_date:
                self.min_date = addInspectDialog.dateEdit.date()
                self.dateStartEdit.setMinimumDate(self.min_date)
            if addInspectDialog.dateEdit.date() > self.max_date:
                self.max_date = addInspectDialog.dateEdit.date()
                self.dateEndEdit.setMaximumDate(self.max_date)
            self.searchButtonClicked2()


    @QtCore.pyqtSlot()
    def mod_row_data(self):
        try:
            index = self.tableView.currentIndex()
            if not index.isValid():
                QMessageBox.critical(self, "Error","Please select the check record!",QMessageBox.Ok)
                return
            rows = self.tableView.selectionModel().selectedIndexes()
            id = self.queryModel.record(rows[0].row()).value("id")
            name = self.queryModel.record(rows[0].row()).value("name")
            inspect = self.queryModel.record(rows[0].row()).value("inspDetils")
            date = self.queryModel.record(rows[0].row()).value("date")
            address = self.queryModel.record(rows[0].row()).value("address")
            joinDep = self.queryModel.record(rows[0].row()).value("joinDep")
            remark = self.queryModel.record(rows[0].row()).value("remark")
            modInspectDialog = modDialog()
            modInspectDialog.id = id
            modInspectDialog.txtName.setText(str(name))
            modInspectDialog.txtInspect.setText(str(inspect))
            if self.validate_date(date):
                modInspectDialog.dateEdit.setDateTime(datetime.datetime.strptime(date,"%Y/%m/%d"))
            modInspectDialog.txtAddress.setText(str(address))
            modInspectDialog.txtWithPeople.setText(str(joinDep))
            modInspectDialog.txtComment.setText(str(remark))
            modInspectDialog.show()
            if(modInspectDialog.exec_() == 1):
                rows = self.tableView.selectionModel().selectedIndexes()
                id = self.queryModel.record(rows[0].row()).value("id")
                name = modInspectDialog.txtName.text().strip()
                inspect = modInspectDialog.txtInspect.text().strip()
                date = modInspectDialog.dateEdit.date().toString('yyyy/MM/dd')
                address = modInspectDialog.txtAddress.text().strip()
                joinDep = modInspectDialog.txtWithPeople.text().strip()
                remark = modInspectDialog.txtComment.text().strip()
        
                if name != "":
                    query = QSqlQuery()
                    query.exec_("UPDATE inspect SET name = '{1}', inspDetils = '{2}', date = '{3}', address = '{4}', joinDep = '{5}', remark = '{6}' WHERE id = {0}".format(id,name,inspect,date,address,joinDep,remark))

                    if modInspectDialog.dateEdit.date() < self.min_date:
                        self.min_date = modInspectDialog.dateEdit.date()
                        self.dateStartEdit.setMinimumDate(self.min_date)
                    if modInspectDialog.dateEdit.date() > self.max_date:
                        self.max_date = modInspectDialog.dateEdit.date()
                        self.dateEndEdit.setMaximumDate(self.max_date)
                    self.searchButtonClicked2()
                    QMessageBox.question(self, "Success","The modification check is successful!",QMessageBox.Ok)
            else:
                if modInspectDialog.dateEdit.date() < self.min_date:
                    self.min_date = modInspectDialog.dateEdit.date()
                    self.dateStartEdit.setMinimumDate(self.min_date)
                if modInspectDialog.dateEdit.date() > self.max_date:
                    self.max_date = modInspectDialog.dateEdit.date()
                    self.dateEndEdit.setMaximumDate(self.max_date)
                self.searchButtonClicked2()
        except Exception as e:
            QMessageBox.critical(self, "Error","Please select the check record!",QMessageBox.Ok)
            return


    @QtCore.pyqtSlot()
    def del_row_data(self):
        try:
            index = self.tableView.currentIndex()
            if not index.isValid():
                QMessageBox.critical(self, "Error","Please select check record!",QMessageBox.Ok)
                return
            rows = set()
            for idx in self.tableView.selectedIndexes():
                record = self.queryModel.record(idx.row())
                id = record.value("id")
                rows.add(id)
            if (QMessageBox.question(self, "Warning","Are you sure?",QMessageBox.Yes | QMessageBox.No) == QMessageBox.No):
                return
            query = QSqlQuery()
            for id in rows:
                query.exec_("DELETE FROM inspect WHERE id = {0}".format(id))
            self.searchButtonClicked2()
        except Exception as e:
            QMessageBox.critical(self, "Error","Please select check record!",QMessageBox.Ok)
            return

    def setButtonStatus(self):
        if (self.currentPage == 1 and self.totalPage == 1):
            self.prevButton.setEnabled(False)
            self.backButton.setEnabled(False)
        elif (self.currentPage > 1 and self.currentPage == self.totalPage):
            self.prevButton.setEnabled(True)
            self.backButton.setEnabled(False)
        elif (self.currentPage == 1 and self.currentPage < self.totalPage):
            self.prevButton.setEnabled(False)
            self.backButton.setEnabled(True)
        elif (self.currentPage > 1 and self.currentPage < self.totalPage):
            self.prevButton.setEnabled(True)
            self.backButton.setEnabled(True)



    def getTotalRecordCount(self):
        self.queryModel.setQuery(self.queryCondition2)
        while(self.queryModel.canFetchMore()):
            self.queryModel.fetchMore()
        self.totalRecord = self.queryModel.rowCount()
        return



    def getPageCount(self):
        self.getTotalRecordCount()

        self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
        return



    def recordQuery(self, index):
        queryCondition = ""
        conditionChoice = self.condisionComboBox.currentText()
        if (conditionChoice == "Auditor"):
            conditionChoice = 'name'
        elif (conditionChoice == "Rectification"):
            conditionChoice = 'inspectDetils'
        elif (conditionChoice == 'Location'):
            conditionChoice = 'address'
        else:
            conditionChoice = 'joinDep'

        if (self.searchEdit.text() == ""):
            if self.rbAll.isChecked():
                queryCondition = "SELECT * FROM inspect"
            else:
                queryCondition = "SELECT * FROM inspect WHERE date BETWEEN '%s' AND '%s'" % (self.dateStartEdit.dateTime().toString('yyyy/MM/dd'),self.dateEndEdit.dateTime().toString('yyyy/MM/dd'))
            self.queryModel.setQuery(queryCondition)
            while(self.queryModel.canFetchMore()):
                self.queryModel.fetchMore()
            self.totalRecord = self.queryModel.rowCount()
            self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
            label = "/" + str(int(self.totalPage)) + "page"
            self.pageLabel.setText(label)
            if self.rbAll.isChecked():
                queryCondition = ("SELECT * FROM inspect ORDER BY id limit %d,%d " % (index, self.pageRecord))
                self.queryCondition2 = ("SELECT * FROM inspect WHERE date BETWEEN '%s' AND '%s' ORDER BY id" % (self.dateStartEdit.dateTime().toString('yyyy/MM/dd'),self.dateEndEdit.dateTime().toString('yyyy/MM/dd')))
            else:
                queryCondition = ("SELECT * FROM inspect WHERE date BETWEEN '%s' AND '%s' ORDER BY id limit %d,%d " % (self.dateStartEdit.dateTime().toString('yyyy/MM/dd'),self.dateEndEdit.dateTime().toString('yyyy/MM/dd'), index, self.pageRecord))
                self.queryCondition2 = ("SELECT * FROM inspect WHERE date BETWEEN '%s' AND '%s' ORDER BY id" % (self.dateStartEdit.dateTime().toString('yyyy/MM/dd'),self.dateEndEdit.dateTime().toString('yyyy/MM/dd')))
            self.queryModel.setQuery(queryCondition)
            self.setButtonStatus()
            return

 
        temp = self.searchEdit.text()
        s = '%'
        for i in range(0, len(temp)):
            s = s + temp[i] + "%"
        if self.rbAll.isChecked():
            queryCondition = ("SELECT * FROM inspect WHERE %s LIKE '%s' ORDER BY id" % (conditionChoice,s))
        else:
            queryCondition = ("SELECT * FROM inspect WHERE %s LIKE '%s' AND date BETWEEN '%s' AND '%s' ORDER BY id" % (conditionChoice, s,self.dateStartEdit.dateTime().toString('yyyy/MM/dd'),self.dateEndEdit.dateTime().toString('yyyy/MM/dd')))
        self.queryModel.setQuery(queryCondition)
        while(self.queryModel.canFetchMore()):
            self.queryModel.fetchMore()
        self.totalRecord = self.queryModel.rowCount()

        if (self.totalRecord == 0):
            QMessageBox.information(self, "Warning", "No record found", QMessageBox.Yes, QMessageBox.Yes)
            if self.rbAll.isChecked():
                queryCondition = "SELECT * FROM inspect ORDER BY id"
            else:
                queryCondition = "SELECT * FROM inspect WHERE date BETWEEN '%s' AND '%s' ORDER BY id" % (self.dateStartEdit.dateTime().toString('yyyy/MM/dd'),self.dateEndEdit.dateTime().toString('yyyy/MM/dd'))
            self.queryModel.setQuery(queryCondition)
            while(self.queryModel.canFetchMore()):
                self.queryModel.fetchMore()
            self.totalRecord = self.queryModel.rowCount()
            self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
            label = "/" + str(int(self.totalPage)) + "page"
            self.pageLabel.setText(label)
            if self.rbAll.isChecked():
                queryCondition = ("SELECT * FROM inspect ORDER BY id limit %d,%d " % (index, self.pageRecord))
                self.queryCondition2 = "SELECT * FROM inspect ORDER BY id"
            else:
                queryCondition = ("SELECT * FROM inspect WHERE date BETWEEN '%s' AND '%s' ORDER BY id limit %d,%d " % (self.dateStartEdit.dateTime().toString('yyyy/MM/dd'),self.dateEndEdit.dateTime().toString('yyyy/MM/dd'), index, self.pageRecord))
                self.queryCondition2 = ("SELECT * FROM inspect WHERE date BETWEEN '%s' AND '%s' ORDER BY id" % (self.dateStartEdit.dateTime().toString('yyyy/MM/dd'),self.dateEndEdit.dateTime().toString('yyyy/MM/dd')))
            self.queryModel.setQuery(queryCondition)
            self.setButtonStatus()
            return
        self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
        label = "/" + str(int(self.totalPage)) + "page"
        self.pageLabel.setText(label)
        if self.rbAll.isChecked():
            queryCondition = ("SELECT * FROM inspect WHERE %s LIKE '%s' ORDER BY id LIMIT %d,%d " % (conditionChoice, s, index, self.pageRecord))
            self.queryCondition2 = ("SELECT * FROM inspect WHERE %s LIKE '%s' ORDER BY id" % (conditionChoice,s))
        else:
            queryCondition = ("SELECT * FROM inspect WHERE %s LIKE '%s' AND date BETWEEN '%s' AND '%s' ORDER BY id LIMIT %d,%d " % (conditionChoice, s,self.dateStartEdit.dateTime().toString('yyyy/MM/dd'),self.dateEndEdit.dateTime().toString('yyyy/MM/dd'), index, self.pageRecord))
            self.queryCondition2 = ("SELECT * FROM inspect WHERE %s LIKE '%s' AND date BETWEEN '%s' AND '%s' ORDER BY id" % (conditionChoice, s,self.dateStartEdit.dateTime().toString('yyyy/MM/dd'),self.dateEndEdit.dateTime().toString('yyyy/MM/dd')))
        self.queryModel.setQuery(queryCondition)
        self.setButtonStatus()
        return

    def searchButtonClicked(self):
        self.currentPage = 1
        self.pageEdit.setText(str(self.currentPage))
        self.getPageCount()
        s = "/" + str(int(self.totalPage)) + "page"
        self.pageLabel.setText(s)
        index = (self.currentPage - 1) * self.pageRecord
        self.recordQuery(index)
        return



    def searchButtonClicked2(self):
        self.pageEdit.setText(str(self.currentPage))
        self.getPageCount()
        s = "/" + str(int(self.totalPage)) + "page"
        self.pageLabel.setText(s)
        index = (self.currentPage - 1) * self.pageRecord
        self.recordQuery(index)
        return


    def prevButtonClicked(self):
        self.currentPage -= 1
        if (self.currentPage <= 1):
            self.currentPage = 1
        self.pageEdit.setText(str(self.currentPage))
        index = (self.currentPage - 1) * self.pageRecord
        self.recordQuery(index)
        return



    def backButtonClicked(self):
        self.currentPage += 1
        if (self.currentPage >= int(self.totalPage)):
            self.currentPage = int(self.totalPage)
        self.pageEdit.setText(str(self.currentPage))
        index = (self.currentPage - 1) * self.pageRecord
        self.recordQuery(index)
        return



    def jumpToButtonClicked(self):
        if (self.pageEdit.text().isdigit()):
            self.currentPage = int(self.pageEdit.text())
            if (self.currentPage > self.totalPage):
                self.currentPage = self.totalPage
            if (self.currentPage <= 1):
                self.currentPage = 1
        else:
            self.currentPage = 1
        index = (self.currentPage - 1) * self.pageRecord
        self.pageEdit.setText(str(self.currentPage))
        self.recordQuery(index)
        return


    @QtCore.pyqtSlot()
    def prt_row_data(self):

        printdialog = QPrintDialog(self.printer,self)

        if QDialog.Accepted == printdialog.exec_():
            c = sqlite3.connect('cmdb.sqlite')
            cur = c.cursor()
            cur.execute(self.queryCondition2)
            test = cur.fetchall()
            template = Template("""
            <table border="1" cellspacing="0" cellpadding="2">
              <tr>
                <th>Auditor</th>
                <th>Inspection</th>
                <th>Date</th>
                <th>Location</th>
                <th>Department</th>
                <th>Remarks</th>
              </tr> 
              {% for row in test %}
              <tr>
                <td> {{ row[1] if row[1] != None }}</td>
                <td max-width="50%"> {{ row[2] if row[2] != None }}</td>
                <td> {{ row[3] if row[3] != None }}</td>
                <td max-width="50%"> {{ row[4] if row[4] != None }}</td>
                <td> {{ row[5] if row[5] != None }}</td>
                <td> {{ row[6] if row[6] != None }}</td>
              </tr> 
              {% endfor %}
            </table>
            """)
            text = template.render(test=test)
            self.editor.setHtml(text)
            self.editor.document().print_(printdialog.printer())
            cur.close()
            c.close()
            QMessageBox.question(self, "Success","The rectification inspection form has been submitted for printing!",QMessageBox.Ok)

    def prt_setup_data(self):
        printsetdialog = QPageSetupDialog(self.printer,self)
        printsetdialog.exec_()


    @QtCore.pyqtSlot()
    def imp_excel_data(self):
        fileName, filetype = QFileDialog.getOpenFileName(self,
                                    "Import Excel file",
                                    "./",
                                    "Excel Files (*.xls)")  
        if fileName != "":
            if(self.readExcelFile(fileName)):

                self.min_date = QDate.currentDate()
                self.max_date = QDate.currentDate()
                query = QSqlQuery()
                if not query.exec_('SELECT MIN(date) AS Min_Date,MAX(date) AS Max_Date from inspect'):
                    query.lastError()
                else:
                    QMessageBox.question(self, "Success","Import the Excel file successfully!",QMessageBox.Ok)
                    while query.next():
                        self.min_date = QDate.fromString(query.value(0),'yyyy/MM/dd')
                        self.max_date = QDate.fromString(query.value(1),'yyyy/MM/dd')

                    self.dateStartEdit.setMinimumDate(self.min_date)
                    self.dateStartEdit.setMaximumDate(self.max_date)
                    self.dateEndEdit.setMinimumDate(self.min_date)
                    self.dateEndEdit.setMaximumDate(self.max_date)
                    self.searchButtonClicked()
            else:
                QMessageBox.critical(self, "Error","The Excel file format is wrong!",QMessageBox.Ok)


    def insert(self,name,inspDetils,date,address,joinDep,remark):
        sql = "insert into inspect(name,inspDetils,date,address,joinDep,remark) values ('%s','%s','%s','%s','%s','%s')" % (name,inspDetils,date,address,joinDep,remark)
        self.cursor.execute(sql)

    def readExcelFile(self, file):
        data = xlrd.open_workbook(file)
        for sheet in data.sheets():
            if sheet.name == 'inspect':
                conn = sqlite3.connect('cmdb.sqlite')
                self.cursor = conn.cursor()
                for rowId in range(1, sheet.nrows):
                    row = sheet.row_values(rowId)
                    if row:
                        self.insert(row[1],row[2],row[3],row[4],row[5],row[6])
                conn.commit()
                self.cursor.close()
                conn.close()
                return True
        return False
    
    @QtCore.pyqtSlot()
    def sqlite_get_col_names(self,cur, select_sql):
        cur.execute(select_sql)
        return [tuple[0] for tuple in cur.description]

    @QtCore.pyqtSlot()
    def query_by_sql(self,cur, select_sql):
        cur.execute(select_sql)
        return cur.fetchall()


    def len_byte(self,value):
        length = len(value)
        utf8_length = len(value.encode('utf-8'))
        length = (utf8_length - length) / 2 + length
        return int(length)
                
    @QtCore.pyqtSlot()
    def sqlite_to_workbook_with_head(self,cur, table, select_sql, workbook,style):
        ws = workbook.add_sheet(table)
    
        for colx, heading in enumerate(self.sqlite_get_col_names(cur, select_sql)):
            ws.write(0, colx, self.queryModel.headerData(colx,Qt.Horizontal),style)   
            

        id = 1

        col_width = []
        for rowy, row in enumerate(self.query_by_sql(cur, select_sql)):
            for colx, text in enumerate(row):    
                t = id if colx == 0 else text
                ws.write(rowy + 1,colx , t,style)    
                if rowy == 0:
                    col_width.append(self.len_byte(str(t)))
                elif col_width[colx] < self.len_byte(str(t)):
                    col_width[colx] = self.len_byte(str(t))
            id+=1


        for i in range(len(col_width)):
            if col_width[i] > 10:
                ws.col(i).width = 256 * col_width[i] 

  
    @QtCore.pyqtSlot()
    def xpt_excel_data(self):
        fileName, filetype = QFileDialog.getSaveFileName(self,
                                    "Export Excel file",
                                    "./",
                                    "Excel Files (*.xls)")   
        if fileName != "":
            c = sqlite3.connect('cmdb.sqlite')
            cur = c.cursor()
            select_sql = self.queryCondition2
            borders = xlwt.Borders()
            borders.left = xlwt.Borders.THIN
            borders.right = xlwt.Borders.THIN
            borders.top = xlwt.Borders.THIN
            borders.bottom = xlwt.Borders.THIN
            style1 = xlwt.XFStyle()
            style1.borders = borders
            workbook = xlwt.Workbook(encoding='utf-8')

            self.sqlite_to_workbook_with_head(cur, 'inspect', select_sql, workbook,style1)
            cur.close()
            c.close()
            workbook.save(fileName)
            QMessageBox.question(self, "Success","Successfully exported the Excel file!",QMessageBox.Ok)


    def onStartDateChanged(self,date):
        self.dateEndEdit.setMinimumDate(date)
        self.searchButtonClicked()

    def onEndDateChanged(self,date):
        self.dateStartEdit.setMaximumDate(date)
        self.searchButtonClicked()

class addDialog(addInspectDialog):
     def __init__(self):
         super(addDialog,self).__init__()
         self.setUpUI()

class modDialog(modInspectDialog):
     def __init__(self):
         super(modDialog,self).__init__()
         self.setUpUI()