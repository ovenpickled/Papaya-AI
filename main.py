import sys
from PyQt5.QtWidgets import QApplication
from agent import Agent
from gui import AgentGUI

def main():
    app = QApplication(sys.argv)
    agent = Agent()
    gui = AgentGUI(agent)
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()