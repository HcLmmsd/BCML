#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.3 on Wed Apr 10 06:24:52 2019
#

import argparse
import configparser
import wx
import threading
import bcml
import glob
import os
import platform
import sys
import shutil
import time


from bcml import mergepacks, mergerstb

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class BcmlFrame(wx.Frame):
    mods = {}
    cemudir = ''

    def __init__(self, *args, **kwds):
        # begin wxGlade: BcmlFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        wx.Frame.__init__(self, *args, **kwds)
        self.list_mods = wx.ListBox(self, wx.ID_ANY, choices=["<No mods installed>"])
        self.button_install = wx.Button(self, wx.ID_ANY, "Install...")
        self.button_uninstall = wx.Button(self, wx.ID_ANY, "Uninstall")
        self.button_change = wx.Button(self, wx.ID_ANY, "Change Priority...")
        self.button_update = wx.Button(self, wx.ID_ANY, "Update")
        self.button_export = wx.Button(self, wx.ID_ANY, "Export...")
        self.button_explore = wx.Button(self, wx.ID_ANY, "Explore...")
        self.text_output = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY|wx.TE_MULTILINE)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        self.button_install.Bind(wx.EVT_BUTTON, self.OnInstall)
        self.button_uninstall.Bind(wx.EVT_BUTTON, self.OnUninstall)
        self.button_update.Bind(wx.EVT_BUTTON, self.OnUpdate)
        self.button_export.Bind(wx.EVT_BUTTON, self.OnExport)
        self.button_explore.Bind(wx.EVT_BUTTON, self.OnExplore)
        self.button_change.Bind(wx.EVT_BUTTON, self.OnChangePriority)

        self.Bind(EVT_BCMLDONE, self.OnBcmlDone)

        self.GetCemuDir()
        self.LoadMods()
        self.CheckPython()

        redir = RedirectText(self.text_output)
        sys.stdout = redir
        sys.stderr = redir

    def __set_properties(self):
        # begin wxGlade: BcmlFrame.__set_properties
        self.SetTitle("BCML: BotW Cemu Mod Loader")
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWFRAME))
        self.SetPosition((64, 32))
        self.SetMaxClientSize((512,-1))
        self.list_mods.SetMinSize((360, 200))
        self.button_install.SetToolTip("Install a new mod")
        self.button_uninstall.SetToolTip("Uninstall the selected mod")
        self.button_change.SetToolTip("Allows you to change the load priority of the selected mod")
        self.button_update.SetToolTip("Manually trigger a refresh of the RSTB and remerge packs")
        self.button_export.SetToolTip("Exports all installed mods as a single modpack ZIP")
        self.button_explore.SetToolTip("Opens the selected mod's folder in Windows Explorer")
        self.text_output.SetMinSize((-1, 120))
        self.text_output.SetBackgroundColour(wx.Colour(33, 33, 33))
        self.text_output.SetForegroundColour(wx.Colour(239, 239, 239))
        # end wxGlade

        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data' , 'bcml.ico'), wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

    def __do_layout(self):
        # begin wxGlade: BcmlFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        bitmap_1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data' , 'logo-smaller.png'), wx.BITMAP_TYPE_ANY))
        sizer_1.Add(bitmap_1, 0, 0, 0)
        label_list = wx.StaticText(self, wx.ID_ANY, "Mods currently installed:")
        sizer_4.Add(label_list, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer_4.Add(self.list_mods, 0, wx.ALL, 8)
        sizer_2.Add(sizer_4, 1, 0, 0)
        sizer_3.Add(self.button_install, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer_3.Add(self.button_uninstall, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer_3.Add(self.button_change, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer_3.Add(self.button_update, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer_3.Add(self.button_export, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer_3.Add(self.button_explore, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer_2.Add(sizer_3, 0, wx.EXPAND, 0)
        sizer_1.Add(sizer_2, 1, wx.ALL | wx.EXPAND, 8)
        sizer_1.Add(self.text_output, 0, wx.ALL | wx.EXPAND, 16)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

    def CheckPython(self):
        ver = platform.python_version_tuple()
        if int(ver[0]) < 3 or (int(ver[0]) >= 3 and int(ver[1]) < 7):
            dlg = wx.MessageDialog(self, f'BCML is only supported on Python 3.7 or higher. You are running {platform.python_version()} The program will now close.', 'BCML Error', wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            os._exit(1)

        is_64bits = sys.maxsize > 2**32
        if not is_64bits:
            dlg = wx.MessageDialog(self, 'BCML is only supported in 64-bit Python, but it looks like you\'re running 32-bit. The program will now close.', 'BCML Error', wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            os._exit(1)

    def GetCemuDir(self):
        workdir = os.path.join(os.getenv('LOCALAPPDATA'), 'bcml')
        os.makedirs(workdir, exist_ok=True)

        cdirfile = os.path.join(workdir,'.cdir')
        if not os.path.exists(cdirfile):
            while not glob.glob(os.path.join(self.cemudir, '*emu*exe')):
                dlg = wx.DirDialog(self, "Choose the directory where Cemu is installed:", style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST)
                if dlg.ShowModal() == wx.ID_OK:
                    self.cemudir = dlg.GetPath()
                else:
                    os._exit(0)
                dlg.Destroy()
            with open(cdirfile, 'w') as cdir:
                cdir.write(os.path.abspath(self.cemudir))
            self.cemudir = os.path.join(self.cemudir, 'graphicPacks')
        else:
            with open(cdirfile, 'r') as cdir:
                self.cemudir = os.path.join(cdir.readline(), 'graphicPacks')

    def LoadMods(self):
        self.mods = {}
        self.list_mods.Clear()
        for i, rulef in enumerate(glob.iglob(os.path.join(self.cemudir, 'BotwMod*', 'rules.txt'))):
            rules = configparser.ConfigParser()
            rules.read(rulef)
            self.mods[i] = {
                'name' : rules['Definition']['name'].replace('"', ''),
                'priority' : rules['Definition']['fsPriority'],
                'path' : os.path.dirname(rulef)
            }
            if self.mods[i]['name'] == 'BCML': continue
            self.list_mods.Append(f'{self.mods[i]["priority"]}. {self.mods[i]["name"]}')

    def OnBcmlDone(self, event):
        self.EnableButtons()
        self.LoadMods()

    def DisableButtons(self):
        self.button_export.Disable()
        self.button_uninstall.Disable()
        self.button_install.Disable()
        self.button_update.Disable()
        self.button_change.Disable()

    def EnableButtons(self):
        self.button_export.Enable()
        self.button_uninstall.Enable()
        self.button_install.Enable()
        self.button_update.Enable()
        self.button_change.Enable()

    def OnInstall(self, event):
        installDlg = InstallDialog(self)
        installDlg.ShowModal()
        if installDlg.GetReturnCode() == wx.ID_YES:
            args = argparse.Namespace()
            args.__setattr__('directory', self.cemudir)
            args.__setattr__('mod', installDlg.install_opts['file'])
            args.__setattr__('shrink',installDlg.install_opts['shrink'])
            args.__setattr__('leave', installDlg.install_opts['leave'])
            args.__setattr__('nomerge',installDlg.install_opts['nomerge'])
            args.__setattr__('priority', installDlg.install_opts['priority'])
            args.__setattr__('verbose', False)
            bcmlInstall = BcmlThread(self, bcml.install.main, args)
            self.DisableButtons()
            bcmlInstall.start()
        else:
            pass

    def OnUninstall(self, event):
        if self.list_mods.GetSelection() < 0:
            dlg = wx.MessageDialog(self, 'No mod selected to uninstall', 'BCML Error', wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        selmod = self.mods[self.list_mods.GetSelection()]
        if wx.MessageBox(f'Are you sure you want to uninstall {selmod["name"]}?','BCML Confirm',wx.YES_NO,parent=self) != wx.YES:
            return
        print('Uninstalling...')
        nomerge = True
        try:
            if os.path.exists(os.path.join(selmod['path'], 'packs.log')): nomerge = False
            shutil.rmtree(selmod['path'])
        except Exception as e:
            print(f'There was an error uninstalling {selmod["name"]}')
            print(e)
            return
        args = argparse.Namespace()
        args.__setattr__('directory', self.cemudir)
        args.__setattr__('verbose', False)
        args.__setattr__('nomerge', nomerge)
        bcmlUninstall = BcmlThread(self, bcml.update.main, args)
        self.DisableButtons()
        bcmlUninstall.start()

    def OnUpdate(self, event):
        args = argparse.Namespace()
        args.__setattr__('directory', self.cemudir)
        args.__setattr__('verbose', False)
        args.__setattr__('nomerge', False)
        bcmlUpdate = BcmlThread(self, bcml.update.main, args)
        self.DisableButtons()
        bcmlUpdate.start()

    def OnExport(self, event):
        exportDlg = ExportDialog(self)
        exportDlg.ShowModal()
        if exportDlg.GetReturnCode() != wx.YES:
            return
        else:
            args = argparse.Namespace()
            args.__setattr__('output', exportDlg.export_options['file'])
            args.__setattr__('directory', self.cemudir)
            args.__setattr__('onlymerges', exportDlg.export_options['mergeonly'])
            args.__setattr__('mlc', (exportDlg.export_options['format'] == 2))
            args.__setattr__('sdcafiine', (exportDlg.export_options['format'] == 1))
            args.__setattr__('title', exportDlg.export_options['titleid'].replace('-',''))
            bcmlUpdate = BcmlThread(self, bcml.export.main, args)
            print(f'Exporting mods to {args.output}...')
            self.DisableButtons()
            bcmlUpdate.start()

    def OnExplore(self, event):
        if self.list_mods.GetSelection() < 0:
            dlg = wx.MessageDialog(self, 'No mod selected to explore', 'BCML Error', wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            os.system(f'explorer {self.mods[self.list_mods.GetSelection()]["path"]}')

    def OnChangePriority(self, event):
        if self.list_mods.GetSelection() < 0:
            dlg = wx.MessageDialog(self, 'No mod selected to change priority', 'BCML Error', wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        selmod = self.mods[self.list_mods.GetSelection()]

        dlgPriority = wx.TextEntryDialog(self, f'Enter the new priority for {selmod["name"]}','Change Mod Priority')
        if dlgPriority.ShowModal() != wx.ID_OK: return
        p = dlgPriority.GetValue()
        dlgPriority.Destroy()

        if not is_number(p):
            dlg = wx.MessageDialog(self, f'{p} is not a valid number', 'BCML Error', wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        else:
            p = int(p)
            if os.path.exists(os.path.join(self.cemudir, f'BotwMod_mod{p}')):
                dlg = wx.MessageDialog(self, f'Priority {p} is already being used by another mod', 'BCML Error', wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                self.DisableButtons()
                moddir = os.path.join(self.cemudir, f'BotwMod_mod{p:03}')
                remerge = os.path.exists(os.path.join(selmod['path'], 'packs.log'))

                try:
                    shutil.move(selmod['path'], moddir)

                    rules = configparser.ConfigParser()
                    rules.read(os.path.join(moddir,'rules.txt'))
                    rules['Definition']['fsPriority'] = str(p)
                    with open(os.path.join(moddir,'rules.txt'), 'w') as rulef:
                        rules.write(rulef)

                    print('Updating RSTB configuration...')
                    mergerstb.main(self.cemudir, "quiet")
                    print()
                    if remerge: 
                        print('Updating merged packs...')
                        mergepacks.main(self.cemudir, False)
                    print()
                    print('Mod configuration updated successfully')
                except Exception as e:
                    print(f'There was an error changing the priority of {selmod["name"]}')
                    print('Check error.log for details')
                    workdir = os.path.join(os.getenv('LOCALAPPDATA'),'bcml')
                    with open(os.path.join(workdir,'error.log'),'w') as elog:
                        elog.write(str(e))
                finally:
                    self.EnableButtons()
                    self.LoadMods()

myEVT_BCMLDONE = wx.NewEventType()
EVT_BCMLDONE = wx.PyEventBinder(myEVT_BCMLDONE, 1)
class BcmlDoneEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid):
        wx.PyCommandEvent.__init__(self, etype, eid)

class BcmlThread(threading.Thread):
    def __init__(self, parent, target, *args):
        threading.Thread.__init__(self)
        self._parent = parent
        self._target = target
        self._args = args

    def run(self):
        self._target(*self._args)
        evt = BcmlDoneEvent(myEVT_BCMLDONE, -1)
        wx.PostEvent(self._parent, evt)

class RedirectText:
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,string):
        self.out.WriteText(string)

# end of class BcmlFrame

class InstallDialog(wx.Dialog):
    install_opts = {}

    def __init__(self, *args, **kwds):
        # begin wxGlade: InstallDialog.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.file_ctrl = wx.FilePickerCtrl(self, wx.ID_ANY, "")
        self.spin_ctrl_priority = wx.SpinCtrl(self, wx.ID_ANY, "100", min=100, max=998)
        self.checkbox_shrink = wx.CheckBox(self, wx.ID_ANY, "Update RSTB entries for files which have not grown")
        self.checkbox_leave = wx.CheckBox(self, wx.ID_ANY, "Do not remove RSTB entries for files with sizes that cannot be calculated")
        self.checkbox_nomerge = wx.CheckBox(self, wx.ID_ANY, "Disable pack merging for this mod")
        self.button_yinstall = wx.Button(self, wx.ID_ANY, "Install")
        self.button_ninstall = wx.Button(self, wx.ID_ANY, "Cancel")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        self.button_yinstall.Bind(wx.EVT_BUTTON, self.OnInstall)
        self.button_ninstall.Bind(wx.EVT_BUTTON, self.OnCancel)

    def __set_properties(self):
        # begin wxGlade: InstallDialog.__set_properties
        self.SetTitle("Install a Mod")
        self.spin_ctrl_priority.SetToolTip("This specifies the load priority of the mod. By default, mods start with a priority of 100 and go up by 1 for each installation. Higher priority mods will overwrite conflicting changes from lower priority ones.")
        self.checkbox_shrink.SetToolTip("By default, BCML will ignore files with equal or smaller sizes to what was originally in the RSTB. This option forces it to update anyway. I can't think of any reason to use this except as a last ditch effort to stop blood moon spam on a heavily modded setup.")
        self.checkbox_leave.SetToolTip("By default, BCML will delete RSTB entries when the RSTB size of a file cannot be calculated. This option leaves them alone. Be warned: This can cause instability.")
        self.checkbox_nomerge.SetToolTip("By default, BCML will try to merge changes when multiple mods modify the same pack files. Sometimes this will break things when mods have completely incompatible changes. This option disables pack merging on the current mod. Any packs with conflicting changes will either give way to or trump the whole pack depending on load priority.")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: InstallDialog.__do_layout
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_7 = wx.GridSizer(1, 2, 0, 0)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5.Add(self.file_ctrl, 0, wx.ALL | wx.EXPAND, 8)
        label_1 = wx.StaticText(self, wx.ID_ANY, "Mod Priority: ")
        sizer_6.Add(label_1, 0, wx.BOTTOM | wx.RIGHT | wx.TOP, 8)
        sizer_6.Add(self.spin_ctrl_priority, 0, wx.BOTTOM | wx.RIGHT | wx.TOP, 8)
        sizer_5.Add(sizer_6, 1, wx.ALL | wx.EXPAND, 8)
        label_2 = wx.StaticText(self, wx.ID_ANY, "Advanced options:")
        sizer_5.Add(label_2, 0, wx.ALL, 8)
        sizer_5.Add(self.checkbox_shrink, 0, wx.ALL, 8)
        sizer_5.Add(self.checkbox_leave, 0, wx.ALL, 8)
        sizer_5.Add(self.checkbox_nomerge, 0, wx.ALL, 8)
        sizer_7.Add(self.button_yinstall, 0, 0, 0)
        sizer_7.Add(self.button_ninstall, 0, wx.RIGHT, 0)
        sizer_5.Add(sizer_7, 1, wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        self.SetSizer(sizer_5)
        sizer_5.Fit(self)
        self.Layout()
        # end wxGlade

    def OnCancel(self, event):
        self.Close()

    def OnInstall(self, event):
        self.install_opts = {
            'file': self.file_ctrl.GetPath(),
            'shrink': self.checkbox_shrink.IsChecked(),
            'leave': self.checkbox_leave.IsChecked(),
            'nomerge': self.checkbox_nomerge.IsChecked(),
            'priority': self.spin_ctrl_priority.GetValue()
        }
        if self.install_opts['file'] == '':
            dlg = wx.MessageDialog(self, 'You must select a mod to install!', 'BCML Error', wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.EndModal(wx.ID_YES)

# end of class InstallDialog

class ExportDialog(wx.Dialog):
    export_options = {}

    def __init__(self, *args, **kwds):
        # begin wxGlade: ExportDialog.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((400, 285))
        self.choice_format = wx.Choice(self, wx.ID_ANY, choices=["Graphic Pack", "SDCafiine", "MLC"])
        self.checkbox_mergeonly = wx.CheckBox(self, wx.ID_ANY, "Only include BCML-generated RSTB and merged packs, not all\nmod files")
        self.text_ctrl_titleid = wx.TextCtrl(self, wx.ID_ANY, "00050000101C9400")
        self.button_export = wx.Button(self, wx.ID_ANY, "Export")
        self.button_cancel = wx.Button(self, wx.ID_ANY, "Cancel")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        self.button_cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
        self.button_export.Bind(wx.EVT_BUTTON, self.OnExport)

    def __set_properties(self):
        # begin wxGlade: ExportDialog.__set_properties
        self.SetTitle("Export Mod Configuration")
        self.SetSize((400, 350))
        self.choice_format.SetSelection(0)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ExportDialog.__do_layout
        sizer_8 = wx.BoxSizer(wx.VERTICAL)
        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        label_3 = wx.StaticText(self, wx.ID_ANY, "This function will combine all of the mods you have installed and turn them into a single modpack that can be installed by itself on Cemu or Wii U.\n\nFor devs: This can be used as way to create compatibility patches.")
        label_3.Wrap(384)
        sizer_8.Add(label_3, 0, wx.ALL | wx.EXPAND, 8)
        label_4 = wx.StaticText(self, wx.ID_ANY, "Export Format: ")
        sizer_8.Add(label_4, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer_8.Add(self.choice_format, 0, wx.ALL, 8)
        sizer_8.Add(self.checkbox_mergeonly, 0, wx.ALL, 8)
        label_5 = wx.StaticText(self, wx.ID_ANY, "TitleID (only needed for SDCafiine and MLC):")
        sizer_8.Add(label_5, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        sizer_8.Add(self.text_ctrl_titleid, 0, wx.ALL | wx.EXPAND, 8)
        sizer_9.Add(self.button_export, 0, 0, 0)
        sizer_9.Add(self.button_cancel, 0, 0, 0)
        sizer_8.Add(sizer_9, 1, wx.ALIGN_RIGHT | wx.ALL, 8)
        self.SetSizer(sizer_8)
        self.Layout()
        # end wxGlade

    def OnCancel(self, event):
        self.Close()

    def OnExport(self, event):
        fileDlg = wx.FileDialog(self, "Export Mod Zip", wildcard="ZIP files (*.zip)|*.zip",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if fileDlg.ShowModal() == wx.ID_CANCEL:
            return
        self.export_options = {
            'file': fileDlg.GetPath(),
            'format': self.choice_format.GetSelection(),
            'mergeonly': self.checkbox_mergeonly.IsChecked(),
            'titleid': self.text_ctrl_titleid.GetValue()
        }
        self.EndModal(wx.YES)

# end of class ExportDialog

class MyApp(wx.App):
    def OnInit(self):
        self.frame = BcmlFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MyApp

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def main():
    app = MyApp(0)
    app.MainLoop()

if __name__ == "__main__":
    main()
