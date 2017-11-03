import wx
#import sys
import wx.lib.newevent
import cv2
import urllib2
from urllib2 import URLError
import socket
import numpy as np
import threading
import time

CameraEvent, EVT_CAMERA_EVENT = wx.lib.newevent.NewEvent()

RedrawEvent, EVT_RDR_EVENT = wx.lib.newevent.NewEvent()

class StreamClientThread(threading.Thread):
    def __init__(self, wnd, url, proxysetting, thr_type=1, sigma=0.5):
        threading.Thread.__init__(self)
        self.__lock=threading.Lock()
        self.wnd=wnd
        self.__url = url
        self.__proxysetting=proxysetting
        self.__stop = False
        self.stream=None
        self.bytes=''
        self.frame=None
        self.conts = None
        self.bmp = None
        self.bmp_c = None
        self.thr_type = thr_type  # static
        self.sigma = sigma
        self.lines_rho=1
        self.lines_phi_div=180
        self.lines_threshold = 100
        self.lines_minLineLength = 56
        self.lines_maxLineGap = 100

        self.setDaemon(1)

    def SetThresholdType(self, tt) :
        self.thr_type = tt

    def SetSigma(self, sigma) :
        self.sigma = sigma

    def SetLinesRho(self, rho):
        self.lines_rho = rho

    def SetLinesPhiDiv(self, phi_div):
        self.lines_phi_div = phi_div

    def SetLinesThres(self, threshold):
        self.lines_threshold = threshold

    def SetLinesMinLineLength(self, minLineLength):
        self.lines_minLineLength = minLineLength

    def SetLinesMaxLineGap(self, maxLineGap):
        self.lines_maxLineGap = maxLineGap

    def stop(self) : self.__stop=True
    def lock(self) : self.__lock.acquire()
    def unlock(self) : self.__lock.release()

    def contoursCanny(self, img_g):
        img_cont = cv2.bilateralFilter(img_g, 11, 17, 17)
        edged = cv2.Canny(img_cont, 30, 200)
        # note - findCounters is destructive, so it will destroy edge !
        # _, contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        _, contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #_, contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def contoursBfilt(self, img_g):
        img_cont = cv2.bilateralFilter(img_g, 11, 17, 17)
        ret, thresh = cv2.threshold(img_cont, 127, 255, cv2.THRESH_BINARY)
        _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def contoursStd(self, img_g):
        ret, thresh = cv2.threshold(img_g, 127, 255, cv2.THRESH_BINARY)
        _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        ###ret, thresh = cv2.threshold(img_cont, 127, 255, cv2.THRESH_BINARY_INV)
        ###ret, thresh = cv2.threshold(img_cont, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        ###thresh = cv2.adaptiveThreshold(img_cont, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        ###thresh = cv2.adaptiveThreshold(img_cont, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        ###_, contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)    return contours
        return contours

    def edges(self, img):
        h, w = img.shape[:2]
        low_bound = 0.05
        hi_bound = 0.5

        minLineLength = 20
        maxLineGap = 2

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        low_thresh, high_thresh = 50, 150
        if self.thr_type == 2:
            high_thresh, thresh_im = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            low_thresh = 0.5 * high_thresh
        elif self.thr_type == 3:
            # auto canny
            v = np.median(gray)
            # apply automatic Canny edge detection using the computed median
            low_thresh = int(max(0, (1.0 - self.sigma) * v))
            high_thresh = int(min(255, (1.0 + self.sigma) * v))

        print("Thresholds %s (%s): %s %s : %s %s %s %s %s" % (self.thr_type, self.sigma, low_thresh, high_thresh,
                                                              self.lines_rho, self.lines_phi_div, self.lines_threshold,
                                                              self.lines_minLineLength, self.lines_maxLineGap))

        #gray = cv2.bilateralFilter(gray, 11, 17, 17) #?
        #edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        # apperture size 1, 3, 5, or 7
        edges = cv2.Canny(gray, low_thresh, high_thresh, apertureSize=3, L2gradient=False)
        #edges = cv2.Canny(gray, 80, 120)
        #edges = cv2.Canny(gray, 30, 200)


        #lines = cv2.HoughLinesP(edges, 1, np.pi / 2, 1, None, minLineLength, maxLineGap)
        #lines = cv2.HoughLinesP(edges, 1, np.pi / 180,
        #                        threshold=60, minLineLength=40, maxLineGap=8)

        lines = cv2.HoughLinesP(edges, self.lines_rho, np.pi / self.lines_phi_div,
                                threshold=self.lines_threshold, minLineLength=self.lines_minLineLength, maxLineGap=self.lines_maxLineGap)

        if lines is None:
            return img, cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)


        print("Lines : %s" % (len(lines)))

        y_lim_1 = int(h * (1-low_bound))
        y_lim_0 = int(h * (1 - hi_bound))
        cv2.line(img, (0, y_lim_1), (w-1, y_lim_1), (0, 0, 255), 1)
        cv2.line(img, (0, y_lim_0), (w - 1, y_lim_0), (0, 0, 255), 1)

        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)

        for line in lines:
            for x1, y1, x2, y2 in line:
                if abs(y1-y2)>40 and abs(x1-x2)*100/abs(y1-y2)<10 and min(y1,y2)<y_lim_1 and max(y1,y2)>y_lim_0:  #5% inclination
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)


        """
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)

        if lines is None:
            return

        for line in lines:
            for rho, theta in line:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))

                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        """
        return img, cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

    def countoursProcess(self, img, contours):
        cntf = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            rect_area = w * h
            extent = float(area) / rect_area
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            dim = np.sqrt(area)
            if rect_area > 0:
                solidity1 = float(hull_area) / rect_area
            else:
                solidity1 = 1
            if w > 2 and h > 2 and (w > 10 or h > 10):
                # if dim/max(w,h) > 0.15 and w > 2 and h > 2 and (w > 10 or h > 10):
                # if extent > 0.01 and w>2 and h>2 and (w>10 or h>10):
                # if solidity1 > 0.7 and w>2 and h>2:
                # peri = cv2.arcLength(cnt, True)
                # cnt = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                cntf.append(cnt)

        # contours=cntf

        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        print("found %s countours" % (len(contours)))

        # for c in contours :
        #    print(c)
        cv2.drawContours(img, contours, -1, (0, 255, 0), 1)
        return

    def loadimg(self):
        if self.stream is None : return None
        while True:
            try:
                self.bytes+=self.stream.read(1024)
                a = self.bytes.find('\xff\xd8')
                b = self.bytes.find('\xff\xd9')
                if a!=-1 and b!=-1:
                    jpg = self.bytes[a:b+2]
                    self.bytes= self.bytes[b+2:]
                    img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
                    h, w  = img.shape[:2]
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    #img = cv2.rectangle(img, (w/3, h/3), (w*2/3, h*2/3), (0, 255, 0), 3)
                    #cv2.putText(img, 'CAM1', (0, h), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 2, cv2.LINE_AA)

                    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                    #contours = self.contoursBfilt(gray)
                    #self.countoursProcess(img, contours)

                    img, conts = self.edges(img)

                    return img, conts
                    #return gray
            except Exception as e:
                print('failed to read')
                print(e)
                return None

    def run (self):

        print('starting streamer...')

        if self.__proxysetting is not None :
            proxy = urllib2.ProxyHandler(self.__proxysetting)
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)

        while not self.__stop:
            time.sleep(5.0)
            print('opening stream at %s ...' % (self.__url))
            self.stream=None
            try:
                self.stream=urllib2.urlopen(self.__url, timeout=20.0)
                print('stream opened')
            except URLError as e:
                print(e.reason)
                continue
            except socket.timeout as e:
                print("timeout")
                continue

            self.frame, self.conts = self.loadimg()

            if self.frame is not None:
                print(self.frame.shape)
                self.height, self.width = self.frame.shape[:2]
                self.bmp = wx.BitmapFromBuffer(self.width, self.height, self.frame)
                self.bmp_c = wx.BitmapFromBuffer(self.width, self.height, self.frame)

            else:
                print "Error no webcam image"
                continue

            while not self.__stop and self.frame is not None:
                #self.frame = self.loadimg()
                #if self.frame is not None:
                #self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                self.lock()
                self.bmp.CopyFromBuffer(self.frame)
                self.bmp_c.CopyFromBuffer(self.conts)
                self.unlock()
                #print "Fire event"
                event = RedrawEvent(bmp=self.bmp,  bmp_c=self.bmp_c)
                wx.PostEvent(self.wnd, event)
                time.sleep(0.1)
                self.frame, self.conts = self.loadimg()

        print "Streamer stopped"


