from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QLabel
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys

class VoiceListenerThread(QThread):
    text_received = pyqtSignal(str)
    
    def __init__(self, voice_recognizer):
        super().__init__()
        self.voice_recognizer = voice_recognizer
        self.running = True
        
    def run(self):
        while self.running:
            text = self.voice_recognizer.listen()
            if text:
                self.text_received.emit(text)
    
    def stop(self):
        self.running = False

class AgentGUI(QMainWindow):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("AI Agent for Windows")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        main_layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        self.text_input = QTextEdit()
        self.text_input.setMaximumHeight(70)
        self.text_input.setPlaceholderText("Type your command here...")
        input_layout.addWidget(self.text_input)
        
        # Buttons
        button_layout = QVBoxLayout()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.on_send_clicked)
        self.voice_button = QPushButton("Voice")
        self.voice_button.clicked.connect(self.on_voice_clicked)
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.voice_button)
        input_layout.addLayout(button_layout)
        
        main_layout.addLayout(input_layout)
        
        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Add initial message
        self.add_message("AI Agent", "Hello! I'm your AI assistant. How can I help you today?")
        
        # Voice listener thread
        self.voice_thread = VoiceListenerThread(self.agent.voice_recognizer)
        self.voice_thread.text_received.connect(self.on_voice_text_received)
        
        # Set up keyboard shortcuts
        self.text_input.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        if obj is self.text_input and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.NoModifier:
                self.on_send_clicked()
                return True
        return super().eventFilter(obj, event)
    
    def add_message(self, sender, message):
        self.chat_display.append(f"<b>{sender}:</b> {message}")
        self.chat_display.append("")  # Add empty line for spacing
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def on_send_clicked(self):
        text = self.text_input.toPlainText().strip()
        if text:
            self.add_message("You", text)
            self.text_input.clear()
            self.process_input(text)
    
    def on_voice_clicked(self):
        if not self.voice_thread.isRunning():
            self.status_label.setText("Listening...")
            self.voice_button.setText("Stop")
            self.voice_thread.start()
        else:
            self.voice_thread.stop()
            self.voice_thread.wait()
            self.voice_button.setText("Voice")
            self.status_label.setText("Ready")
    
    def on_voice_text_received(self, text):
        self.add_message("You (voice)", text)
        self.process_input(text)
        self.voice_thread.stop()
        self.voice_thread.wait()
        self.voice_button.setText("Voice")
        self.status_label.setText("Ready")
        self.voice_thread = VoiceListenerThread(self.agent.voice_recognizer)
        self.voice_thread.text_received.connect(self.on_voice_text_received)
    
    def process_input(self, text):
        self.status_label.setText("Processing...")
        QApplication.processEvents()
        
        response = self.agent.process_query(text)
        self.add_message("AI Agent", response)
        self.status_label.setText("Ready")