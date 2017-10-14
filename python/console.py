import wx
import wx.lib.newevent
import camera


class MyForm(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Console", size=(800,720))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        panel = wx.Panel(self, wx.ID_ANY)
        self.camera = camera.CameraPanel(panel)
        self.layout(panel)

    def layout(self, panel):

        # Add widgets to a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_pan = wx.BoxSizer(wx.HORIZONTAL)
        sizer_charts = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(sizer_pan, 2, wx.ALL|wx.EXPAND, 5)

        sizer_charts.Add(self.camera, 1, wx.ALL|wx.EXPAND, border=0)
        sizer_pan.Add(sizer_charts, 1, wx.ALL|wx.EXPAND, border=0)

        panel.SetSizer(sizer)
        panel.Layout()
        sizer.Fit(panel)



    def OnClose(self, event):
        self.Destroy()

# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm().Show()
    app.MainLoop()