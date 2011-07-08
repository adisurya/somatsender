import pygtk
pygtk.require('2.0')

import gtk
import gobject

#class Progress window
class ProgressWindow:
    progress_timeout_source_id = None

    def __init__(self, parent = None):
        self.parent = parent

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_SPLASHSCREEN)
        self.window.set_modal(True)
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.window.set_border_width(10)
        self.window.set_property("skip-taskbar-hint", True)
        self.window.set_title("Somat Sender")

        vbox = gtk.VBox(False, 10)

        self.progress_label = gtk.Label("Sending SMS")
        self.progress_label.show()
        vbox.add(self.progress_label)

        self.progress_bar = gtk.ProgressBar()
        self.progress_bar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
        self.progress_bar.show()
        vbox.add(self.progress_bar)

        vbox.show()
        self.window.add(vbox)

    def update_title(self, title):
        self.progress_label.set_text(title)

    def progress_timeout(self):
        self.progress_bar.pulse()

        return True

    def show_and_run(self, title = None):
        if title:
            self.update_title(title)

        self.window.show()
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.window.set_property('skip-taskbar-hint', True)

        if self.parent:
            self.window.set_transient_for(self.parent)

        if not self.progress_timeout_source_id:
            self.progress_timeout_source_id = gobject.timeout_add(500, self.progress_timeout)

        while gtk.events_pending():
            gtk.main_iteration()

    def hide_and_stop(self):
        if self.progress_timeout_source_id:
            gobject.source_remove(self.progress_timeout_source_id)
            self.progress_timeout_source_id = None;

        self.window.hide()
