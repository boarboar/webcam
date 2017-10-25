import wx
import wx.lib.newevent
import camera


class MyForm(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Console", size=(800,720))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        panel = wx.Panel(self, wx.ID_ANY)
        self.camera = camera.CameraPanel(panel)
        #self.but_r = wx.RadioButton(self, wx.ID_ANY, "real", style=wx.RB_GROUP)
        #self.but_d = wx.RadioButton(self, wx.ID_ANY, "debug")
        #self.but_r.Bind(wx.EVT_RADIOBUTTON, self.OnReal)
        #self.but_d.Bind(wx.EVT_RADIOBUTTON, self.OnDbg)
        self.layout(panel)

    def layout(self, panel):

        # Add widgets to a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_pan = wx.BoxSizer(wx.HORIZONTAL)
        sizer_cam = wx.BoxSizer(wx.VERTICAL)
        sizer_but = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(sizer_pan, 2, wx.ALL|wx.EXPAND, 5)
        #sizer_but.Add(self.but_r)
        #sizer_but.Add(self.but_d)
        sizer_cam.Add(self.camera, 10, wx.ALL|wx.EXPAND, border=0)
        sizer_pan.Add(sizer_cam, 1, wx.ALL|wx.EXPAND, border=0)
        #sizer_pan.Add(sizer_but, 0, wx.ALL | wx.EXPAND)

        panel.SetSizer(sizer)
        panel.Layout()
        sizer.Fit(panel)



    def OnClose(self, event):
        self.Destroy()

    def OnReal(self, e):
        self.but_r.SetValue(True)

    def OnDbg(self, e):
        self.but_d.SetValue(True)


# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm().Show()
    app.MainLoop()