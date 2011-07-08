#!/usr/bin/env python

import pygtk
pygtk.require('2.0')

import gtk
import string
import httplib
import gobject
import os
import string

from  somat_window.progress_window import ProgressWindow
from  somat_window.setting_window import SettingWindow

class SomatSender:

    def __init__(self):
        self.apikey = None
        self.base_dir = os.path.expanduser('~') + "/.somatsender"

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('destroy', lambda x: gtk.main_quit())
        self.window.set_title("SOMAT SMS Sender")
        self.progress_window = ProgressWindow(self.window)
        self.setting_window = SettingWindow(self)


        if not os.path.isfile(self.base_dir + "/config.ini"):
            dialog = gtk.MessageDialog(
                self.window,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_WARNING,
                gtk.BUTTONS_OK,
                "You don't have an apikey, please enter your apikey in Application Setting!"
            )
            dialog.run()
            dialog.destroy()


        container = gtk.VBox(False)
        container.set_border_width(10)

        ui = """
            <ui>
                <menubar name="MenuBar">
                    <menu action="File">
                        <menuitem action="ImportContact" />
                        <menuitem action="Setting" />
                        <separator />
                        <menuitem action="Exit" />
                    </menu>
                </menubar>
            </ui>
            """
        ui_manager = gtk.UIManager()
        accel_group = ui_manager.get_accel_group()
        self.window.add_accel_group(accel_group)
        action_group = gtk.ActionGroup("Menu OTP")
        action_group.add_actions(
            [
                ("File", None, "_File", None, None, None),
                ("ImportContact", None, "_Import Destination", "<control>i", "Import Contact From File", self.import_contact),
                ("Setting", None, "_Configuration", None, "Setting", self.show_setting),
                ("Exit", None, "E_xit", "<control>x", "Exit This Application", gtk.main_quit)

            ]
        )
        ui_manager.insert_action_group(action_group, 0)
        ui_manager.add_ui_from_string(ui)
        menubar = ui_manager.get_widget("/MenuBar")
        #container.pack_start(menubar, False, False, 0)

        vpaned = gtk.VPaned()

        vtop = gtk.VBox(False)
        label = gtk.Label('_Destination:')
        label.set_use_underline(True)

        label.set_alignment(0,0)
        vtop.pack_start(label, False, False, 0)

        self.to_entry = gtk.TextView()
        self.to_entry.set_accepts_tab(False)
        self.to_entry.set_wrap_mode(gtk.WRAP_WORD)

        self.to_entry.set_size_request(500, 100)
        label.set_mnemonic_widget(self.to_entry)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.to_entry)
        vtop.pack_start(sw, True, True, 5)

        vpaned.add1(vtop)

        vbottom = gtk.VBox(False)

        label = gtk.Label('_Message:')
        label.set_use_underline(True)
        label.set_alignment(0,0)
        vbottom.pack_start(label, False, False, 0)

        self.message_entry = gtk.TextView()
        self.message_entry.set_accepts_tab(False)
        self.message_entry.set_wrap_mode(gtk.WRAP_WORD)
        label.set_mnemonic_widget(self.message_entry)
        entry_buffer = self.message_entry.get_buffer()
        entry_buffer.connect("changed", self.update_message_length)
        self.message_entry.set_size_request(500, 100)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.message_entry)
        vbottom.pack_start(sw, True, True, 5)
        vpaned.add2(vbottom)
        container.pack_start(vpaned, True, True, 5)

        message = self.get_text_from_buffer(self.message_entry)

        self.message_count_label = gtk.Label()
        self.message_count_label.set_text("160 chars left")

        self.message_count_label.set_alignment(0,0)
        container.pack_start(self.message_count_label, False, False, 0)

        separator = gtk.HSeparator()
        container.pack_start(separator, False, False, 5)

        button_box = gtk.HButtonBox()
        button_box.set_layout(gtk.BUTTONBOX_END)
        container.pack_start(button_box, False, False, 5)

        button = gtk.Button('_Send')
        button.connect('clicked', self.send)

        button_box.add(button)
        box = gtk.VBox(False)
        box.add(menubar)
        box.add(container)


        self.window.add(box)

    def main(self):
        self.window.show_all()
        gtk.main()

    def send(self, widget, data = None):

        # check if file config is not exists
        if not os.path.isfile(self.base_dir + "/config.ini"):
            dialog = gtk.MessageDialog(
                self.window,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_WARNING,
                gtk.BUTTONS_OK,
                "You don't have an apikey, please enter your apikey in Application Setting!"
            )
            dialog.run()
            dialog.destroy()
            return False
        else:
            f = open(self.base_dir + "/config.ini", 'r')
            self.apikey = f.read()
            f.close()

        # check if file config is empty
        if self.apikey == None or len(string.strip(self.apikey)) <= 0:
            dialog = gtk.MessageDialog(
                self.window,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_WARNING,
                gtk.BUTTONS_OK,
                "You don't have an apikey, please enter your apikey in Application Setting!"
            )
            dialog.run()
            dialog.destroy()
            return False
        print self.apikey
        gobject.idle_add(self.progress_window.show_and_run)
        to = self.get_text_from_buffer(self.to_entry)
        message = self.get_text_from_buffer(self.message_entry)
        list_recipients = string.split(to)
        xml = "<smses>"
        xml += "<apikey>" + self.apikey + "</apikey>"
        xml += "<sms>"
        xml += "<destination>"
        for recipient in list_recipients:
            xml += "<to>" + recipient + "</to>"

        xml += "</destination>"
        xml += "<message>" + message + "</message>"
        xml += "</sms>"
        xml += "</smses>"
        print xml
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
        }
        conn = httplib.HTTPConnection("sms.mondial.co.id:80")
        conn.request("POST", "/rest/v3/sms.php", xml, headers)
        #conn = httplib.HTTPConnection("mondial.co.id:80")
        #conn.request("POST", "", xml, headers)

        response = conn.getresponse()

        if response.status == 200 and response.read():
            gobject.idle_add(self.progress_window.hide_and_stop)
            dialog = gtk.MessageDialog(
                self.window,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_INFO,
                gtk.BUTTONS_OK,
                "Message sent!"
            )
            dialog.run()
            dialog.destroy()

        else:
            gobject.idle_add(self.progress_window.hide_and_stop)
            dialog = gtk.MessageDialog(
                self.window,
                gtk.DIALOG_MODAL,
                gtk.MESSAGE_INFO,
                gtk.BUTTONS_OK,
                "Error sending message!"
            )
            dialog.run()
            dialog.destroy()


    def get_text_from_buffer(self, widget):
        buf = widget.get_buffer()
        start = buf.get_start_iter()
        end = buf.get_end_iter()
        return buf.get_text(start, end, True);

    def import_contact(self, action, data = None):
        dialog = gtk.FileChooserDialog(
            'Import', self.window, gtk.FILE_CHOOSER_ACTION_OPEN,
            (
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK
            )
        )

        dialog_filter = gtk.FileFilter()
        dialog_filter.set_name("TEXT File")
        dialog_filter.add_pattern("*.txt")

        dialog.add_filter(dialog_filter)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            f = open(dialog.get_filename(), 'r')
            contact = f.read()
            buf = self.to_entry.get_buffer()
            end = buf.get_end_iter()
            buf.insert(end, ' ' + contact)

        dialog.destroy()

    def show_setting(self, action, data = None):
        self.setting_window.show()

    def update_message_length(self, widget, data = None):
        total = widget.get_char_count()
        total_2 = 160 - total
        max_char = widget.get_iter_at_offset(160)
        end = widget.get_end_iter()

        if total <= 0:
            self.message_count_label.set_text("160 chars left")
        elif total > 160:
            widget.delete(max_char, end)
        else:
            self.message_count_label.set_text(str(total_2) + " chars left")

if __name__ == "__main__":
    somat_sender = SomatSender()
    somat_sender.main()
