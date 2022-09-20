from UIControls.FrameController import *

def main():
    app = QApplication(sys.argv)
    controller = FrameController()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()