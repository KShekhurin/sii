from abc import ABC, abstractmethod
from ast import List
from typing import Optional

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QGroupBox,
    QHBoxLayout, QListView, QListWidget, QListWidgetItem,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QVBoxLayout, QWidget)

from stand.server.gui.console.console_window import Ui_ConsoleWindow, ConsoleWindow
from stand.server.gui.main_presenter import MainPresenter, MainStates
from stand.server.gui.main_view import MainView
from stand.server.server_api import AbstractGame, AbstractGameAgent


class ListItemWithCheckbox(QListWidgetItem):
    def __init__(self, display_text: str, parent=None):
        super(ListItemWithCheckbox, self).__init__()

        self.setText(display_text)
        self.setCheckState(Qt.Unchecked)
        self.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled)


class Ui_MainWindow(MainView):
    def setupUi(self, MainWindow):
        #state
        self.presenter = MainPresenter(self)
        self.active_sessions = []

        #ui
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(568, 606)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setEnabled(True)
        self.groupBox_2.setFlat(True)
        self.horizontalLayout = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.refresh_agents_btn = QPushButton(self.groupBox_2)
        self.refresh_agents_btn.setObjectName(u"refresh_agents_btn")

        self.verticalLayout_2.addWidget(self.refresh_agents_btn)

        self.pushButton_5 = QPushButton(self.groupBox_2)
        self.pushButton_5.setObjectName(u"pushButton_5")

        self.verticalLayout_2.addWidget(self.pushButton_5)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.agents_list_view = QListWidget(self.groupBox_2)
        self.agents_list_view.setObjectName(u"agents_list_view")
        self.agents_list_view.setEnabled(True)
        self.agents_list_view.setAutoFillBackground(False)
        self.agents_list_view.setProperty(u"showDropIndicator", False)
        self.agents_list_view.setAlternatingRowColors(True)
        self.agents_list_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.agents_list_view.setLayoutMode(QListView.LayoutMode.SinglePass)
        self.agents_list_view.setModelColumn(0)
        self.agents_list_view.setUniformItemSizes(False)
        self.agents_list_view.setSelectionRectVisible(True)

        self.horizontalLayout.addWidget(self.agents_list_view)


        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 1)

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setFlat(True)
        self.groupBox.setCheckable(False)
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.refresh_games_btn = QPushButton(self.groupBox)
        self.refresh_games_btn.setObjectName(u"refresh_games_btn")

        self.verticalLayout.addWidget(self.refresh_games_btn)

        self.pushButton_4 = QPushButton(self.groupBox)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.verticalLayout.addWidget(self.pushButton_4)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.games_list_view = QListWidget(self.groupBox)
        ListItemWithCheckbox("test1", self.games_list_view)
        ListItemWithCheckbox("test2", self.games_list_view)
        self.games_list_view.setObjectName(u"games_list_view")
        self.games_list_view.setAlternatingRowColors(True)

        self.horizontalLayout_2.addWidget(self.games_list_view)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.run_cli_btn = QPushButton(self.centralwidget)
        self.run_cli_btn.setObjectName(u"run_cli_btn")
        #self.run_cli_btn.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.run_cli_btn)

        self.run_gui_btn = QPushButton(self.centralwidget)
        self.run_gui_btn.setObjectName(u"run_gui_btn")
        #self.run_gui_btn.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.run_gui_btn)


        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 568, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

        self.games_list_view.itemChanged.connect(self.on_selected_game_item_changed)
        self.agents_list_view.itemChanged.connect(self.on_selected_agent_item_changed)

        self.run_cli_btn.clicked.connect(self.presenter.start_cli_session)

        self.presenter.change_state(MainStates.SELECTING_GAME)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Agents", None))
        self.refresh_agents_btn.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"Select", None))

        __sortingEnabled = self.agents_list_view.isSortingEnabled()
        self.agents_list_view.setSortingEnabled(False)
        self.agents_list_view.setSortingEnabled(__sortingEnabled)

        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Game", None))
        self.refresh_games_btn.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Select", None))

        __sortingEnabled1 = self.games_list_view.isSortingEnabled()
        self.games_list_view.setSortingEnabled(False)
        self.games_list_view.setSortingEnabled(__sortingEnabled1)

        self.run_cli_btn.setText(QCoreApplication.translate("MainWindow", u"Run CLI", None))
        self.run_gui_btn.setText(QCoreApplication.translate("MainWindow", u"Run GUI", None))

    def show_cli_window(self, game: AbstractGame, agents: list[AbstractGameAgent]):
        window = ConsoleWindow(game, agents)
        window.show()

        self.active_sessions.append(window)

    def on_selected_game_item_changed(self, item):
        if item.checkState() == Qt.Checked:
            for row in range(self.agents_list_view.count()):
                citem = self.agents_list_view.item(row)
                if citem != item:
                    citem.setCheckState(Qt.Unchecked)
            self.presenter.on_selected_game_changed(self.games_list_view.row(item))
        else:
            self.presenter.on_game_unselected()

    def on_selected_agent_item_changed(self, item):
        if item.checkState() == Qt.Checked:
            self.presenter.on_agent_added(self.agents_list_view.row(item))
        else:
            self.presenter.on_agent_removed(self.agents_list_view.row(item))

    def get_selected_game_id(self) -> Optional[int]:
        for row in range(self.games_list_view.count()):
            item = self.games_list_view.item(row)

            if item.checkState() == Qt.Checked:
                return row

        return None

    def set_games(self, texts: list[str]):
        self.games_list_view.clear()

        for text in texts:
            item = ListItemWithCheckbox(text, self.games_list_view)
            self.games_list_view.addItem(item)

    def get_selected_agents_ids(self) -> list[int]:
        result = []

        for row in range(self.agents_list_view.count()):
            item = self.agents_list_view.item(row)

            if item.checkState() == Qt.Checked:
                result.append(item.text())

        return result

    def set_agents(self, texts: list[str]):
        self.agents_list_view.clear()

        for text in texts:
            item = ListItemWithCheckbox(text, self.agents_list_view)
            self.agents_list_view.addItem(item)

    def set_agents_box_enabled(self, enabled: bool):
        self.groupBox_2.setEnabled(enabled)

    def set_cli_btn_enabled(self, enabled: bool):
        self.run_cli_btn.setEnabled(enabled)

    def set_gui_btn_enabled(self, enabled: bool):
        self.run_gui_btn.setEnabled(enabled)