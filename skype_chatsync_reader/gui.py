#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.6.8 (standalone edition) on Thu Jan 22 07:21:12 2015
#
import webbrowser
import wx
import os
import os.path
import sys
from threading import Thread
import traceback
import warnings
from datetime import datetime
from scanner import parse_chatsync_profile_dir

import sqlite3
from sqlite3 import Error
import base64

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class ChatSyncLoader(Thread):
    '''
    A thread object that loads the chatsync conversation objects from a given dirname.
    When finished invokes the .on_conversations_loaded on the provided main_frame object.
    '''
    
    def __init__(self, dirname, main_frame):
        Thread.__init__(self)
        self.dirname = dirname
        self.main_frame = main_frame
        self.start()
    
    def run(self):
        try:
            # print self.dirname
            conversations = parse_chatsync_profile_dir(self.dirname)
        except:
            traceback.print_exc()
            conversations = []
        wx.CallAfter(self.main_frame.on_conversations_loaded, conversations)


class ConversationSearcher(object):
    '''
    A utility class for implementing Find/FindNext in a list of conversation objects.
    '''
    
    def __init__(self, conversations=[]):
        self.conversations = conversations
        self.current_word = None
    
    def find(self, word):
        self.current_word = word
        self.current_conversation_id = 0
        self.current_message_id = 0
        return self.find_next()
    
    def find_next(self):
        if self.current_word is None or self.current_word == '' or len(self.conversations) == 0:
            return None
        while True:
            if self.current_word in self.conversations[self.current_conversation_id].conversation[self.current_message_id].text:
                result = (self.current_conversation_id, self.current_message_id)
                self.next_message()
                return result
            else:
                if not self.next_message():
                    break
        return False
        
    def next_message(self):
        if len(self.conversations) == 0:
            return False
        self.current_message_id += 1
        if self.current_message_id >= len(self.conversations[self.current_conversation_id].conversation):
            self.current_conversation_id = (self.current_conversation_id + 1) % len(self.conversations)
            self.current_message_id = 0
            if self.current_conversation_id == 0:
                return False
        return True
            
        
        
    
