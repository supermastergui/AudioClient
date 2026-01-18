# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pilot_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QTabWidget, QVBoxLayout, QWidget)

from src.ui.component.selected_button import SelectedButton

class Ui_ClientWindow(object):
    def setupUi(self, ClientWindow):
        if not ClientWindow.objectName():
            ClientWindow.setObjectName(u"ClientWindow")
        ClientWindow.resize(790, 413)
        font = QFont()
        font.setFamilies([u"Leelawadee UI"])
        font.setPointSize(10)
        ClientWindow.setFont(font)
        self.gridLayout_2 = QGridLayout(ClientWindow)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.group_com = QGroupBox(ClientWindow)
        self.group_com.setObjectName(u"group_com")
        self.group_com.setFont(font)
        self.gridLayout_3 = QGridLayout(self.group_com)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.layout_coms = QGridLayout()
        self.layout_coms.setObjectName(u"layout_coms")
        self.button_com2_tx = SelectedButton(self.group_com)
        self.button_com2_tx.setObjectName(u"button_com2_tx")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_com2_tx.sizePolicy().hasHeightForWidth())
        self.button_com2_tx.setSizePolicy(sizePolicy)

        self.layout_coms.addWidget(self.button_com2_tx, 1, 2, 1, 1)

        self.button_com1_rx = SelectedButton(self.group_com)
        self.button_com1_rx.setObjectName(u"button_com1_rx")
        sizePolicy.setHeightForWidth(self.button_com1_rx.sizePolicy().hasHeightForWidth())
        self.button_com1_rx.setSizePolicy(sizePolicy)

        self.layout_coms.addWidget(self.button_com1_rx, 0, 3, 1, 1)

        self.label_com2_freq = QLabel(self.group_com)
        self.label_com2_freq.setObjectName(u"label_com2_freq")
        self.label_com2_freq.setMinimumSize(QSize(100, 0))
        font1 = QFont()
        font1.setFamilies([u"Leelawadee UI"])
        font1.setPointSize(12)
        self.label_com2_freq.setFont(font1)

        self.layout_coms.addWidget(self.label_com2_freq, 1, 1, 1, 1)

        self.label_com2 = QLabel(self.group_com)
        self.label_com2.setObjectName(u"label_com2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_com2.sizePolicy().hasHeightForWidth())
        self.label_com2.setSizePolicy(sizePolicy1)
        self.label_com2.setMinimumSize(QSize(80, 0))
        self.label_com2.setFont(font1)

        self.layout_coms.addWidget(self.label_com2, 1, 0, 1, 1)

        self.button_com1_tx = SelectedButton(self.group_com)
        self.button_com1_tx.setObjectName(u"button_com1_tx")
        sizePolicy.setHeightForWidth(self.button_com1_tx.sizePolicy().hasHeightForWidth())
        self.button_com1_tx.setSizePolicy(sizePolicy)

        self.layout_coms.addWidget(self.button_com1_tx, 0, 2, 1, 1)

        self.label_com1 = QLabel(self.group_com)
        self.label_com1.setObjectName(u"label_com1")
        sizePolicy1.setHeightForWidth(self.label_com1.sizePolicy().hasHeightForWidth())
        self.label_com1.setSizePolicy(sizePolicy1)
        self.label_com1.setMinimumSize(QSize(80, 0))
        self.label_com1.setFont(font1)

        self.layout_coms.addWidget(self.label_com1, 0, 0, 1, 1)

        self.label_com1_freq = QLabel(self.group_com)
        self.label_com1_freq.setObjectName(u"label_com1_freq")
        self.label_com1_freq.setMinimumSize(QSize(100, 0))
        self.label_com1_freq.setFont(font1)

        self.layout_coms.addWidget(self.label_com1_freq, 0, 1, 1, 1)

        self.button_com2_rx = SelectedButton(self.group_com)
        self.button_com2_rx.setObjectName(u"button_com2_rx")
        sizePolicy.setHeightForWidth(self.button_com2_rx.sizePolicy().hasHeightForWidth())
        self.button_com2_rx.setSizePolicy(sizePolicy)

        self.layout_coms.addWidget(self.button_com2_rx, 1, 3, 1, 1)


        self.gridLayout_3.addLayout(self.layout_coms, 0, 0, 1, 1)

        self.spacer_1 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.spacer_1, 0, 1, 1, 1)


        self.gridLayout_2.addWidget(self.group_com, 0, 0, 1, 1)

        self.group_controllers = QGroupBox(ClientWindow)
        self.group_controllers.setObjectName(u"group_controllers")
        self.group_controllers.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.group_controllers.sizePolicy().hasHeightForWidth())
        self.group_controllers.setSizePolicy(sizePolicy1)
        self.group_controllers.setFont(font)
        self.verticalLayout = QVBoxLayout(self.group_controllers)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.layout_unicom = QHBoxLayout()
        self.layout_unicom.setObjectName(u"layout_unicom")
        self.label_unicom = QLabel(self.group_controllers)
        self.label_unicom.setObjectName(u"label_unicom")
        sizePolicy1.setHeightForWidth(self.label_unicom.sizePolicy().hasHeightForWidth())
        self.label_unicom.setSizePolicy(sizePolicy1)
        self.label_unicom.setMinimumSize(QSize(100, 0))

        self.layout_unicom.addWidget(self.label_unicom)

        self.label_unicom_freq = QLabel(self.group_controllers)
        self.label_unicom_freq.setObjectName(u"label_unicom_freq")
        sizePolicy1.setHeightForWidth(self.label_unicom_freq.sizePolicy().hasHeightForWidth())
        self.label_unicom_freq.setSizePolicy(sizePolicy1)
        self.label_unicom_freq.setMinimumSize(QSize(100, 0))

        self.layout_unicom.addWidget(self.label_unicom_freq)

        self.button_unicom_com1 = SelectedButton(self.group_controllers)
        self.button_unicom_com1.setObjectName(u"button_unicom_com1")
        sizePolicy.setHeightForWidth(self.button_unicom_com1.sizePolicy().hasHeightForWidth())
        self.button_unicom_com1.setSizePolicy(sizePolicy)

        self.layout_unicom.addWidget(self.button_unicom_com1)

        self.button_unicom_com2 = SelectedButton(self.group_controllers)
        self.button_unicom_com2.setObjectName(u"button_unicom_com2")
        sizePolicy.setHeightForWidth(self.button_unicom_com2.sizePolicy().hasHeightForWidth())
        self.button_unicom_com2.setSizePolicy(sizePolicy)

        self.layout_unicom.addWidget(self.button_unicom_com2)


        self.verticalLayout_2.addLayout(self.layout_unicom)

        self.layout_emer = QHBoxLayout()
        self.layout_emer.setObjectName(u"layout_emer")
        self.label_emer = QLabel(self.group_controllers)
        self.label_emer.setObjectName(u"label_emer")
        sizePolicy1.setHeightForWidth(self.label_emer.sizePolicy().hasHeightForWidth())
        self.label_emer.setSizePolicy(sizePolicy1)
        self.label_emer.setMinimumSize(QSize(100, 0))

        self.layout_emer.addWidget(self.label_emer)

        self.label_emer_freq = QLabel(self.group_controllers)
        self.label_emer_freq.setObjectName(u"label_emer_freq")
        sizePolicy1.setHeightForWidth(self.label_emer_freq.sizePolicy().hasHeightForWidth())
        self.label_emer_freq.setSizePolicy(sizePolicy1)
        self.label_emer_freq.setMinimumSize(QSize(100, 0))

        self.layout_emer.addWidget(self.label_emer_freq)

        self.button_emer_com1 = SelectedButton(self.group_controllers)
        self.button_emer_com1.setObjectName(u"button_emer_com1")
        sizePolicy.setHeightForWidth(self.button_emer_com1.sizePolicy().hasHeightForWidth())
        self.button_emer_com1.setSizePolicy(sizePolicy)

        self.layout_emer.addWidget(self.button_emer_com1)

        self.button_emer_com2 = SelectedButton(self.group_controllers)
        self.button_emer_com2.setObjectName(u"button_emer_com2")
        sizePolicy.setHeightForWidth(self.button_emer_com2.sizePolicy().hasHeightForWidth())
        self.button_emer_com2.setSizePolicy(sizePolicy)

        self.layout_emer.addWidget(self.button_emer_com2)


        self.verticalLayout_2.addLayout(self.layout_emer)


        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.spacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.spacer_2)


        self.gridLayout_2.addWidget(self.group_controllers, 0, 1, 3, 1)

        self.group_message = QGroupBox(ClientWindow)
        self.group_message.setObjectName(u"group_message")
        self.group_message.setEnabled(False)
        self.group_message.setFont(font)
        self.gridLayout_5 = QGridLayout(self.group_message)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.channel_messages = QTabWidget(self.group_message)
        self.channel_messages.setObjectName(u"channel_messages")
        self.unicom = QWidget()
        self.unicom.setObjectName(u"unicom")
        self.channel_messages.addTab(self.unicom, "")

        self.gridLayout_5.addWidget(self.channel_messages, 0, 0, 1, 1)

        self.layout_send = QHBoxLayout()
        self.layout_send.setObjectName(u"layout_send")
        self.label_unicom_2 = QLabel(self.group_message)
        self.label_unicom_2.setObjectName(u"label_unicom_2")

        self.layout_send.addWidget(self.label_unicom_2)

        self.line_edit_message = QLineEdit(self.group_message)
        self.line_edit_message.setObjectName(u"line_edit_message")

        self.layout_send.addWidget(self.line_edit_message)


        self.gridLayout_5.addLayout(self.layout_send, 1, 0, 1, 1)


        self.gridLayout_2.addWidget(self.group_message, 1, 0, 1, 1)


        self.retranslateUi(ClientWindow)

        self.channel_messages.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ClientWindow)
    # setupUi

    def retranslateUi(self, ClientWindow):
        ClientWindow.setWindowTitle(QCoreApplication.translate("ClientWindow", u"PilotClient", None))
        self.group_com.setTitle(QCoreApplication.translate("ClientWindow", u"\u901a\u8baf\u9762\u677f", None))
        self.button_com2_tx.setText(QCoreApplication.translate("ClientWindow", u"TX", None))
        self.button_com1_rx.setText(QCoreApplication.translate("ClientWindow", u"RX", None))
        self.label_com2_freq.setText(QCoreApplication.translate("ClientWindow", u"---.---", None))
        self.label_com2.setText(QCoreApplication.translate("ClientWindow", u"COM2:", None))
        self.button_com1_tx.setText(QCoreApplication.translate("ClientWindow", u"TX", None))
        self.label_com1.setText(QCoreApplication.translate("ClientWindow", u"COM1:", None))
        self.label_com1_freq.setText(QCoreApplication.translate("ClientWindow", u"---.---", None))
        self.button_com2_rx.setText(QCoreApplication.translate("ClientWindow", u"RX", None))
        self.group_controllers.setTitle(QCoreApplication.translate("ClientWindow", u"\u5728\u7ebf\u7ba1\u5236\u5458", None))
        self.label_unicom.setText(QCoreApplication.translate("ClientWindow", u"UNICOM", None))
        self.label_unicom_freq.setText(QCoreApplication.translate("ClientWindow", u"122.800", None))
        self.button_unicom_com1.setText(QCoreApplication.translate("ClientWindow", u"COM1", None))
        self.button_unicom_com2.setText(QCoreApplication.translate("ClientWindow", u"COM2", None))
        self.label_emer.setText(QCoreApplication.translate("ClientWindow", u"EMER", None))
        self.label_emer_freq.setText(QCoreApplication.translate("ClientWindow", u"121.500", None))
        self.button_emer_com1.setText(QCoreApplication.translate("ClientWindow", u"COM1", None))
        self.button_emer_com2.setText(QCoreApplication.translate("ClientWindow", u"COM2", None))
        self.group_message.setTitle(QCoreApplication.translate("ClientWindow", u"\u6587\u5b57\u6d88\u606f", None))
        self.channel_messages.setTabText(self.channel_messages.indexOf(self.unicom), QCoreApplication.translate("ClientWindow", u"UNICOM", None))
        self.label_unicom_2.setText(QCoreApplication.translate("ClientWindow", u"UNICOM", None))
    # retranslateUi

