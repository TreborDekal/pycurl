# $Id$

## System modules
import sys, threading
from gtk import *

## PycURL module
import pycurl


class ProgressBar:

    def __init__(self, uri):
        self.round = 0.0
        win = GtkDialog()
        win.set_title("PycURL progress")
        win.show()
        vbox = GtkVBox(spacing=5)
        vbox.set_border_width(10)
        win.vbox.pack_start(vbox)
        win.set_default_size(200, 20)
        vbox.show()
        label = GtkLabel("Downloading %s" % uri)
        label.set_alignment(0, 0.5)
        vbox.pack_start(label, expand=FALSE)
        label.show()
        pbar = GtkProgressBar()
        pbar.show()
        self.pbar = pbar
        vbox.pack_start(pbar)
        win.connect("destroy", self.close_app)
        win.connect("delete_event", self.close_app)

    def progress(self, download_t, download_d, upload_t, upload_d):
        threads_enter()
        if download_t == 0:
            self.round = self.round + 0.1
            if self.round >= 1.0:  self.round = 0.0
        else:
            self.round = float(download_d) / float(download_t)
        self.pbar.update(self.round)
        threads_leave()

    def mainloop(self):
        threads_enter()
        mainloop()
        threads_leave()

    def close_app(self, *args):
        args[0].destroy()
        mainquit()


class Test(threading.Thread):

    def __init__(self, url, target_file, progress):
        threading.Thread.__init__(self)
        self.target_file = target_file
        self.progress = progress
        self.curl = pycurl.init()
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.WRITEDATA, self.target_file)
        self.curl.setopt(pycurl.FOLLOWLOCATION, 1)
        self.curl.setopt(pycurl.NOPROGRESS, 0)
        self.curl.setopt(pycurl.PROGRESSFUNCTION, self.progress)
        self.curl.setopt(pycurl.MAXREDIRS, 5)

    def run(self):
        self.curl.perform()
        self.curl.cleanup()
        self.target_file.close()
        self.progress(1.0, 1.0, 0, 0)


# Check command line args
if len(sys.argv) < 3:
    print "Usage: %s <URL> <filename>" % sys.argv[0]
    raise SystemExit

# Make a progress bar window
p = ProgressBar(sys.argv[1])
# Start thread for fetching url
Test(sys.argv[1], open(sys.argv[2], 'w'), p.progress).start()
# Enter the GTK mainloop
p.mainloop()