class CameraPanel(wx.Window):
    " camera panel"
    def __init__(self, parent):
        wx.Window.__init__(self, parent, wx.ID_ANY, style=wx.SIMPLE_BORDER, size=(640, 480))

        self.isDebug = False

        self.imgSizer = (480, 360)
        #self.imgSizer = (640, 480)
        self.pnl = wx.Panel(self, -1)
        self.pnl_c = wx.Panel(self, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.pnl_c, 1, flag=wx.EXPAND, border=5)
        sizer.Add(self.pnl, 1, flag=wx.EXPAND, border=5)
        self.SetSizer(sizer)

        #self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.image = wx.EmptyImage(self.imgSizer[0],self.imgSizer[1])
        self.imageBit = wx.BitmapFromImage(self.image)
        self.staticBit = wx.StaticBitmap(self.pnl, wx.ID_ANY, self.imageBit)

        self.image_c = wx.EmptyImage(self.imgSizer[0], self.imgSizer[1])
        self.imageBit_c = wx.BitmapFromImage(self.image_c)
        self.staticBit_c = wx.StaticBitmap(self.pnl_c, wx.ID_ANY, self.imageBit_c)

        #self.vbox.Add(self.staticBit)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(EVT_RDR_EVENT, self.onRedrawEvent)

        self.isPlaying = False
        self.staticBit.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)

        self.thr_type = 1  # static
        self.streamthread = None
        self.sigma = 0.33
        self.lines_rho = 1
        self.lines_phi_div = 180
        self.lines_threshold = 60
        self.lines_minLineLength = 40
        self.lines_maxLineGap = 8


        #self.SetSize(self.imgSizer)
        #self.pnl.SetSizer(self.vbox)
        #self.vbox.Fit(self)
        #self.Show()

    def SetThresholdType(self, tt) :
        self.thr_type = tt
        if self.streamthread is not None :
            self.streamthread.SetThresholdType(self.thr_type)

    def SetSigma(self, sigma) :
        self.sigma = sigma/100.0
        if self.streamthread is not None :
            self.streamthread.SetSigma(self.sigma)

    def SetLinesRho(self, rho) :
        self.lines_rho = rho
        if self.streamthread is not None :
            self.streamthread.SetLinesRho(self.lines_rho)

    def SetLinesPhiDiv(self, phi_div) :
        self.lines_phi_div = phi_div
        if self.streamthread is not None :
            self.streamthread.SetLinesPhiDiv(self.lines_phi_div)

    def SetLinesThres(self, threshold):
        self.lines_threshold = threshold
        if self.streamthread is not None:
            self.streamthread.SetLinesThres(self.lines_threshold)

    def SetLinesMinLineLength(self, minLineLength) :
        self.lines_minLineLength = minLineLength
        if self.streamthread is not None :
            self.streamthread.SetLinesMinLineLength(self.lines_minLineLength)

    def SetLinesMaxLineGap(self, maxLineGap) :
        self.lines_maxLineGap = maxLineGap
        if self.streamthread is not None :
            self.streamthread.SetLinesMaxLineGap(self.lines_maxLineGap)


    def SetSrcType(self, st):
        self.isDebug = st==2

    def onRedrawEvent(self, evt):
        #print "Update"
        """
        self.streamthread.lock()
        self.staticBit.SetBitmap(evt.bmp)
        self.Refresh()
        self.streamthread.unlock()
        """
        #Size  = self.staticBit.ClientSize
        Size  = self.pnl.ClientSize
        self.streamthread.lock()
        image=wx.ImageFromBitmap(evt.bmp)
        image_c = wx.ImageFromBitmap(evt.bmp_c)
        self.streamthread.unlock()
        image = image.Scale(Size[0], Size[1], wx.IMAGE_QUALITY_HIGH)
        bmp = wx.BitmapFromImage(image)
        self.staticBit.SetBitmap(bmp)
        image_c = image_c.Scale(Size[0], Size[1], wx.IMAGE_QUALITY_HIGH)
        bmp_c = wx.BitmapFromImage(image_c)
        self.staticBit_c.SetBitmap(bmp_c)
        self.Refresh()


    def OnPaint(self, event):
        """
        if self.isPlaying :
            self.streamthread.lock()
            self.Refresh()
            self.streamthread.unlock()
        """
        self.Refresh()

    def OnMouseLeftUp(self, evt):
        if self.isPlaying :
            self.isPlaying=False
            self.streamthread.stop()
            self.streamthread = None
        else :
            self.isPlaying=True
            if self.isDebug :
                self.streamthread =StreamClientThread(self,
                                                #"http://88.53.197.250/axis-cgi/mjpg/video.cgi?resolution=320x240",
                                                "http://iris.not.iac.es/axis-cgi/mjpg/video.cgi?resolution=320x240",
                                                #"http://webcam.st-malo.com/axis-cgi/mjpg/video.cgi?resolution=352x288",
                                                  {'http': 'proxy.reksoft.ru:3128'})
            else :
                self.streamthread =StreamClientThread(self, 'http://192.168.1.120:8080/?action=stream', None)
            self.streamthread.SetThresholdType(self.thr_type)
            self.streamthread.SetSigma(self.sigma)
            self.streamthread.start()
