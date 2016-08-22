
import cv2
from PyQt4 import QtGui, QtCore
import numpy as np
import math, colorsys

key_list=[]
H=70 #green
S=60 #moderated saturation
V=0  #any color intensity
sensitivity = 20
#crosshair (aim) functions
crosshair_x = 640/2
crosshair_y = 480/2

def average(hsv):
    global H, sensitivity
    count = 0
    totalh = 0
    totals = 0
    totalv = 0
    for i in hsv:
        for j in i:
            totalh = totalh + j[0]
            totals = totals + j[1]
            totalv = totalv + j[2]
            count+=1
    return totalh/count,totals/count,totalv/count

def move_crosshair_by_keypress():
    global key_list, crosshair_x, crosshair_y
    for l in key_list:
                if l == 'w':
                    crosshair_y-=5
                elif l == 's':
                    crosshair_y+=5
                elif l == 'a':
                    crosshair_x-=5
                elif l == 'd':
                    crosshair_x+=5


#"motor" aim functions
def motor_horizontal(n):
    global crosshair_x
    crosshair_x+=int(math.ceil(n/10))
    if crosshair_x<0:
        crosshair_x=0
    if crosshair_x>640:
        crosshair_x=640

def motor_vertical(n):
    global crosshair_y
    crosshair_y+=int(math.ceil(n/10))
    if crosshair_y<0:
        crosshair_y=0
    if crosshair_y>480:
        crosshair_y=480

class Capture():
    def __init__(self):
        self.capturing = False
        self.c = cv2.VideoCapture(0)
    def startCapture(self):
        global crosshair_x,crosshair_y, key_list, H, S, V, sensitivity
        print( "pressed start")
        self.capturing = True
        cap = self.c

        while(self.capturing):
            ret, frame = cap.read()
            frame = cv2.flip(frame,1)    #1 -> vertical flip
                                         #0 -> horizontal flip


            lower_color_threshold = np.array([H-sensitivity,S,V])
            upper_color_threshold = np.array([H+sensitivity,255,255])
            frame_converted_to_hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
            #frame_converted_to_hsv = cv2.medianBlur(frame_converted_to_hsv,15)    # 5 is a fairly small kernel size

            mask = cv2.inRange(frame_converted_to_hsv,lower_color_threshold,upper_color_threshold)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            #res = cv2.bitwise_and(frame,frame,mask=mask)
            #res = cv2.medianBlur(res,5)
            move_crosshair_by_keypress()


            contour = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
            if len(contour)>0:
                c = max(contour,key=cv2.contourArea)
                max_contour_area = cv2.contourArea(c)
                if max_contour_area>1000:
                    rect = cv2.minAreaRect(c)
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    cv2.drawContours(frame,[box],0,(0,0,255),2)

                    ((target_x,target_y),radius)=cv2.minEnclosingCircle(c)

                    isolated_object = frame[max(target_y-radius,0):min(target_y+radius,480),max(target_x-radius,0):min(target_x+radius,640)]
                    frame[0:100,0:100] = cv2.resize(isolated_object,(100,100))


            #Using the movement functions / moves the crosshair
            try:
                motor_vertical(int(target_y)-crosshair_y)
                motor_horizontal(int(target_x)-crosshair_x)
            except:
                pass

            #Displaying crosshair coordinates and drawing the crosshair
            cv2.circle(frame,(int(crosshair_x),int(crosshair_y)),15,(0,0,255),3)
            cv2.circle(frame,(int(crosshair_x),int(crosshair_y)),5,(0,0,255),3)
            cv2.putText(frame,"Crosshair: x:"+str(round(crosshair_x))+"    y:"+str(round(crosshair_y)),(10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 0, 255), 1)
            cv2.imshow("Capture", frame)
            cv2.waitKey(5)
        cv2.destroyAllWindows()

    def endCapture(self):
        print( "pressed End")
        self.capturing = False

    def quitCapture(self):
        print( "pressed Quit")
        cap = self.c
        cv2.destroyAllWindows()
        cap.release()
        QtCore.QCoreApplication.quit()
    def changeH(self,value):
        global H
        H = int(value)
    def changeS(self,value):
        global S
        S = int(value)
    def changeV(self,value):
        global V
        V = int(value)

