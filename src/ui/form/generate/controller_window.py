# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'controller_window.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QWidget)

from src.ui.component.selected_button import SelectedButton

class Ui_ControllerWindow(object):
    def setupUi(self, ControllerWindow):
        if not ControllerWindow.objectName():
            ControllerWindow.setObjectName(u"ControllerWindow")
        ControllerWindow.resize(306, 175)
        font = QFont()
        font.setFamilies([u"Leelawadee UI"])
        font.setPointSize(10)
        ControllerWindow.setFont(font)
        self.gridLayout_3 = QGridLayout(ControllerWindow)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.layout_info = QGridLayout()
        self.layout_info.setObjectName(u"layout_info")
        self.label_emer_freq = QLabel(ControllerWindow)
        self.label_emer_freq.setObjectName(u"label_emer_freq")
        self.label_emer_freq.setMinimumSize(QSize(60, 0))

        self.layout_info.addWidget(self.label_emer_freq, 3, 0, 1, 1)

        self.label_main_freq = QLabel(ControllerWindow)
        self.label_main_freq.setObjectName(u"label_main_freq")
        self.label_main_freq.setMinimumSize(QSize(60, 0))

        self.layout_info.addWidget(self.label_main_freq, 1, 0, 1, 1)

        self.label_current_freq = QLabel(ControllerWindow)
        self.label_current_freq.setObjectName(u"label_current_freq")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_current_freq.sizePolicy().hasHeightForWidth())
        self.label_current_freq.setSizePolicy(sizePolicy)
        self.label_current_freq.setMinimumSize(QSize(60, 25))

        self.layout_info.addWidget(self.label_current_freq, 0, 0, 1, 1)

        self.label_unicom = QLabel(ControllerWindow)
        self.label_unicom.setObjectName(u"label_unicom")
        self.label_unicom.setMinimumSize(QSize(60, 0))

        self.layout_info.addWidget(self.label_unicom, 2, 0, 1, 1)

        self.label_unicom_v = QLabel(ControllerWindow)
        self.label_unicom_v.setObjectName(u"label_unicom_v")

        self.layout_info.addWidget(self.label_unicom_v, 2, 1, 1, 1)

        self.label_current_freq_v = QLabel(ControllerWindow)
        self.label_current_freq_v.setObjectName(u"label_current_freq_v")

        self.layout_info.addWidget(self.label_current_freq_v, 0, 1, 1, 1)

        self.label_emer_freq_v = QLabel(ControllerWindow)
        self.label_emer_freq_v.setObjectName(u"label_emer_freq_v")

        self.layout_info.addWidget(self.label_emer_freq_v, 3, 1, 1, 1)

        self.line_edit_freq = QLineEdit(ControllerWindow)
        self.line_edit_freq.setObjectName(u"line_edit_freq")
        self.line_edit_freq.setMaximumSize(QSize(120, 16777215))

        self.layout_info.addWidget(self.line_edit_freq, 4, 1, 1, 1)

        self.label_freq = QLabel(ControllerWindow)
        self.label_freq.setObjectName(u"label_freq")

        self.layout_info.addWidget(self.label_freq, 4, 0, 1, 1)

        self.label_main_freq_v = QLabel(ControllerWindow)
        self.label_main_freq_v.setObjectName(u"label_main_freq_v")

        self.layout_info.addWidget(self.label_main_freq_v, 1, 1, 1, 1)

        self.button_main_freq_tx = SelectedButton(ControllerWindow)
        self.button_main_freq_tx.setObjectName(u"button_main_freq_tx")
        self.button_main_freq_tx.setMaximumSize(QSize(80, 16777215))

        self.layout_info.addWidget(self.button_main_freq_tx, 1, 2, 1, 1)

        self.button_main_freq_rx = SelectedButton(ControllerWindow)
        self.button_main_freq_rx.setObjectName(u"button_main_freq_rx")
        self.button_main_freq_rx.setMaximumSize(QSize(80, 16777215))

        self.layout_info.addWidget(self.button_main_freq_rx, 1, 3, 1, 1)

        self.button_unicom_freq_tx = SelectedButton(ControllerWindow)
        self.button_unicom_freq_tx.setObjectName(u"button_unicom_freq_tx")
        self.button_unicom_freq_tx.setMaximumSize(QSize(80, 16777215))

        self.layout_info.addWidget(self.button_unicom_freq_tx, 2, 2, 1, 1)

        self.button_emer_freq_tx = SelectedButton(ControllerWindow)
        self.button_emer_freq_tx.setObjectName(u"button_emer_freq_tx")
        self.button_emer_freq_tx.setMaximumSize(QSize(80, 16777215))

        self.layout_info.addWidget(self.button_emer_freq_tx, 3, 2, 1, 1)

        self.button_freq_tx = SelectedButton(ControllerWindow)
        self.button_freq_tx.setObjectName(u"button_freq_tx")

        self.layout_info.addWidget(self.button_freq_tx, 4, 2, 1, 1)

        self.button_freq_rx = SelectedButton(ControllerWindow)
        self.button_freq_rx.setObjectName(u"button_freq_rx")

        self.layout_info.addWidget(self.button_freq_rx, 4, 3, 1, 1)

        self.button_emer_freq_rx = SelectedButton(ControllerWindow)
        self.button_emer_freq_rx.setObjectName(u"button_emer_freq_rx")
        self.button_emer_freq_rx.setMaximumSize(QSize(80, 16777215))

        self.layout_info.addWidget(self.button_emer_freq_rx, 3, 3, 1, 1)

        self.button_unicom_freq_rx = SelectedButton(ControllerWindow)
        self.button_unicom_freq_rx.setObjectName(u"button_unicom_freq_rx")
        self.button_unicom_freq_rx.setMaximumSize(QSize(80, 16777215))

        self.layout_info.addWidget(self.button_unicom_freq_rx, 2, 3, 1, 1)


        self.gridLayout_3.addLayout(self.layout_info, 1, 0, 1, 1)

        self.spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.spacer, 2, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 1, 1, 1, 1)


        self.retranslateUi(ControllerWindow)

        QMetaObject.connectSlotsByName(ControllerWindow)
    # setupUi

    def retranslateUi(self, ControllerWindow):
        ControllerWindow.setWindowTitle(QCoreApplication.translate("ControllerWindow", u"ControllerClient", None))
        self.label_emer_freq.setText(QCoreApplication.translate("ControllerWindow", u"EMER", None))
        self.label_main_freq.setText(QCoreApplication.translate("ControllerWindow", u"\u4e3b\u9891\u7387", None))
        self.label_current_freq.setText(QCoreApplication.translate("ControllerWindow", u"\u5f53\u524d\u9891\u7387", None))
        self.label_unicom.setText(QCoreApplication.translate("ControllerWindow", u"UNICOM", None))
        self.label_unicom_v.setText(QCoreApplication.translate("ControllerWindow", u"122.800", None))
        self.label_current_freq_v.setText(QCoreApplication.translate("ControllerWindow", u"---.---", None))
        self.label_emer_freq_v.setText(QCoreApplication.translate("ControllerWindow", u"121.500", None))
        self.label_freq.setText(QCoreApplication.translate("ControllerWindow", u"\u9891\u7387", None))
        self.label_main_freq_v.setText(QCoreApplication.translate("ControllerWindow", u"---.---", None))
        self.button_main_freq_tx.setText(QCoreApplication.translate("ControllerWindow", u"TX", None))
        self.button_main_freq_rx.setText(QCoreApplication.translate("ControllerWindow", u"RX", None))
        self.button_unicom_freq_tx.setText(QCoreApplication.translate("ControllerWindow", u"TX", None))
        self.button_emer_freq_tx.setText(QCoreApplication.translate("ControllerWindow", u"TX", None))
        self.button_freq_tx.setText(QCoreApplication.translate("ControllerWindow", u"TX", None))
        self.button_freq_rx.setText(QCoreApplication.translate("ControllerWindow", u"RX", None))
        self.button_emer_freq_rx.setText(QCoreApplication.translate("ControllerWindow", u"RX", None))
        self.button_unicom_freq_rx.setText(QCoreApplication.translate("ControllerWindow", u"RX", None))
    # retranslateUi

