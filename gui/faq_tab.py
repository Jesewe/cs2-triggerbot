from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

def init_faq_tab(main_window):
    """
    Sets up the FAQs tab with common questions and answers.
    """
    faq_tab = QWidget()
    layout = QVBoxLayout()
    faqs_content = """
    <h3 style="color:#D5006D;">Frequently Asked Questions</h3>
    <p><b>Q: What is a <span style="color:#BB86FC;">TriggerBot</span>?</b></p>
    <p>A: A <span style="color:#BB86FC;">TriggerBot</span> is a tool that automatically shoots when your crosshair is over an enemy.</p>
    <p><b>Q: Is this tool safe to use?</b></p>
    <p>A: This tool is for educational purposes only. Use it at your own risk.</p>
    <p><b>Q: How do I start the <span style="color:#BB86FC;">TriggerBot</span>?</b></p>
    <p>A: Go to the 'Home' tab and click 'Start Bot' after ensuring the game is running.</p>
    <p><b>Q: How can I update the <span style="color:#BB86FC;">offsets</span>?</b></p>
    <p>A: Offsets are fetched automatically from the server. Check the 'Home' tab for the last update timestamp.</p>
    <p><b>Q: Can I customize the bot's behavior?</b></p>
    <p>A: Yes, use the 'General Settings' tab to adjust key configurations, delays, and teammate attack settings.</p>
    <p><b>Q: Does the TriggerBot work on <span style="color:#BB86FC;">FACEIT</span>?</b></p>
    <p>A: No, using the TriggerBot on FACEIT is against their terms of service and can result in a ban.</p>
    <p><b>Q: I found a bug, where can I report it?</b></p>
    <p>A: Report bugs by opening an issue on our <a style="color: #BB86FC;" href="https://github.com/Jesewe/cs2-triggerbot/issues">GitHub Issues page</a>.</p>
    <p><b>Q: How can I contribute to the project?</b></p>
    <p>A: Open a pull request on our <a style="color: #BB86FC;" href="https://github.com/Jesewe/cs2-triggerbot/pulls">GitHub Pull Requests page</a>.</p>
    <p><b>Q: Where can I join the community?</b></p>
    <p>A: Join our <a style="color: #BB86FC;" href="https://t.me/cs2_jesewe">Telegram Channel</a> for updates and support.</p>
    """
    faqs_widget = QTextEdit()
    faqs_widget.setHtml(faqs_content)
    faqs_widget.setReadOnly(True)
    layout.addWidget(faqs_widget)
    faq_tab.setLayout(layout)
    main_window.tabs.addTab(faq_tab, "FAQs")