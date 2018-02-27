# -*- coding: utf-8 -*-
from __future__ import print_function
import ipywidgets as widgets
import sys
import re
import os
import signal
import threading
import subprocess
import select
import time
import shutil
from queue import Queue

color_rect = '<svg width="4" height="20"><rect width="4" height="20" style="fill:%s"/></svg>  %s'
colors = ["rgb(60,179,113)", "rgb(255,165,0)", "rgb(255,99,71)", "rgb(51,153,255"]


class Submit(object):
    
    SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n)
        for n in dir(signal) if n.startswith('SIG') and '_' not in n)

    CACHEDIR = os.path.expanduser('~/data/results/.submit_cache')

    def __init__(self, 
                 label='Run',
                 tooltip='Run Simulation',
                 start_func=None,
                 done_func=None,
                 **kwargs):
        self.label = label
        self.tooltip = tooltip
        self.start_func = start_func
        self.done_func = done_func
        self.q = Queue()
        self.thread = 0
        self.status = None
        self.txt = None

        if start_func is None:
            print("start_func is required.", file=sys.stderr)
            return

        self.but = widgets.Button(
            description=self.label,
            tooltip=self.tooltip,
            button_style='success'
        )

        self.but.on_click(self._but_cb)
        self.disabled = kwargs.get('disabled', False)
        self.w = widgets.VBox([self.but])

    def _but_cb(self, change):
        if self.but.description == self.label:
            self.start_func(self)
            return
        if self.but.description == 'Cancel':
            self.but.description = 'Stopping'
            self.but.button_style = 'warning'
            if self.pid:
                os.killpg(self.pid, signal.SIGTERM)

    def run(self, 
            cmd,
            runname=None,
            cachename=None):

        self.runname = runname
        self.cachename = cachename

        if cachename is not None and runname is None:
            print("ERROR: 'cachename' set, but 'runname' is not.", file=sys.stderr)
            return

        # cmd should not have 'submit', '--runName' or '--progress'
        if cmd.startswith('submit'):
            print("ERROR: run method should be called with args passed to submit", file=sys.stderr)
            print("and should not contain 'submit'.", file=sys.stderr)
            return

        if '--runName' in cmd:
            print("ERROR: run method should be called with args passed to submit", file=sys.stderr)
            print("and should not contain '--runName'.", file=sys.stderr)
            return

        if '--progress' in cmd:
            print("ERROR: run method should be called with args passed to submit", file=sys.stderr)
            print("and should not contain '--progress'.", file=sys.stderr)
            return

        if runname:
            cmd = "submit --runName=%s --progress submit %s" % (runname, cmd)
        else:
            cmd = "submit --progress submit %s" % (cmd)

        self.but.description = 'Cancel'
        self.but.button_style = 'danger'

        if self.txt is None:
            self.txt = widgets.Textarea(
                layout={'width': '100%', 'height': '400px'}
            )
            self.acc = widgets.Accordion(children=[self.txt])
            self.acc.set_title(0, 'Output')
            self.acc.selected_index = None
            self.w.children = (self.acc, self.but)
        else:
            self.txt.value = ""

        if self.thread:
            # cleanup old thread
            self.thread.join()

        self.thread = threading.Thread(target=poll_thread, args=(cmd, self))
        self.thread.start()
        self.pid = os.getpgid(self.q.get())

    def _ipython_display_(self):
        self.w._ipython_display_()

    @property
    def disabled(self):
        return self.but.disabled

    @disabled.setter
    def disabled(self, newval):
        self.but.disabled = newval

    @property
    def visible(self):
        if self.w.layout.visibility is None:
            self.w.layout.visibility = 'visible'
        return self.w.layout.visibility == 'visible'

    @visible.setter
    def visible(self, newval):
        if newval:
            self.w.layout.visibility = 'visible'
            return
        self.w.layout.visibility = 'hidden'
  

def poll_thread(cmd, self):
    # set the output encoding
    outenc = sys.stdout.encoding

    start_time = time.time()
    errState = "Start Time: %s" % time.strftime("%H:%M:%S", time.localtime(start_time))
    errNum = 3
    state_str = color_rect % (colors[errNum], errState)
    if self.status is None:
        # first run. Insert status line
        self.status = widgets.HTML(state_str)
        self.w.children = (self.acc, self.status, self.but)
    else:
        self.status.value = state_str

    try:
        child = subprocess.Popen(
            cmd, bufsize=4096,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            close_fds=True,
            preexec_fn=os.setsid)
    except Exception as e:
        print(e.strerror)
        return

    self.q.put(child.pid)
    poller = select.poll()
    poller.register(child.stdout, select.POLLIN)
    poller.register(child.stderr, select.POLLIN)

    numfds = 2
    while numfds > 0:
        try:
            r = poller.poll(1)
        except select.error as err:
            print(err[1], file=sys.stderr)
            break
        for fd, flags in r:
            if flags & (select.POLLIN | select.POLLPRI):
                c = os.read(fd, 4096).decode(outenc)
                if fd == child.stderr.fileno():
                    if c.endswith('\n'):
                        c = c[:-1]
                    self.txt.value += u'⇉ ' + c + u' ⇇\n'
                else:
                    # write c to output widget
                    self.txt.value += c

            if flags & (select.POLLHUP | select.POLLERR):
                poller.unregister(fd)
                numfds -= 1
    
    pid, exitStatus = os.waitpid(child.pid, 0)
    elapsed_time = time.time() - start_time

    self.but.description = self.label
    self.but.button_style = 'success'  # green
    
    errStr = ""
    errNum = 0
    errState = "Last Run: OK"
    
    if exitStatus != 0:
        if os.WIFSIGNALED(exitStatus):
            signame = Submit.SIGNALS_TO_NAMES_DICT[os.WTERMSIG(exitStatus)]
            errStr = "%s failed w/ signal %s\n" % (cmd, signame)
            errNum = 1
            errState = "Last Run: Canceled"
        else:
            if os.WIFEXITED(exitStatus):
                exitStatus = os.WEXITSTATUS(exitStatus)
            errStr = "\"%s\" failed w/ exit code %d\n" % (cmd, exitStatus)
            errNum = 2
            errState = "Last Run: Failed"
        self.txt.value += '\n' + '='*20 + '\n' + errStr

    errState += ".  Run Time: %s" % time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    self.status.value = color_rect % (colors[errNum], errState)

    # copy files to cache dir and return full pathname for it
    rdir = None
    if self.cachename:
        rdir = copy_files(start_time, self.cachename, self.runname)
    else:
        rdir = self.runname

    # callback for processing the data
    if self.done_func and errNum == 0:
        self.done_func(self, rdir)


def copy_files(start_time, toolname, runName):
    rdir = os.path.join(Submit.CACHEDIR, toolname, runName)
    if os.path.exists(rdir):
        shutil.rmtree(rdir)

    if os.path.isdir(runName):
        # output directory was created.  Must have been a parametric run
        shutil.move(runName, rdir)
    else:
        # nonparametric run.  Results are in current working directory.
        # Use the timestamp to copy all newer files to the cacheName.
        os.makedirs(rdir)
        files = os.listdir('.')
        for f in files:
            if os.path.getmtime(f) <= start_time:
                continue
            shutil.copy2(f, rdir)
    return rdir


def rname(*args):
    return
