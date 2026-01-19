# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login_window.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QLabel,
    QLayout, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)
import resource_rc
import resource_rc

class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        if not LoginWindow.objectName():
            LoginWindow.setObjectName(u"LoginWindow")
        LoginWindow.resize(366, 336)
        self.gridLayout = QGridLayout(LoginWindow)
        self.gridLayout.setObjectName(u"gridLayout")
        self.layout_title = QGridLayout()
        self.layout_title.setObjectName(u"layout_title")
        self.layout_title.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.spacer_r = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_title.addItem(self.spacer_r, 1, 3, 1, 1)

        self.label_title = QLabel(LoginWindow)
        self.label_title.setObjectName(u"label_title")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_title.sizePolicy().hasHeightForWidth())
        self.label_title.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies([u"Leelawadee UI"])
        font.setPointSize(24)
        font.setWeight(QFont.ExtraBold)
        self.label_title.setFont(font)
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout_title.addWidget(self.label_title, 1, 2, 1, 1)

        self.label_icon = QLabel(LoginWindow)
        self.label_icon.setObjectName(u"label_icon")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_icon.sizePolicy().hasHeightForWidth())
        self.label_icon.setSizePolicy(sizePolicy1)
        self.label_icon.setMaximumSize(QSize(43, 43))
        self.label_icon.setPixmap(QPixmap(u":/icon/logo"))
        self.label_icon.setScaledContents(True)
        self.label_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout_title.addWidget(self.label_icon, 1, 1, 1, 1)

        self.spacer_l = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_title.addItem(self.spacer_l, 1, 0, 1, 1)


        self.gridLayout.addLayout(self.layout_title, 1, 0, 1, 3)

        self.spacer_t = QSpacerItem(208, 35, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.spacer_t, 0, 1, 1, 1)

        self.layout_form = QVBoxLayout()
        self.layout_form.setObjectName(u"layout_form")
        self.label_account = QLabel(LoginWindow)
        self.label_account.setObjectName(u"label_account")

        self.layout_form.addWidget(self.label_account)

        self.line_edit_account = QLineEdit(LoginWindow)
        self.line_edit_account.setObjectName(u"line_edit_account")
        self.line_edit_account.setMinimumSize(QSize(200, 0))

        self.layout_form.addWidget(self.line_edit_account)

        self.label_password = QLabel(LoginWindow)
        self.label_password.setObjectName(u"label_password")

        self.layout_form.addWidget(self.label_password)

        self.line_edit_password = QLineEdit(LoginWindow)
        self.line_edit_password.setObjectName(u"line_edit_password")
        self.line_edit_password.setMinimumSize(QSize(200, 0))
        self.line_edit_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.layout_form.addWidget(self.line_edit_password)

        self.check_box_remember_me = QCheckBox(LoginWindow)
        self.check_box_remember_me.setObjectName(u"check_box_remember_me")

        self.layout_form.addWidget(self.check_box_remember_me)


        self.gridLayout.addLayout(self.layout_form, 2, 1, 2, 1)

        self.layout_buttons = QGridLayout()
        self.layout_buttons.setObjectName(u"layout_buttons")
        self.button_login = QPushButton(LoginWindow)
        self.button_login.setObjectName(u"button_login")

        self.layout_buttons.addWidget(self.button_login, 0, 0, 1, 1)

        self.button_settings = QPushButton(LoginWindow)
        self.button_settings.setObjectName(u"button_settings")
        sizePolicy1.setHeightForWidth(self.button_settings.sizePolicy().hasHeightForWidth())
        self.button_settings.setSizePolicy(sizePolicy1)
        self.button_settings.setMinimumSize(QSize(29, 29))
        icon = QIcon()
        icon.addFile(u":/icon/setting", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_settings.setIcon(icon)

        self.layout_buttons.addWidget(self.button_settings, 0, 1, 1, 1)


        self.gridLayout.addLayout(self.layout_buttons, 4, 1, 1, 1)

        self.spacer_r_2 = QSpacerItem(212, 114, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.spacer_r_2, 3, 2, 1, 1)

        self.spacer_l_2 = QSpacerItem(212, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.spacer_l_2, 3, 0, 1, 1)

        self.spacer_b = QSpacerItem(208, 57, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.spacer_b, 6, 1, 1, 1)


        self.retranslateUi(LoginWindow)

        QMetaObject.connectSlotsByName(LoginWindow)
    # setupUi

    def retranslateUi(self, LoginWindow):
        LoginWindow.setWindowTitle(QCoreApplication.translate("LoginWindow", u"AudioClient", None))
        self.label_title.setText(QCoreApplication.translate("LoginWindow", u"AudioClient", None))
        self.label_icon.setText("")
        self.label_account.setText(QCoreApplication.translate("LoginWindow", u"\u8d26\u53f7\uff1a", None))
        self.label_password.setText(QCoreApplication.translate("LoginWindow", u"\u5bc6\u7801\uff1a", None))
        self.check_box_remember_me.setText(QCoreApplication.translate("LoginWindow", u"\u8bb0\u4f4f\u6211", None))
        self.button_login.setText(QCoreApplication.translate("LoginWindow", u"\u767b\u5f55", None))
        self.button_settings.setText("")
    # retranslateUi

