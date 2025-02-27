from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

def init_logs_tab(main_window):
    """
    Sets up the Logs tab to display application logs.
    Attaches a read-only text area to the main window.
    """
    logs_tab = QWidget()
    layout = QVBoxLayout()
    main_window.log_output = QTextEdit()
    main_window.log_output.setReadOnly(True)
    layout.addWidget(main_window.log_output)
    logs_tab.setLayout(layout)
    main_window.tabs.addTab(logs_tab, "Logs")