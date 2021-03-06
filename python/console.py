import wx
import wx.lib.newevent
import camera


class MyForm(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Console", size=(800,720))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        panel = wx.Panel(self, wx.ID_ANY)
        self.camera = camera.CameraPanel(panel)
        self.but_r = wx.RadioButton(panel, wx.ID_ANY, "real", style=wx.RB_GROUP)
        self.but_d = wx.RadioButton(panel, wx.ID_ANY, "debug")
        self.but_t1 = wx.RadioButton(panel, wx.ID_ANY, "Fix", style=wx.RB_GROUP)
        self.but_t2 = wx.RadioButton(panel, wx.ID_ANY, "Auto2")
        self.but_t3 = wx.RadioButton(panel, wx.ID_ANY, "Auto3")
        self.sld_1 = wx.Slider(panel, value=33, minValue=1, maxValue=100,
                             style=wx.SL_VERTICAL | wx.SL_LABELS)
        self.sld_line_rho = wx.Slider(panel, value=1, minValue=1, maxValue=10,
                               style=wx.SL_VERTICAL | wx.SL_LABELS)
        self.sld_line_phi_div = wx.Slider(panel, value=180, minValue=1, maxValue=180,
                                      style=wx.SL_VERTICAL | wx.SL_LABELS)
        self.sld_line_thres = wx.Slider(panel, value=60, minValue=1, maxValue=100,
                                          style=wx.SL_VERTICAL | wx.SL_LABELS)
        self.sld_line_minLineLength = wx.Slider(panel, value=40, minValue=1, maxValue=200,
                                        style=wx.SL_VERTICAL | wx.SL_LABELS)
        self.sld_line_maxLineGap = wx.Slider(panel, value=8, minValue=1, maxValue=100,
                                                style=wx.SL_VERTICAL | wx.SL_LABELS)

        self.but_r.Bind(wx.EVT_RADIOBUTTON, self.OnReal)
        self.but_d.Bind(wx.EVT_RADIOBUTTON, self.OnDbg)
        self.but_t1.Bind(wx.EVT_RADIOBUTTON, self.OnSetT1)
        self.but_t2.Bind(wx.EVT_RADIOBUTTON, self.OnSetT2)
        self.but_t3.Bind(wx.EVT_RADIOBUTTON, self.OnSetT3)
        self.sld_1.Bind(wx.EVT_SLIDER, self.OnSliderScroll)
        self.sld_line_rho.Bind(wx.EVT_SLIDER, self.OnSliderScroll_Line_Rho)
        self.sld_line_phi_div.Bind(wx.EVT_SLIDER, self.OnSliderScroll_Line_PhiDiv)
        self.sld_line_thres.Bind(wx.EVT_SLIDER, self.OnSliderScroll_Line_Thres)
        self.sld_line_minLineLength.Bind(wx.EVT_SLIDER, self.OnSliderScroll_Line_minLineLength)
        self.sld_line_maxLineGap.Bind(wx.EVT_SLIDER, self.OnSliderScroll_Line_maxLineGap)

        self.layout(panel)

    def layout(self, panel):

        # Add widgets to a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_pan = wx.BoxSizer(wx.VERTICAL)
        sizer_cam = wx.BoxSizer(wx.VERTICAL)
        sizer_but = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(sizer_pan, 2, wx.ALL|wx.EXPAND, 5)
        sizer_but.Add(wx.StaticText(panel, label='SRC:'))
        sizer_but.Add(self.but_r)
        sizer_but.Add(self.but_d)
        sizer_but.Add(wx.StaticText(panel, label='THR:'))
        sizer_but.Add(self.but_t1)
        sizer_but.Add(self.but_t2)
        sizer_but.Add(self.but_t3)
        sizer_but.Add(wx.StaticText(panel, label='S:'))
        sizer_but.Add(self.sld_1)
        sizer_but.Add(wx.StaticText(panel, label='Rho:'))
        sizer_but.Add(self.sld_line_rho)
        sizer_but.Add(wx.StaticText(panel, label='PhiD:'))
        sizer_but.Add(self.sld_line_phi_div)
        sizer_but.Add(wx.StaticText(panel, label='LineTh:'))
        sizer_but.Add(self.sld_line_thres)
        sizer_but.Add(wx.StaticText(panel, label='MinLLen:'))
        sizer_but.Add(self.sld_line_minLineLength)
        sizer_but.Add(wx.StaticText(panel, label='MaxLGap:'))
        sizer_but.Add(self.sld_line_maxLineGap)

        sizer_cam.Add(self.camera, 10, wx.ALL|wx.EXPAND, border=0)
        sizer_pan.Add(sizer_cam, 1, wx.ALL|wx.EXPAND, border=0)
        sizer_pan.Add(sizer_but, 0, wx.ALL | wx.EXPAND)

        panel.SetSizer(sizer)
        panel.Layout()
        sizer.Fit(panel)



    def OnClose(self, event):
        self.Destroy()

    def OnReal(self, e):
        self.camera.SetSrcType(1)

    def OnDbg(self, e):
        self.camera.SetSrcType(2)

    def OnSetT1(self, e):
        self.camera.SetThresholdType(1)

    def OnSetT2(self, e):
        self.camera.SetThresholdType(2)

    def OnSetT3(self, e):
        self.camera.SetThresholdType(3)

    def OnSliderScroll(self, e):
        self.camera.SetSigma(self.sld_1.GetValue())

    def OnSliderScroll_Line_Rho(self, e):
        self.camera.SetLinesRho(self.sld_line_rho.GetValue())

    def OnSliderScroll_Line_PhiDiv(self, e):
        self.camera.SetLinesPhiDiv(self.sld_line_phi_div.GetValue())

    def OnSliderScroll_Line_Thres(self, e):
        self.camera.SetLinesThres(self.sld_line_thres.GetValue())

    def OnSliderScroll_Line_minLineLength(self, e):
        self.camera.SetLinesMinLineLength(self.sld_line_minLineLength.GetValue())

    def OnSliderScroll_Line_maxLineGap(self, e):
        self.camera.SetLinesMaxLineGap(self.sld_line_maxLineGap.GetValue())


# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm().Show()
    app.MainLoop()