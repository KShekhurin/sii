from __future__ import annotations
from enum import Enum
from queue import Queue

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt, Signal, Slot, QThread, QObject)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QMenuBar,
                               QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
                               QTextBrowser, QVBoxLayout, QWidget, QInputDialog)

from stand.games.bid_game.WCLIRenderer import BidWCLIRenderer
from stand.server.server_api import AbstractCLIDisplay, AbstractGame, AbstractGameAgent, AbstractRenderer, game, \
    AbstractInput
from stand.server.utils import run

class ExecCodes(Enum):
    EXIT = 1
    NEXT_STEP = 2

class InputDialogue(AbstractInput):
    def __init__(self, worker: TerminalWorker, input_queue: Queue):
        self.input_queue = input_queue
        self.worker = worker

    def read_line(self, prefix: str) -> str:
        self.worker.need_input.emit(prefix)
        result = self.input_queue.get()
        return result

class TerminalDisplay(AbstractCLIDisplay):
    def __init__(self, terminal_worker: TerminalWorker):
        super().__init__()
        self.worker = terminal_worker

    def print_line(self, text) -> None:
        self.worker.append_text.emit(text)

    def read_line(self, prefix) -> str:
        return ""

class TerminalWorker(QObject):
    append_text = Signal(str)
    need_input = Signal(str)

    def __init__(self, queue: Queue):
        super().__init__()
        self.game = None
        self.renderer = None
        self.queue = queue
        self.input_dialogue = None

    def set_game(self, game: AbstractGame):
        self.game = game

    def set_renderer(self, renderer: AbstractRenderer):
        self.renderer = renderer

    def set_input(self, input_dialogue: InputDialogue):
        self.input_dialogue = input_dialogue

    @Slot()
    def run(self):
        while True:
            code = self.queue.get()
            if code == ExecCodes.EXIT:
                return 0

            if not self.game.is_finished():
                self.game.make_step()
                self.renderer.display()

class Ui_ConsoleWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.console_textbrws = QTextBrowser(self.centralwidget)
        self.console_textbrws.setObjectName(u"console_textbrws")

        self.verticalLayout.addWidget(self.console_textbrws)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.next_step_btn = QPushButton(self.centralwidget)
        self.next_step_btn.setObjectName(u"next_step_btn")

        self.horizontalLayout.addWidget(self.next_step_btn)

        self.view_state_btn = QPushButton(self.centralwidget)
        self.view_state_btn.setObjectName(u"view_state_btn")

        self.horizontalLayout.addWidget(self.view_state_btn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.console_textbrws.setStyleSheet("font-size: 20px;")

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.next_step_btn.setText(QCoreApplication.translate("MainWindow", u"Next step", None))
        self.view_state_btn.setText(QCoreApplication.translate("MainWindow", u"View state", None))
    # retranslateUi


class ConsoleWindow(QMainWindow):
    def __init__(self, game: AbstractGame, agents: list[type]):
        super().__init__()
        self.ui = Ui_ConsoleWindow()
        self.ui.setupUi(self)

        self.ui.next_step_btn.clicked.connect(self.on_next_step_btn_click)

        self.msg_queue = Queue()
        self.input_queue = Queue()
        self.on_next_step_btn_click()

        self.display_thread_worker = TerminalWorker(self.msg_queue)
        self.display_thread = QThread()
        self.display = TerminalDisplay(self.display_thread_worker)
        self.input = InputDialogue(self.display_thread_worker, self.input_queue)

        game.add_agents(map(lambda a: a(self.input), agents))
        game.setup()

        renderer = game.build_cli_requirements(self.display)

        self.display_thread_worker.set_game(game)
        self.display_thread_worker.set_renderer(renderer)
        self.display_thread_worker.set_input(self.input)

        self.display_thread_worker.append_text.connect(self.on_text_print_msg)
        self.display_thread_worker.need_input.connect(self.on_request_show_dialogue)
        self.display_thread_worker.moveToThread(self.display_thread)
        self.display_thread.started.connect(self.display_thread_worker.run)
        self.display_thread.start()

    def close_event(self, event):
        self.msg_queue.put(ExecCodes.EXIT)

        self.display_thread.quit()
        self.display_thread.wait()

        event.accept()

    def on_text_print_msg(self, text: str):
        self.ui.console_textbrws.append(text)

    def on_request_show_dialogue(self, prefix: str):
        text, ok = QInputDialog.getText(
            self,
            "User input",  # window title
            prefix  # label text
        )

        self.input_queue.put(text)

    def on_next_step_btn_click(self):
        self.msg_queue.put(ExecCodes.NEXT_STEP)

    def closeEvent(self, event):
        # Access the queue and thread from the UI object
        self.msg_queue.put(ExecCodes.EXIT)
        self.display_thread.quit()
        self.display_thread.wait()
        event.accept()