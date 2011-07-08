import pygtk
pygtk.require('2.0')

import gtk
import os

class SettingWindow:
    def __init__(self, caller = None):
        self.caller = caller

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Configuration")
        self.window.set_border_width(10)
        self.window.connect("delete-event", self.delete_event)
        self.window.set_property('skip-taskbar-hint', True)
        self.window.set_transient_for(self.caller.window)
        self.window.set_modal(True)

        container = gtk.VBox(False)

        label = gtk.Label("APIKEY:")
        label.set_alignment(0,0)
        container.pack_start(label, False, False, 0)

        self.apikey_entry = gtk.Entry(40)
        container.pack_start(self.apikey_entry, False, False, 0)

        label = gtk.Label("You can get APIKEY from http://sms.mondial.co.id")
        label.set_alignment(0,0)
        container.pack_start(label, False, False, 15)


        button_box = gtk.HButtonBox()
        button_box.set_layout(gtk.BUTTONBOX_END)

        button = gtk.Button("Save APIKEY")
        button.connect("clicked", self.save)
        button_box.add(button)
        container.pack_start(button_box, False, False, 0)
        self.window.add(container)

        if os.path.isfile(self.caller.base_dir + "/config.ini"):
            f = open(self.caller.base_dir + "/config.ini", 'r')
            self.apikey_entry.set_text(f.read())
            f.close()



    def show(self):
        self.window.show_all()

    def delete_event(self, event, widget, data = None):
        self.window.hide()
        return True

    def save(self, widget, data = None):

        if not os.path.isdir(self.caller.base_dir):
            os.mkdir(self.caller.base_dir)

        config_file = self.caller.base_dir + "/config.ini"

        f = open(config_file, 'w')
        f.write(self.apikey_entry.get_text())
        f.close()

        dialog = gtk.MessageDialog(
            self.window,
            gtk.DIALOG_MODAL,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_OK,
            "Apikey saved!"
        )
        dialog.run()
        dialog.destroy()







