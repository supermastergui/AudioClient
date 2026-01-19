# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'loading_window.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QSizePolicy,
    QSpacerItem, QWidget)

from src.ui.component.loading_spinner import LoadingSpinner

class Ui_LoadingWindow(object):
    def setupUi(self, LoadingWindow):
        if not LoadingWindow.objectName():
            LoadingWindow.setObjectName(u"LoadingWindow")
        LoadingWindow.resize(372, 300)
        self.gridLayout_2 = QGridLayout(LoadingWindow)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.loading_label = QLabel(LoadingWindow)
        self.loading_label.setObjectName(u"loading_label")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.loading_label, 5, 0, 1, 2)

        self.title_label = QLabel(LoadingWindow)
        self.title_label.setObjectName(u"title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.title_label, 1, 0, 1, 2)

        self.status_label = QLabel(LoadingWindow)
        self.status_label.setObjectName(u"status_label")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.status_label, 6, 0, 1, 2)

        self.spacer_d = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.spacer_d, 0, 0, 1, 2)

        self.spacer_t = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.spacer_t, 7, 0, 1, 2)

        self.layout_loading = QGridLayout()
        self.layout_loading.setObjectName(u"layout_loading")
        self.loading_spinner = LoadingSpinner(LoadingWindow)
        self.loading_spinner.setObjectName(u"loading_spinner")
        self.loading_spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout_loading.addWidget(self.loading_spinner, 0, 1, 1, 1)

        self.spacer_l = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_loading.addItem(self.spacer_l, 0, 0, 1, 1)

        self.spacer_r = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_loading.addItem(self.spacer_r, 0, 2, 1, 1)


        self.gridLayout_2.addLayout(self.layout_loading, 3, 0, 1, 2)


        self.retranslateUi(LoadingWindow)

        QMetaObject.connectSlotsByName(LoadingWindow)
    # setupUi

    def retranslateUi(self, LoadingWindow):
        LoadingWindow.setWindowTitle(QCoreApplication.translate("LoadingWindow", u"Form", None))
        self.loading_label.setText(QCoreApplication.translate("LoadingWindow", u"\u5e94\u7528\u521d\u59cb\u5316\u4e2d...", None))
        self.title_label.setText(QCoreApplication.translate("LoadingWindow", u"AudioClient", None))
        self.status_label.setText(QCoreApplication.translate("LoadingWindow", u"\u52a0\u8f7d\u53ef\u80fd\u9700\u8981\u4e00\u70b9\u65f6\u95f4, \u8bf7\u8010\u5fc3\u7b49\u5f85", None))
        self.loading_spinner.setText(QCoreApplication.translate("LoadingWindow", u"loading", None))
    # retranslateUi

