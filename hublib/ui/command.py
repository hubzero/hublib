# -*- coding: utf-8 -*-
from __future__ import print_function
import ipywidgets as widgets
import sys
import os
import signal
import threading
import subprocess
import select
import time
from queue import Queue

color_rect = '<svg width="4" height="20"><rect width="4" height="20" style="fill:%s"/></svg>  %s'
colors = ["rgb(60,179,113)", "rgb(255,165,0)", "rgb(255,99,71)", "rgb(51,153,255"]


class RunCommand(object):
    """
    A widget to run a Linux command and monitor progress.

    Use this to run external code locally that might take a couple of
    minutes.  If you are using 'submit',
    you should probably use the Submit widget.

    :param label: The label for the start button.
    :param tooltip: The tooltip for the start button.
    :param start_func: Required. Function to be called when the
        start button is pressed.
    :param done_func: Optional function to be called when the
        command is completed.
    :param outcb: Optional function to be called when
        standard output is received..
    """

    SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n)
        for n in dir(signal) if n.startswith('SIG') and '_' not in n)

    def __init__(self, 
                 label='Run',
                 tooltip='Run Simulation',
                 start_func=None,
                 done_func=None,
                 outcb=None):

        self.label = label
        self.tooltip = tooltip
        self.start_func = start_func
        self.done_func = done_func
        self.outcb = outcb
        self.q = Queue()
        self.thread = 0
        self.status = None
        self.output = None

        if start_func is None:
            print("start_func is required", file=sys.stderr)

        self.but = widgets.Button(
            description=self.label,
            tooltip=self.tooltip,
            button_style='success'
        )
        self.but.on_click(self._but_cb)
        self.disabled = False
        self.w = widgets.VBox([self.but])

    def _but_cb(self, change):
        if self.but.description == self.label:
            self.but.description = 'Cancel'
            self.but.button_style = 'danger'
            self.start_func(self)
            return
        if self.but.description == 'Cancel':
            self.but.description = 'Stopping'
            self.but.button_style = 'warning'
            if self.pid:
                os.killpg(self.pid, signal.SIGTERM)

    def run(self, cmd):
        """
        Starts the command.

        :param cmd: The Linux shell command to run.
        """
        if self.output is None:
            self.output = widgets.Textarea(
                layout={'width': '100%', 'height': '400px'}
            )
            self.acc = widgets.Accordion(children=[self.output])
            self.acc.set_title(0, 'Output')
            self.acc.selected_index = None
            self.w.children = (self.acc, self.but)
        else:
            self.output.value = ""

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
                    self.output.value += u'⇉ ' + c + u' ⇇\n'
                else:
                    # write c to output widget
                    self.output.value += c
                    if self.outcb:
                        self.outcb(c)

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
            signame = RunCommand.SIGNALS_TO_NAMES_DICT[os.WTERMSIG(exitStatus)]
            errStr = "%s failed w/ signal %s\n" % (cmd, signame)
            errNum = 1
            errState = "Last Run: Canceled"
        else:
            if os.WIFEXITED(exitStatus):
                exitStatus = os.WEXITSTATUS(exitStatus)
            errStr = "\"%s\" failed w/ exit code %d\n" % (cmd, exitStatus)
            errNum = 2
            errState = "Last Run: Failed"
        self.output.value += '\n' + '='*20 + '\n' + errStr

    errState += ".  Run Time: %s" % time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    self.status.value = color_rect % (colors[errNum], errState)
    if self.done_func and errNum == 0:
        self.done_func(self)
