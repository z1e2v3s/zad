# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'zad/Designer/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(1081, 812)
        mainWindow.setSizeIncrement(QtCore.QSize(10, 10))
        self.centralwidget = QtWidgets.QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.splitter_0 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_0.setOrientation(QtCore.Qt.Vertical)
        self.splitter_0.setObjectName("splitter_0")
        self.splitter_1 = QtWidgets.QSplitter(self.splitter_0)
        self.splitter_1.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_1.setObjectName("splitter_1")
        self.box1 = QtWidgets.QGroupBox(self.splitter_1)
        self.box1.setObjectName("box1")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.box1)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.comboBoxZone_1 = QtWidgets.QComboBox(self.box1)
        self.comboBoxZone_1.setObjectName("comboBoxZone_1")
        self.verticalLayout_4.addWidget(self.comboBoxZone_1)
        self.comboBoxSub_1 = QtWidgets.QComboBox(self.box1)
        self.comboBoxSub_1.setObjectName("comboBoxSub_1")
        self.verticalLayout_4.addWidget(self.comboBoxSub_1)
        self.tableView_1 = QtWidgets.QTableView(self.box1)
        self.tableView_1.setObjectName("tableView_1")
        self.verticalLayout_4.addWidget(self.tableView_1)
        self.verticalLayout_5.addLayout(self.verticalLayout_4)
        self.box2 = QtWidgets.QGroupBox(self.splitter_1)
        self.box2.setObjectName("box2")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.box2)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.comboBoxZone_2 = QtWidgets.QComboBox(self.box2)
        self.comboBoxZone_2.setObjectName("comboBoxZone_2")
        self.verticalLayout_6.addWidget(self.comboBoxZone_2)
        self.comboBoxSub_2 = QtWidgets.QComboBox(self.box2)
        self.comboBoxSub_2.setObjectName("comboBoxSub_2")
        self.verticalLayout_6.addWidget(self.comboBoxSub_2)
        self.tableView_2 = QtWidgets.QTableView(self.box2)
        self.tableView_2.setObjectName("tableView_2")
        self.verticalLayout_6.addWidget(self.tableView_2)
        self.verticalLayout_7.addLayout(self.verticalLayout_6)
        self.box3 = QtWidgets.QGroupBox(self.splitter_1)
        self.box3.setObjectName("box3")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.box3)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.comboBoxZone_3 = QtWidgets.QComboBox(self.box3)
        self.comboBoxZone_3.setObjectName("comboBoxZone_3")
        self.verticalLayout_8.addWidget(self.comboBoxZone_3)
        self.comboBoxSub_3 = QtWidgets.QComboBox(self.box3)
        self.comboBoxSub_3.setObjectName("comboBoxSub_3")
        self.verticalLayout_8.addWidget(self.comboBoxSub_3)
        self.tableView_3 = QtWidgets.QTableView(self.box3)
        self.tableView_3.setObjectName("tableView_3")
        self.verticalLayout_8.addWidget(self.tableView_3)
        self.verticalLayout_9.addLayout(self.verticalLayout_8)
        self.splitter_2 = QtWidgets.QSplitter(self.splitter_0)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.mainBox = QtWidgets.QGroupBox(self.splitter_2)
        self.mainBox.setObjectName("mainBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.mainBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.comboBoxMainZone = QtWidgets.QComboBox(self.mainBox)
        self.comboBoxMainZone.setCurrentText("")
        self.comboBoxMainZone.setObjectName("comboBoxMainZone")
        self.verticalLayout_2.addWidget(self.comboBoxMainZone)
        self.comboBoxMainSub = QtWidgets.QComboBox(self.mainBox)
        self.comboBoxMainSub.setObjectName("comboBoxMainSub")
        self.verticalLayout_2.addWidget(self.comboBoxMainSub)
        self.maintableView = QtWidgets.QTableView(self.mainBox)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.maintableView.setFont(font)
        self.maintableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.maintableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.maintableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.maintableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.maintableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.maintableView.setObjectName("maintableView")
        self.maintableView.verticalHeader().setVisible(False)
        self.maintableView.verticalHeader().setHighlightSections(False)
        self.verticalLayout_2.addWidget(self.maintableView)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.buttonM = QtWidgets.QPushButton(self.mainBox)
        self.buttonM.setObjectName("buttonM")
        self.horizontalLayout_2.addWidget(self.buttonM)
        self.buttonP = QtWidgets.QPushButton(self.mainBox)
        self.buttonP.setObjectName("buttonP")
        self.horizontalLayout_2.addWidget(self.buttonP)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.editBox = QtWidgets.QGroupBox(self.splitter_2)
        self.editBox.setObjectName("editBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.editBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.nameAddressLabel = QtWidgets.QLabel(self.editBox)
        self.nameAddressLabel.setObjectName("nameAddressLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.nameAddressLabel)
        self.nameAddressEdit = QtWidgets.QLineEdit(self.editBox)
        self.nameAddressEdit.setObjectName("nameAddressEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.nameAddressEdit)
        self.ttlLabel = QtWidgets.QLabel(self.editBox)
        self.ttlLabel.setObjectName("ttlLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.ttlLabel)
        self.ttlEdit = QtWidgets.QLineEdit(self.editBox)
        self.ttlEdit.setObjectName("ttlEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.ttlEdit)
        self.typeLabel = QtWidgets.QLabel(self.editBox)
        self.typeLabel.setObjectName("typeLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.typeLabel)
        self.typeEdit = QtWidgets.QLineEdit(self.editBox)
        self.typeEdit.setObjectName("typeEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.typeEdit)
        self.rdataLabel = QtWidgets.QLabel(self.editBox)
        self.rdataLabel.setObjectName("rdataLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.rdataLabel)
        self.rdataEdit = QtWidgets.QTextEdit(self.editBox)
        self.rdataEdit.setObjectName("rdataEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.rdataEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.buttonReset = QtWidgets.QPushButton(self.editBox)
        self.buttonReset.setObjectName("buttonReset")
        self.horizontalLayout.addWidget(self.buttonReset)
        self.buttonOK = QtWidgets.QPushButton(self.editBox)
        self.buttonOK.setObjectName("buttonOK")
        self.horizontalLayout.addWidget(self.buttonOK)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_3.addWidget(self.splitter_0)
        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1081, 22))
        self.menubar.setObjectName("menubar")
        self.menuZad = QtWidgets.QMenu(self.menubar)
        self.menuZad.setObjectName("menuZad")
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(mainWindow)
        self.statusbar.setObjectName("statusbar")
        mainWindow.setStatusBar(self.statusbar)
        self.actionAbout = QtWidgets.QAction(mainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionSettings = QtWidgets.QAction(mainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.actionZones = QtWidgets.QAction(mainWindow)
        self.actionZones.setObjectName("actionZones")
        self.menuZad.addAction(self.actionAbout)
        self.menuZad.addAction(self.actionSettings)
        self.menuZad.addAction(self.actionZones)
        self.menubar.addAction(self.menuZad.menuAction())

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "MainWindow"))
        self.box1.setTitle(_translate("mainWindow", "Domain-Zone"))
        self.box2.setTitle(_translate("mainWindow", "IPv4-Zone"))
        self.box3.setTitle(_translate("mainWindow", "IPv6-Zone"))
        self.mainBox.setTitle(_translate("mainWindow", "Edit-Zone"))
        self.buttonM.setText(_translate("mainWindow", "-"))
        self.buttonP.setText(_translate("mainWindow", "+"))
        self.editBox.setTitle(_translate("mainWindow", "Editor"))
        self.nameAddressLabel.setText(_translate("mainWindow", "Name/Address"))
        self.ttlLabel.setText(_translate("mainWindow", "TTL"))
        self.typeLabel.setText(_translate("mainWindow", "Type"))
        self.rdataLabel.setText(_translate("mainWindow", "Rdata"))
        self.buttonReset.setText(_translate("mainWindow", "Reset"))
        self.buttonOK.setText(_translate("mainWindow", "OK"))
        self.menuZad.setTitle(_translate("mainWindow", "zad"))
        self.actionAbout.setText(_translate("mainWindow", "About"))
        self.actionSettings.setText(_translate("mainWindow", "Settings"))
        self.actionZones.setText(_translate("mainWindow", "Zones"))