class MainFrame(wx.Frame):
    '''
    The main and only frame of the application.
    '''
    
    def __init__(self, *args, **kwds):
        # begin wxGlade: MainFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
        # Menu Bar
        self.menubar = wx.MenuBar()
        self.mi_menu = wx.Menu()
        self.mi_open = wx.MenuItem(self.mi_menu, wx.ID_ANY, "&Open...\tCtrl+O", "Specify a chatsync directory to load files from", wx.ITEM_NORMAL)
        self.mi_menu.AppendItem(self.mi_open)
        self.mi_find = wx.MenuItem(self.mi_menu, wx.ID_ANY, "&Find...\tCtrl+F", "Search for text in messages", wx.ITEM_NORMAL)
        self.mi_menu.AppendItem(self.mi_find)
        self.mi_find_next = wx.MenuItem(self.mi_menu, wx.ID_ANY, "Find &next\tF3", "Search for the next occurrence of the same string in messages", wx.ITEM_NORMAL)
        self.mi_menu.AppendItem(self.mi_find_next)
        self.mi_export = wx.MenuItem(self.mi_menu, wx.ID_ANY, "&Export...\tCtrl+E", "Export database", wx.ITEM_NORMAL)
        self.mi_menu.AppendItem(self.mi_export)
        self.mi_menu.AppendSeparator()



        self.Exit = wx.MenuItem(self.mi_menu, wx.ID_ANY, "&Exit", "Exit", wx.ITEM_NORMAL)
        self.mi_menu.AppendItem(self.Exit)
        self.menubar.Append(self.mi_menu, "&Menu")
        self.SetMenuBar(self.menubar)
        # Menu Bar end
        self.splitter = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_3D | wx.SP_BORDER)
        self.pane_left = wx.Panel(self.splitter, wx.ID_ANY, style=wx.STATIC_BORDER)
        self.list_conversations = wx.ListCtrl(self.pane_left, wx.ID_ANY, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES | wx.SUNKEN_BORDER)
        self.pane_right = wx.Panel(self.splitter, wx.ID_ANY, style=wx.NO_BORDER)
        self.text_chatcontent = wx.TextCtrl(self.pane_right, wx.ID_ANY, u"Use Menu \u2192 Open to load the chatsync directory.", style=wx.TE_MULTILINE | wx.TE_READONLY)
        font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.text_chatcontent.SetFont(font1)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_MENU, self.on_open, self.mi_open)
        self.Bind(wx.EVT_MENU, self.on_find, self.mi_find)
        self.Bind(wx.EVT_MENU, self.on_find_next, self.mi_find_next)
        self.Bind(wx.EVT_MENU, self.on_export, self.mi_export)
        self.Bind(wx.EVT_MENU, self.on_quit, self.Exit)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_conversation_selected, self.list_conversations)
        # end wxGlade
        
        if sys.platform == 'win32':
            icon = wx.Icon(sys.executable, wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)       
        
        self.searcher = ConversationSearcher()
        self.conversation_message_coords = []   # messageno ->(beginpos, endpos). Used to find begin and end points for selection highlights in the textbox.
        self.mi_find.Enable(False)
        self.mi_find_next.Enable(False)
        
        self.folderPath = ""
        self.contacts = []
        

        
    def __set_properties(self):
        # begin wxGlade: MainFrame.__set_properties
        self.SetTitle("Skype ChatSync File Viewer")
        self.SetSize((750, 420))
        self.text_chatcontent.SetFont(wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, ""))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MainFrame.__do_layout
        sizer_root = wx.BoxSizer(wx.HORIZONTAL)
        sizer_right = wx.BoxSizer(wx.VERTICAL)
        sizer_left = wx.BoxSizer(wx.HORIZONTAL)
        sizer_left.Add(self.list_conversations, 1, wx.ALL | wx.EXPAND, 0)
        self.pane_left.SetSizer(sizer_left)
        sizer_right.Add(self.text_chatcontent, 1, wx.ALL | wx.EXPAND, 0)
        self.pane_right.SetSizer(sizer_right)
        self.splitter.SplitVertically(self.pane_left, self.pane_right, 200)
        sizer_root.Add(self.splitter, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(sizer_root)
        self.Layout()
        # end wxGlade

    def on_open(self, event):  # wxGlade: MainFrame.<event_handler>
        default_dir = os.getenv('APPDATA', None)
        if default_dir is not None:
            default_dir = os.path.join(default_dir, 'Skype')
        else:
            default_dir = os.path.abspath('~/.Skype')
        dialog = wx.DirDialog(self, message='Please, select the "chatsync" directory within a Skype user profile:', defaultPath=default_dir, style=wx.DD_DIR_MUST_EXIST | wx.RESIZE_BORDER)
        if (dialog.ShowModal() == wx.ID_OK):
            self.list_conversations.ClearAll()
            self.text_chatcontent.Clear()
            self.text_chatcontent.SetValue("Please wait...")
            self.mi_open.Enable(False)

            # print dialog.GetPath()
            self.folderPath = dialog.GetPath()
            self.accounts()
            ChatSyncLoader(dialog.GetPath(), self)
            
    def on_quit(self, event):  # wxGlade: MainFrame.<event_handler>
        self.Close()

    def on_conversations_loaded(self, conversations):
        conversations = [c for c in conversations if not c.is_empty and len(c.conversation) > 0]
        conversations.sort(lambda x,y: x.timestamp - y.timestamp)
        self.conversations = conversations
        self.searcher = ConversationSearcher(conversations)
        
        if len(conversations) == 0:
            self.text_chatcontent.SetValue("Done. No non-empty conversations found or could be loaded.")
            self.mi_find.Enable(False)
            self.mi_find_next.Enable(False)
        else:
            self.text_chatcontent.SetValue("Done. Select a conversations using the list on the left to view.")
            self.mi_find.Enable()
            self.mi_find_next.Enable()
            self.list_conversations.ClearAll()
            self.list_conversations.InsertColumn(0, "Time")
            self.list_conversations.InsertColumn(1, "From")
            self.list_conversations.InsertColumn(2, "To")
            for c in conversations:
                dt = datetime.fromtimestamp(c.timestamp)
                self.list_conversations.Append((dt.strftime("%Y-%m-%d %H:%M"), c.participants[0], c.participants[1]))
        self.mi_open.Enable()
    
    def on_conversation_selected(self, event):  # wxGlade: MainFrame.<event_handler>
        sel_idx = self.list_conversations.GetFirstSelected()
        if sel_idx == -1:
            return
        if sel_idx >= len(self.conversations):
            self.text_chatcontent.SetValue("Error... :(")
        else:
            self.text_chatcontent.SetValue("")
            self.conversation_message_coords = []
            if len(self.conversations[sel_idx].conversation) == 0:
                self.text_chatcontent.AppendText("[empty]")
            total_len = 0
            for c in self.conversations[sel_idx].conversation:
                dt = datetime.fromtimestamp(c.timestamp).strftime("[%Y-%m-%d %H:%M]")
                txt = u"%s [%s]" % (dt, c.author)
                if c.is_edit:
                   txt += u" [edit]"
                txt += u": "
                txt += c.text + "\n"
                txt.replace('\r\n', '\n')
                text_len = len(txt)                 
                if len(os.linesep) == 2:
                    # Note that there is a discrepancy between lineseparators of the control's "Value" and its actual internal state
                    text_len += txt.count('\n')
                self.conversation_message_coords.append((total_len, total_len + text_len - 2))
                total_len += text_len
                self.text_chatcontent.AppendText(txt)

    def on_find(self, event):  # wxGlade: MainFrame.<event_handler>
        dlg = wx.TextEntryDialog(self,message="Enter text to search for:")
        if (dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != ''):
            result = self.searcher.find(dlg.GetValue())
            if result is None:
                wx.MessageBox(self, 'Text not found', 'Search result', wx.ICON_INFORMATION | wx.OK)
            else:
                self.highlight(result)
    
    def on_find_next(self, event):  # wxGlade: MainFrame.<event_handler>
        if self.searcher.current_word is None:
            self.on_find(event)
        else:
            result = self.searcher.find_next()
            if result is None:
                wx.MessageBox(self, 'Reached end of conversation list', 'Search result', wx.ICON_INFORMATION | wx.OK)
            else:
                self.highlight(result)
    
    def on_export(self, event): #export to HTML
        print "EXPORT."
        sel_idx = self.list_conversations.GetFirstSelected()
        if sel_idx == -1:
            return
        if sel_idx >= len(self.conversations):
            self.text_chatcontent.SetValue("Error... :(")
        else:
            if len(self.conversations[sel_idx].conversation) == 0:
                print "[empty]"
            total_len = 0

            participants = self.conversations[sel_idx].participants
            template = open("template.html").read()
            chat = open("chat.html").read()
            date_template = open("date.html").read()
            #print template
            template = template.replace('FIRST_USER_USERNAME', participants[0])
            template = template.replace('FIRST_USER_FULLNAME', self.get_account_fullname(participants[0])) #TODO
            template = template.replace('SECOND_USER_USERNAME', participants[1])
            template = template.replace('SECOND_USER_FULLNAME', self.get_account_fullname(participants[1])) #TODO

            template = template.replace('FIRST_IMAGE_DATA', self.get_account_img(participants[0])) #TODO
            template = template.replace('SECOND_IMAGE_DATA', self.get_account_img(participants[1])) #TODO

            txt = ""
            idx = 0
            current_date = ''
            last_date = ''
            for c in self.conversations[sel_idx].conversation:
                idx = idx+1
                # dt = datetime.fromtimestamp(c.timestamp).strftime("[%Y-%m-%d %H:%M]")
                # txt = u"%s [%s]" % (dt, c.author)
                # if c.is_edit:
                #    txt += u" [edit]"
                # txt += u": "
                # txt += c.text + "\n"
                # txt.replace('\r\n', '\n')
                # text_len = len(txt)                 
                # if len(os.linesep) == 2:
                #     # Note that there is a discrepancy between lineseparators of the control's "Value" and its actual internal state
                #     text_len += txt.count('\n')
                #print txt
                #format html
                current_date = datetime.fromtimestamp(c.timestamp).strftime("<span class='weekday'>%A</span> %d-%m-%Y")
                if current_date != last_date:
                    txt += date_template.replace('DATE',current_date)
                    last_date = current_date

                temp = chat
                temp = temp.replace('FIRST_USER_USERNAME', self.get_account_fullname(participants[0]))
                temp = temp.replace('SECOND_USER_USERNAME', self.get_account_fullname(participants[1]))
                # temp = temp.replace("DATE_TIME", datetime.fromtimestamp(c.timestamp).strftime("[%Y-%m-%d %H:%M]"))
                temp = temp.replace('CHAT_CONTENT', c.text)
                temp = temp.replace('AUTHOR', self.get_account_fullname(c.author))
                temp = temp.replace('TIME', datetime.fromtimestamp(c.timestamp).strftime("%H:%M"))
                css_class = 'remote'
                if c.author == participants[0]:
                    css_class = 'local'
                temp = temp.replace('CSS_CLASS', css_class)

                txt += temp
            
            template = template.replace("DATA_CHAT_CONTENT", txt.encode('utf-8'))
            template = template.replace('TOTAL_MESSAGE', str(idx))
            template = template.replace('CURRENT_DATETIME', datetime.now().strftime("%Y-%m-%d %H:%M"))
            file_name = "Skype_chat_%s_%s_%s" % (participants[0], participants[1], datetime.now().strftime("%Y-%m-%d"))
            export_file = open(file_name+".html", "w")
            export_file.write(template)
            export_file.close()
            print "DONE"
            webbrowser.open('file://' + os.path.realpath(file_name+".html"))

    def accounts(self):
        # print self.folderPath
        path = os.path.dirname(self.folderPath) + "/main.db"
        # print path
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM Contacts")
        rows = cur.fetchall()
        self.contacts = rows


    def get_account_fullname(self, skypename):
        for c in self.contacts:
            if c[3] == skypename:
                return str(c[6]).encode('utf-8')
        
        return skypename
    
    def get_account_img(self, skypename):
        import binascii
        for c in self.contacts:
            # print c[3]
            if c[3] == skypename:
                if c[78]:
                    x = bytearray(c[78])
                    return base64.b64encode(self.fix_image_raw(x))
                else:
                    break
        default_img = "iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAABV0RVh0Q3JlYXRpb24gVGltZQA2LzIwLzA4DqTMIgAAABx0RVh0U29mdHdhcmUAQWRvYmUgRmlyZXdvcmtzIENTNAay06AAAAQ2SURBVHic7Z3NauM8FIbfTgQqCGpQiMEFQ70L9P6voFeQRaALQwMODSggsMFQgUO/xYeHgWlnPI2PjuTqge4aydZjSUc/lm+6rntHgo0f3Bfw3UkCmEkCmEkCmEkCmEkCmEkCmEkCmEkCmBHcFzAF5xze3t4AAJfLBX3f//X/siyDlBJaawgR7m0Ge2Vt2+J4PKJt2y/9vus6AIAQAmVZoiiKOS9vNm5CmwtyzqGu6y8X/GdorVFVFaSUs6Z7LUEIGIYB1lp0XQdjDGleSikURRFM08QuoO977Pd7DMPgPe88z/Hw8MAqgjUK4ix8ADDGYL/fwznHkj/AKGAYBjw/P7MV/kjf99jtdp9GVtSwNEHGGBwOB/bC/xUhBB4fH6GU8pqvVwFUEc5cKKWw3W69RkreBIxVPQaqqvI2bvDWB1wuF19ZXU3TNN7ySnNBHzAMA/l4ZMSbgNfXV19ZzYKvWuBFwMvLC6y1PrKaDeecFwnkAqy1OJ1O1NmQ0DQNecRGKmAYBtR1TZkFOcfjkTR9UgFN0wQ12PoKbduSjpLJBAzDgPP5TJW8VygjIjIB1tron/4RygCCTADnDOPcUN5LEjARqn4gCZjIuMY8N2kqYiJU44EkYCKpBjBDFdElAROhWrgnE3B3d0eVNAtU95NqwES01iTpJgETybKMJF0yASHsOpsTqoV6MgG+t3fEShLADJmA1Wq1KAlRDsSWJCC6PgCgu2jf5Hkep4ClLMhQ7pJLS5IToKzJaUlyArvdLr7JuFj3An2Ec47sfsgEcL3wQEV0nfBSIqCR29tbknTTSHgi0U1HU03fckD5MJEJoJq+5SBKAVLKxTRDUQoA/h/CL4FoBSylH6Bc3yafjIs9HKVuRsnXhKniZ19Q7+4gFxD79pT1ek2aPrmAmPsBKWX8NUApFe2YoCxL8jy87AvabrdRhaRCCFRV5eWavR7WwX0+0BR8H9jhdWecUir4PoFy/fcjvG9NDH1c4Hv6JO0N/QUhhPew2buAkCfoOJpH7wJCDkk5Dnf1LmC1WgXZEXNNn7P0ASEK4LomFgHr9Tq49weo53w+g0VAaM0QR/QzwhaGhjQe4HwY2ASEFA1xPgxpIAbeh4FNQOwLNXPBenh3KIyfPeGATcDhcODK+jfqukZd1yxH7HhfDzDGwFob7HlCWmsUReGtXyAX0LYtrLVBF/pHSClRliX5p05IBIwFvoS3ZIQQP2sFxVzRbAL6vsfpdFpEoX9GlmXYbDazrhVfJSCGNp0CIQQ2mw3u7++vHsT9swDnHKy1MMYs7jWkr3DtZ7EmCRi/83U+n4P9/EgIaK1//k2V8UcB45Me29HzITBVxm8CvkNn6ps/ybjpuu7dOQdjDIwx36oz5UAphTzPobWGlBI3T09P76kz5UEphR+p8Pno+z6tB3CTBDCTBDCTBDCTBDDzH7726OxO0Z6SAAAAAElFTkSuQmCC"

        return default_img

    def fix_image_raw(self, raw):
        """Returns the raw image bytestream with garbage removed from front."""
        JPG_HEADER = "\xFF\xD8\xFF\xE0\x00\x10JFIF"
        PNG_HEADER = "\x89PNG\r\n\x1A\n"
        if isinstance(raw, unicode):
            raw = raw.encode("latin1")
        if JPG_HEADER in raw:
            raw = raw[raw.index(JPG_HEADER):]
        elif PNG_HEADER in raw:
            raw = raw[raw.index(PNG_HEADER):]
        elif raw.startswith("\0"):
            raw = raw[1:]
            if raw.startswith("\0"):
                raw = "\xFF" + raw[1:]
        return raw



    def highlight(self, coords):
        self.list_conversations.Select(coords[0])
        wx.CallAfter(self.highlight_message, coords)
    
    def highlight_message(self, coords):
        if self.list_conversations.GetFirstSelected() == coords[0]:
            self.text_chatcontent.SetSelection(*self.conversation_message_coords[coords[1]])
            self.text_chatcontent.SetFocus()
            
# end of class MainFrame

class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        main_frame = MainFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(main_frame)
        main_frame.Show()
        return 1

# end of class MyApp

def main():
    app = MyApp(0)
    app.MainLoop()

if __name__ == "__main__":
    main()
