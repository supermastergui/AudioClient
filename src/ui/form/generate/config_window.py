# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'config_window.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QWidget)

from src.ui.component.hotkey_button import HotkeyButton
import resource_rc

class Ui_ConfigWindow(object):
    def setupUi(self, ConfigWindow):
        if not ConfigWindow.objectName():
            ConfigWindow.setObjectName(u"ConfigWindow")
        ConfigWindow.resize(451, 374)
        ConfigWindow.setMinimumSize(QSize(451, 162))
        font = QFont()
        font.setFamilies([u"Leelawadee UI"])
        font.setPointSize(10)
        ConfigWindow.setFont(font)
        icon = QIcon()
        icon.addFile(u":/icon/logo", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        ConfigWindow.setWindowIcon(icon)
        self.gridLayout_2 = QGridLayout(ConfigWindow)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.layout_form = QGridLayout()
        self.layout_form.setObjectName(u"layout_form")
        self.layout_form.setContentsMargins(3, 3, 3, 3)
        self.combo_box_audio_output = QComboBox(ConfigWindow)
        self.combo_box_audio_output.setObjectName(u"combo_box_audio_output")

        self.layout_form.addWidget(self.combo_box_audio_output, 9, 1, 1, 2)

        self.label_udp_port = QLabel(ConfigWindow)
        self.label_udp_port.setObjectName(u"label_udp_port")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_udp_port.sizePolicy().hasHeightForWidth())
        self.label_udp_port.setSizePolicy(sizePolicy)
        self.label_udp_port.setMinimumSize(QSize(100, 0))

        self.layout_form.addWidget(self.label_udp_port, 6, 0, 1, 1)

        self.line_edit_server_address = QLineEdit(ConfigWindow)
        self.line_edit_server_address.setObjectName(u"line_edit_server_address")

        self.layout_form.addWidget(self.line_edit_server_address, 4, 1, 1, 2)

        self.combo_box_audio_driver = QComboBox(ConfigWindow)
        self.combo_box_audio_driver.setObjectName(u"combo_box_audio_driver")

        self.layout_form.addWidget(self.combo_box_audio_driver, 7, 1, 1, 2)

        self.line_edit_udp_port = QLineEdit(ConfigWindow)
        self.line_edit_udp_port.setObjectName(u"line_edit_udp_port")

        self.layout_form.addWidget(self.line_edit_udp_port, 6, 1, 1, 2)

        self.line_edit_account = QLineEdit(ConfigWindow)
        self.line_edit_account.setObjectName(u"line_edit_account")

        self.layout_form.addWidget(self.line_edit_account, 2, 1, 1, 2)

        self.label_audio_input = QLabel(ConfigWindow)
        self.label_audio_input.setObjectName(u"label_audio_input")
        sizePolicy.setHeightForWidth(self.label_audio_input.sizePolicy().hasHeightForWidth())
        self.label_audio_input.setSizePolicy(sizePolicy)
        self.label_audio_input.setMinimumSize(QSize(100, 0))

        self.layout_form.addWidget(self.label_audio_input, 8, 0, 1, 1)

        self.combo_box_log_level = QComboBox(ConfigWindow)
        self.combo_box_log_level.addItem("")
        self.combo_box_log_level.addItem("")
        self.combo_box_log_level.addItem("")
        self.combo_box_log_level.addItem("")
        self.combo_box_log_level.addItem("")
        self.combo_box_log_level.addItem("")
        self.combo_box_log_level.addItem("")
        self.combo_box_log_level.setObjectName(u"combo_box_log_level")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.combo_box_log_level.sizePolicy().hasHeightForWidth())
        self.combo_box_log_level.setSizePolicy(sizePolicy1)

        self.layout_form.addWidget(self.combo_box_log_level, 1, 1, 1, 1)

        self.combo_box_audio_input = QComboBox(ConfigWindow)
        self.combo_box_audio_input.setObjectName(u"combo_box_audio_input")

        self.layout_form.addWidget(self.combo_box_audio_input, 8, 1, 1, 2)

        self.line_edit_tcp_port = QLineEdit(ConfigWindow)
        self.line_edit_tcp_port.setObjectName(u"line_edit_tcp_port")

        self.layout_form.addWidget(self.line_edit_tcp_port, 5, 1, 1, 2)

        self.label_log_level = QLabel(ConfigWindow)
        self.label_log_level.setObjectName(u"label_log_level")
        sizePolicy.setHeightForWidth(self.label_log_level.sizePolicy().hasHeightForWidth())
        self.label_log_level.setSizePolicy(sizePolicy)
        self.label_log_level.setMinimumSize(QSize(100, 0))

        self.layout_form.addWidget(self.label_log_level, 1, 0, 1, 1)

        self.label_password = QLabel(ConfigWindow)
        self.label_password.setObjectName(u"label_password")
        sizePolicy.setHeightForWidth(self.label_password.sizePolicy().hasHeightForWidth())
        self.label_password.setSizePolicy(sizePolicy)
        self.label_password.setMinimumSize(QSize(100, 0))

        self.layout_form.addWidget(self.label_password, 3, 0, 1, 1)

        self.label_audio_output = QLabel(ConfigWindow)
        self.label_audio_output.setObjectName(u"label_audio_output")
        sizePolicy.setHeightForWidth(self.label_audio_output.sizePolicy().hasHeightForWidth())
        self.label_audio_output.setSizePolicy(sizePolicy)
        self.label_audio_output.setMinimumSize(QSize(100, 0))

        self.layout_form.addWidget(self.label_audio_output, 9, 0, 1, 1)

        self.button_ptt = HotkeyButton(ConfigWindow)
        self.button_ptt.setObjectName(u"button_ptt")
        self.button_ptt.setMinimumSize(QSize(0, 23))

        self.layout_form.addWidget(self.button_ptt, 10, 1, 1, 2)

        self.line_edit_password = QLineEdit(ConfigWindow)
        self.line_edit_password.setObjectName(u"line_edit_password")
        self.line_edit_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.layout_form.addWidget(self.line_edit_password, 3, 1, 1, 2)

        self.label_config_version_2 = QLabel(ConfigWindow)
        self.label_config_version_2.setObjectName(u"label_config_version_2")
        self.label_config_version_2.setMinimumSize(QSize(0, 23))

        self.layout_form.addWidget(self.label_config_version_2, 0, 1, 1, 1)

        self.check_box_remember_me = QCheckBox(ConfigWindow)
        self.check_box_remember_me.setObjectName(u"check_box_remember_me")

        self.layout_form.addWidget(self.check_box_remember_me, 0, 2, 1, 1)

        self.label_account = QLabel(ConfigWindow)
        self.label_account.setObjectName(u"label_account")
        sizePolicy.setHeightForWidth(self.label_account.sizePolicy().hasHeightForWidth())
        self.label_account.setSizePolicy(sizePolicy)
        self.label_account.setMinimumSize(QSize(100, 0))

        self.layout_form.addWidget(self.label_account, 2, 0, 1, 1)

        self.label_tcp_port = QLabel(ConfigWindow)
        self.label_tcp_port.setObjectName(u"label_tcp_port")
        sizePolicy.setHeightForWidth(self.label_tcp_port.sizePolicy().hasHeightForWidth())
        self.label_tcp_port.setSizePolicy(sizePolicy)
        self.label_tcp_port.setMinimumSize(QSize(100, 0))

        self.layout_form.addWidget(self.label_tcp_port, 5, 0, 1, 1)

        self.label_server_address = QLabel(ConfigWindow)
        self.label_server_address.setObjectName(u"label_server_address")
        sizePolicy.setHeightForWidth(self.label_server_address.sizePolicy().hasHeightForWidth())
        self.label_server_address.setSizePolicy(sizePolicy)
        self.label_server_address.setMinimumSize(QSize(100, 0))

        self.layout_form.addWidget(self.label_server_address, 4, 0, 1, 1)

        self.label_ptt = QLabel(ConfigWindow)
        self.label_ptt.setObjectName(u"label_ptt")
        sizePolicy.setHeightForWidth(self.label_ptt.sizePolicy().hasHeightForWidth())
        self.label_ptt.setSizePolicy(sizePolicy)
        self.label_ptt.setMinimumSize(QSize(100, 0))

        self.layout_form.addWidget(self.label_ptt, 10, 0, 1, 1)

        self.label_audio_driver = QLabel(ConfigWindow)
        self.label_audio_driver.setObjectName(u"label_audio_driver")
        sizePolicy.setHeightForWidth(self.label_audio_driver.sizePolicy().hasHeightForWidth())
        self.label_audio_driver.setSizePolicy(sizePolicy)
        self.label_audio_driver.setMinimumSize(QSize(100, 0))

        self.layout_form.addWidget(self.label_audio_driver, 7, 0, 1, 1)

        self.label_config_version = QLabel(ConfigWindow)
        self.label_config_version.setObjectName(u"label_config_version")
        sizePolicy.setHeightForWidth(self.label_config_version.sizePolicy().hasHeightForWidth())
        self.label_config_version.setSizePolicy(sizePolicy)
        self.label_config_version.setMinimumSize(QSize(100, 0))

        self.layout_form.addWidget(self.label_config_version, 0, 0, 1, 1)


        self.gridLayout_2.addLayout(self.layout_form, 6, 0, 1, 3)

        self.layout_buttons = QHBoxLayout()
        self.layout_buttons.setObjectName(u"layout_buttons")
        self.button_ok = QPushButton(ConfigWindow)
        self.button_ok.setObjectName(u"button_ok")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.button_ok.sizePolicy().hasHeightForWidth())
        self.button_ok.setSizePolicy(sizePolicy2)

        self.layout_buttons.addWidget(self.button_ok)

        self.button_apply = QPushButton(ConfigWindow)
        self.button_apply.setObjectName(u"button_apply")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.button_apply.sizePolicy().hasHeightForWidth())
        self.button_apply.setSizePolicy(sizePolicy3)

        self.layout_buttons.addWidget(self.button_apply)

        self.button_cancel = QPushButton(ConfigWindow)
        self.button_cancel.setObjectName(u"button_cancel")
        sizePolicy2.setHeightForWidth(self.button_cancel.sizePolicy().hasHeightForWidth())
        self.button_cancel.setSizePolicy(sizePolicy2)

        self.layout_buttons.addWidget(self.button_cancel)


        self.gridLayout_2.addLayout(self.layout_buttons, 7, 1, 1, 2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 7, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 8, 0, 1, 3)


        self.retranslateUi(ConfigWindow)

        QMetaObject.connectSlotsByName(ConfigWindow)
    # setupUi

    def retranslateUi(self, ConfigWindow):
        ConfigWindow.setWindowTitle(QCoreApplication.translate("ConfigWindow", u"\u9996\u9009\u9879", None))
        self.label_udp_port.setText(QCoreApplication.translate("ConfigWindow", u"UDP\u7aef\u53e3", None))
        self.label_audio_input.setText(QCoreApplication.translate("ConfigWindow", u"\u97f3\u9891\u8f93\u5165", None))
        self.combo_box_log_level.setItemText(0, QCoreApplication.translate("ConfigWindow", u"TRACE", None))
        self.combo_box_log_level.setItemText(1, QCoreApplication.translate("ConfigWindow", u"DEBUG", None))
        self.combo_box_log_level.setItemText(2, QCoreApplication.translate("ConfigWindow", u"INFO", None))
        self.combo_box_log_level.setItemText(3, QCoreApplication.translate("ConfigWindow", u"SUCCESS", None))
        self.combo_box_log_level.setItemText(4, QCoreApplication.translate("ConfigWindow", u"WARNING", None))
        self.combo_box_log_level.setItemText(5, QCoreApplication.translate("ConfigWindow", u"ERROR", None))
        self.combo_box_log_level.setItemText(6, QCoreApplication.translate("ConfigWindow", u"CRITICAL", None))

        self.label_log_level.setText(QCoreApplication.translate("ConfigWindow", u"\u65e5\u5fd7\u7b49\u7ea7", None))
        self.label_password.setText(QCoreApplication.translate("ConfigWindow", u"\u5bc6\u7801", None))
        self.label_audio_output.setText(QCoreApplication.translate("ConfigWindow", u"\u97f3\u9891\u8f93\u51fa", None))
        self.button_ptt.setText("")
        self.label_config_version_2.setText(QCoreApplication.translate("ConfigWindow", u"1.0.0", None))
        self.check_box_remember_me.setText(QCoreApplication.translate("ConfigWindow", u"\u8bb0\u4f4f\u6211", None))
        self.label_account.setText(QCoreApplication.translate("ConfigWindow", u"\u8d26\u53f7", None))
        self.label_tcp_port.setText(QCoreApplication.translate("ConfigWindow", u"TCP\u7aef\u53e3", None))
        self.label_server_address.setText(QCoreApplication.translate("ConfigWindow", u"\u670d\u52a1\u5668\u5730\u5740", None))
        self.label_ptt.setText(QCoreApplication.translate("ConfigWindow", u"PTT\u6309\u952e", None))
        self.label_audio_driver.setText(QCoreApplication.translate("ConfigWindow", u"\u97f3\u9891\u9a71\u52a8", None))
        self.label_config_version.setText(QCoreApplication.translate("ConfigWindow", u"\u914d\u7f6e\u6587\u4ef6\u7248\u672c", None))
        self.button_ok.setText(QCoreApplication.translate("ConfigWindow", u"\u4fdd\u5b58", None))
        self.button_apply.setText(QCoreApplication.translate("ConfigWindow", u"\u5e94\u7528", None))
        self.button_cancel.setText(QCoreApplication.translate("ConfigWindow", u"\u53d6\u6d88", None))
    # retranslateUi