class Window(QtGui.QWidget):
    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setWindowTitle('Control Panel')
        self.palette = self.palette()




        self.capture = Capture()
        self.start_button = QtGui.QPushButton('Start',self)
        self.start_button.setGeometry(10,30,50,20)
        self.start_button.clicked.connect(self.capture.startCapture)

        self.end_button = QtGui.QPushButton('End',self)
        self.end_button.clicked.connect(self.capture.endCapture)
        self.end_button.setGeometry(10,55,50,20)

        self.quit_button = QtGui.QPushButton('Quit',self)
        self.quit_button.clicked.connect(self.capture.quitCapture)
        self.quit_button.clicked.connect(self.quit_app)
        self.quit_button.setGeometry(10,80,50,20)

        self.slider1 = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.slider1.setGeometry(30,105,100,30)
        self.slider1.setRange(0,180)
        self.slider1.valueChanged.connect(lambda: self.capture.changeH(self.slider1.value()))
        self.slider1.valueChanged.connect(self.changeLabelH)
        self.slider1.valueChanged.connect(self.changeBackground)
        self.slider1.setValue(64)
        self.labelH = QtGui.QLabel('H',self)
        self.labelH.setGeometry(10,105,10,30)

        self.slider2 = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.slider2.setGeometry(30,135,100,30)
        self.slider2.setRange(0,255)
        self.slider2.valueChanged.connect(lambda: self.capture.changeS(self.slider2.value()))
        self.slider2.valueChanged.connect(self.changeLabelS)
        self.slider2.valueChanged.connect(self.changeBackground)
        self.slider2.setValue(50)
        self.labelS = QtGui.QLabel('S',self)
        self.labelS.setGeometry(10,135,10,30)


        self.slider3 = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.slider3.setGeometry(30,165,100,30)
        self.slider3.setRange(0,255)
        self.slider3.valueChanged.connect(lambda: self.capture.changeV(self.slider3.value()))
        self.slider3.valueChanged.connect(self.changeLabelV)
        self.slider3.valueChanged.connect(self.changeBackground)

        self.slider3.setValue(50)
        self.labelV = QtGui.QLabel('V',self)
        self.labelV.setGeometry(10,165,10,30)

        self.labelValorH = QtGui.QLabel('0',self)
        self.labelValorH.setGeometry(140,105,30,30)
        self.labelValorS = QtGui.QLabel('0',self)
        self.labelValorS.setGeometry(140,135,30,30)
        self.labelValorV = QtGui.QLabel('0',self)
        self.labelValorV.setGeometry(140,165,30,30)
        self.labelValorH.setText('64')
        self.labelValorS.setText('50')
        self.labelValorV.setText('50')

        self.setGeometry(100,100,200,200)
        self.show()

    def changeLabelH(self):
        self.labelValorH.setText(str(self.slider1.value()))
    def changeLabelS(self):
        self.labelValorS.setText(str(self.slider2.value()))
    def changeLabelV(self):
        self.labelValorV.setText(str(self.slider3.value()))

    def keyPressEvent(self, event):
        global key_list
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self.capture.endCapture()
        elif key == QtCore.Qt.Key_Q:
            self.capture.quitCapture()
        elif key == QtCore.Qt.Key_Return:
            self.capture.startCapture()

        elif key == QtCore.Qt.Key_W:
            key_list.append('w')
        elif key == QtCore.Qt.Key_S:
            key_list.append('s')
        elif key == QtCore.Qt.Key_A:
            key_list.append('a')
        elif key == QtCore.Qt.Key_D:
            key_list.append('d')

    def keyReleaseEvent(self, QKeyEvent):
            global key_list
            key = QKeyEvent.key()
            if key == QtCore.Qt.Key_W:
                if key_list.__contains__('w'):
                    key_list.remove('w')
            if key == QtCore.Qt.Key_S:
                if key_list.__contains__('s'):
                    key_list.remove('s')
            if key == QtCore.Qt.Key_A:
                if key_list.__contains__('a'):
                    key_list.remove('a')
            if key == QtCore.Qt.Key_D:
                if key_list.__contains__('d'):
                    key_list.remove('d')

    def quit_app(self):
        self.close()

    def changeBackground(self):
        global H,S,V
        a=colorsys.hsv_to_rgb(H/180,S/255,V/255)
        self.palette.setColor(self.backgroundRole(),QtGui.QColor(255*a[0],255*a[1],255*a[2]) )
        self.setPalette(self.palette)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
