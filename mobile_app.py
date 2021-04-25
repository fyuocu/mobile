import kivy
import threading
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
import socket
import time
import sys

HEADERSIZE = 8
s = None
ACK = 2
full_msg=''
new_msg = True
msglen = 0
close = False
a = None
messages = "Wait! Connecting To Robot"
class MainScreen(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.infotext = Label(text=messages, size_hint=(1,4))
        self.add_widget(self.infotext)

        self.stop = Button(text="STOP")
        self.stop.bind(on_press=self.stopbtn)
        self.add_widget(self.stop)
        # function stop
        self.shutdown = Button(text="SHUT DOWN")
        self.shutdown.bind(on_press=self.shutdownbtn)
        self.add_widget(self.shutdown)
        # function shutdown
        self.goto = Button(text="GO TO")
        self.goto.bind(on_press=self.gotobtn)
        self.add_widget(self.goto)
        #function destination
        self.turnoff = Button(text="EXIT")
        self.turnoff.bind(on_press=self.turnoffbtn)
        self.add_widget(self.turnoff)
        #function turnoff
        Clock.schedule_once(self.connect,1)

    def reconnect(self,instance):
        global a
        while not self.connect_base(self):
            time.sleep(1)
        a = threading.Thread(target=self.listen, args=(self,))
        a.start()
    
    def connect(self, _):
        threading.Thread(target=self.reconnect, args=(self,)).start()
        return
    
    def connect_base(self,instance):
        try:
            global s
            global messages
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("raspberrypi",56142))
            messages = "Connected to Robot"
            self.changetext(self,messages)
        except Exception as e:
            messages = "Please make sure the robot is connected to network!"
            self.changetext(self, messages)
            return False
        
        return True

    def listen(self,instance):
        try:
            global HEADERSIZE
            global new_msg
            global full_msg
            global msglen
            global close
            while not close:
                msg = s.recv(HEADERSIZE)
                if not len(msg):
                    messages="Please make sure the robot is connected to network!"
                    self.changetext(self,messages)
                else:
                    if new_msg:
                        msglen = int(msg[:HEADERSIZE])
                        new_msg =False
                    else:
                        de_msg = msg.decode("utf-8")
                        full_msg += de_msg
                    if len(full_msg) == msglen:
                        self.changetext(self,full_msg)
                        new_msg = True
                        full_msg=''
                      
        except Exception as e:
            messages = "Please make sure the robot is connected to network!"
            self.changetext(self, messages)
            s.close()
            self.connect(self)
            return
    
    def changetext(self,instance, msg):
        self.infotext.text = msg
        clientApp.destination.changetext(clientApp.destination, msg)
        
    def senddata(self,instance, cmd):
        try: 
            global ACK
            global messages
            if ACK == 1:
                ACK = 2
            else:
                ACK = 1
            msg = f'{ACK:<{HEADERSIZE}}' + f'{cmd:<{HEADERSIZE}}';
            s.send(bytes(msg,"utf-8"))
            print("send data start")
            print("send data end")
            return True
        except Exception:
            messages = "Please make sure the robot is connected to network!"
            self.changetext(self, messages)
            return False
    
    def stopbtn(self, instance):
        self.senddata(self,0)
    
    def shutdownbtn(self, instance):
        self.senddata(self,1)
    
    def gotobtn(self, instance):
        clientApp.sm.current = "Dest"

    def turnoffbtn(self,instance):
        global a
        global s
        close = True;
        if s is not None:
            s.close()
        if a is not None:
            a.join()
        App.get_running_app().stop()
        Window.close()
    
class Destination(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1

        self.infotext = Label(text=messages, size_hint=(1,5))
        self.add_widget(self.infotext)

        self.point1 = Button(text="Point 1")
        self.point1.bind(on_press=lambda instance:self.pointbtn(instance, 21))
        self.add_widget(self.point1)
        # function 1
        self.point2 = Button(text="Point 2")
        self.point2.bind(on_press=lambda instance:self.pointbtn(instance, 22))
        self.add_widget(self.point2)
        # function 2
        self.point3 = Button(text="Point 3")
        self.point3.bind(on_press=lambda instance:self.pointbtn(instance, 23))
        self.add_widget(self.point3)
        #function 3
        self.point4 = Button(text="Point 4")
        self.point4.bind(on_press=lambda instance:self.pointbtn(instance, 24))
        self.add_widget(self.point4)
        # function 4
        self.point5 = Button(text="Point 5")
        self.point5.bind(on_press=lambda instance:self.pointbtn(instance, 25))
        self.add_widget(self.point5)
        # function 5

        self.back = Button(text="Back")
        self.back.bind(on_press=self.backbtn)
        self.add_widget(self.back)
        # function 5
        
    def pointbtn(self,instance, go):
        global messages
        if not clientApp.main.senddata(self,go):
            self.changetext(self, messages)
        pass
    
    def backbtn(self,instance):
        clientApp.sm.current="Main"
        pass

    def changetext(self,instance,msg):
        self.infotext.text = msg
        
class MyApp(App):
    def build(self):
        self.sm = ScreenManager()
        
        self.main = MainScreen()
        screen = Screen(name = "Main")
        screen.add_widget(self.main)
        self.sm.add_widget(screen)

        self.destination = Destination()
        screen = Screen(name="Dest")
        screen.add_widget(self.destination)
        self.sm.add_widget(screen)

        return self.sm
        
if __name__ == "__main__":
    clientApp = MyApp()
    clientApp.run()
