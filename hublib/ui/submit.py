# -*- coding: utf-8 -*-
from __future__ import print_function
import ipywidgets as w
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
from joblib import Memory
import uuid

color_rect = '<svg width="4" height="20"><rect width="4" height="20" style="fill:%s"/></svg>  %s'
colors = ["rgb(60,179,113)", "rgb(255,165,0)", "rgb(255,99,71)", "rgb(51,153,255"]


class Submit(object):
    """
    A widget to run the submit command and monitor progress.
    Includes optional local caching of results.

    :param label: The label for the start button.
    :param tooltip: The tooltip for the start button.
    :param start_func: Required. Function to be called when the
        start button is pressed.
    :param done_func: Optional function to be called when the
        submit function is completed.
    :param cachename: Optional. Name of the tool or other unique
        name that will be used for the cache directory.
    :param outcb: Optional function to be called when
        standard output is received. Any returned value
        is written to the submit output widget, otherwise that widget
        will be empty when this is used.
    :param show_progress: Show progress bar?  Default is True.
    :param width: Default is 'auto'.
    """
    SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n)
        for n in dir(signal) if n.startswith('SIG') and '_' not in n)

    CACHEDIR = os.path.expanduser('~/data/results/.submit_cache')
    CACHETABDIR = os.path.expanduser('~/data/results/.submit_cache_table')

    regex = re.compile(r"=SUBMIT-PROGRESS=> aborted=(\d+) finished=(\d+) failed=(\d+) executing=(\d+) waiting=(\d+) setting_up=(\d+) setup=(\d+) %done=(\d*\.\d+|\d+) timestamp=(\d*\.\d+|\d+)")

    def __init__(self, 
                 label='Run',
                 tooltip='Run Simulation',
                 start_func=None,
                 done_func=None,
                 outcb=None,
                 show_progress=True,
                 width='auto',
                 cachename=None):
        self.label = label
        self.tooltip = tooltip
        self.start_func = start_func
        self.done_func = done_func
        self.outcb = outcb
        self.cachename = cachename
        self.q = Queue()
        self.thread = 0
        self.status = None
        self.txt = None
        self.show_progress = show_progress
        self.progress = None
        self.make_rname = None
        self.width = width

        if start_func is None:
            print("start_func is required.", file=sys.stderr)
            return

        if cachename:
            # set up cache
            cachedir = os.path.join(Submit.CACHEDIR, cachename)
            cachetabdir = os.path.join(Submit.CACHETABDIR, cachename)
            if not os.path.isdir(cachedir):
                os.makedirs(cachedir)
            memory = Memory(cachedir=cachetabdir, verbose=0)

            @memory.cache
            def make_rname(*args):
                # uuid should be unique, but check just in case
                while True:
                    fname = str(uuid.uuid4()).replace('-', '')
                    if not os.path.isdir(os.path.join(cachedir, fname)):
                        break
                return fname

            self.make_rname = make_rname

        self.but = w.Button(
            description=self.label,
            tooltip=self.tooltip,
            button_style='success'
        )

        self.but.on_click(self._but_cb)
        self.disabled = False
        _layout = w.Layout(
            flex_flow='column',
            justify_content='flex-start',
            width=self.width
        )
        self.w = w.VBox([self.but], layout=_layout)

    def _but_cb(self, change):
        if self.but.description == self.label:
            self.start_func(self)
            return
        if self.but.description == 'Cancel':
            self.but.description = 'Stopping'
            self.but.button_style = 'warning'
            if self.pid:
                os.killpg(self.pid, signal.SIGTERM)

    def run(self, runname, cmd):
        """
        Starts the submit command.

        :param runname: Directory name for the results.
        :param cmd: The command to pass along to the
            command-line submit. Do not include runName
            or progress.
        """

        if self.thread:
            # cleanup old thread
            self.thread.join()

        self.runname = runname

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

        cmd = "submit --runName=%s --progress submit %s" % (runname, cmd)
        if os.path.exists(runname):
            shutil.rmtree(runname)

        # check cache
        if self.cachename:
            rdir = os.path.join(Submit.CACHEDIR, self.cachename, runname)
            tfile = os.path.join(rdir, '.submit_time')
            if os.path.exists(tfile):
                # cache hit
                try:
                    with open(tfile, 'r') as f:
                        etime = f.read() 
                except:
                    etime = "unknown"

                try:
                    ctime = time.localtime(os.path.getctime(tfile))
                    ctime = time.strftime('%d %b %Y', ctime)
                except:
                    ctime = 'unknown'
                errState = "Cached: (%s, RunTime: %s)" % (ctime, etime)

                self.status = self.statusbar(0, errState)
                self.w.children = [self.status, self.but]
                # notify callback we are finished
                if self.done_func:
                    self.done_func(self, rdir)
                return

        self.but.description = 'Cancel'
        self.but.button_style = 'danger'

        if self.txt is None:
            self.txt = w.Textarea(
                layout={'width': '100%', 'height': '400px'}
            )
            self.acc = w.Accordion(children=[self.txt], width=self.width)
            self.acc.set_title(0, 'Output')
            self.acc.selected_index = None
        else:
            self.txt.value = ""
            self.progress = None
        self.w.children = [self.acc, self.but]
   
        self.thread = threading.Thread(target=poll_thread, args=(cmd, self))
        self.thread.start()
        self.pid = os.getpgid(self.q.get())

    def update(self, val):
        # parse string and update progress bars
        x = re.match(Submit.regex, val)
        if x is None:
            return

        name = ['Setup', 'Waiting', 'Running', 'Finished', 'Failed']
        style = ['warning', 'info', '', 'success', 'danger']
        matchnum = [6, 5, 4, 2, 3]

        if self.progress is None:
            # add up all the jobs
            num = 0
            for i in range(2, 8):
                num += int(x.group(i))
            self.prog = [pwidget(name[i], num, style[i]) for i in range(5)]
            self.progress = w.VBox(self.prog)
            self.w.children = [self.acc, self.status, self.progress, self.but]

        for i in range(5):
            val = int(x.group(matchnum[i]))
            if i == 0:
                # combine "setting_up" and "setup" states
                val += int(x.group(7))
            self.prog[i].value = val

    def clear_cache(self, x):
        x.disabled = True
        if x.description == "Clear All":
            tooldir = os.path.join(Submit.CACHEDIR, self.cachename)
            if os.path.exists(tooldir):
                shutil.rmtree(tooldir)
            tabdir = os.path.join(Submit.CACHETABDIR, self.cachename)
            if os.path.exists(tabdir):
                shutil.rmtree(tabdir)
            return

        rdir = os.path.join(Submit.CACHEDIR, self.cachename, self.runname)
        if os.path.exists(rdir):
            shutil.rmtree(rdir)


    def statusbar(self, num, state):
        state_str = color_rect % (colors[num], state)
        status = w.HTML(state_str)
        if not state.startswith('Cached'):
            return status

        b1 = w.Button(tooltip='Clear the cache for this run.', 
                      description='Clear Entry')
        b2 = w.Button(tooltip='Clear the entire cache for this tool.', 
                      description='Clear All', 
                      button_style='warning', 
                      icon='trash')
        b1.on_click(self.clear_cache)
        b2.on_click(self.clear_cache)
        _layout = w.Layout(
            flex='1 1  auto',
            flex_flow='row wrap'
        )
        return w.HBox([status, b1, b2], layout=_layout)

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

    self.status = self.statusbar(errNum, errState)
    self.w.children = [self.acc, self.status, self.but]
    
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
                    # parse string and update progress bars
                    if self.show_progress:
                        self.update(c)
                    if self.outcb:
                        c = self.outcb(c)
                    # write c to output widget
                    if c:
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
    self.status = self.statusbar(errNum, errState)
    self.w.children = [self.acc, self.status, self.but]

    # copy files to cache dir and return full pathname for it
    rdir = None
    if self.cachename:
        rdir = copy_files(start_time, elapsed_time, self.cachename, self.runname)
    else:
        rdir = self.runname

    # callback for processing the data
    if self.done_func and errNum == 0:
        self.done_func(self, rdir)


def pretty_time_delta(seconds):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%dd%dh%dm%ds' % (days, hours, minutes, seconds)
    elif hours > 0:
        return '%dh%dm%ds' % (hours, minutes, seconds)
    elif minutes > 0:
        return '%dm%ds' % (minutes, seconds)
    else:
        return '%ds' % (seconds,)


def copy_files(start_time, elapsed_time, toolname, runName):
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
            if os.path.getmtime(f) > start_time:
                shutil.copy2(f, rdir)

    with open(os.path.join(rdir, '.submit_time'), 'w') as f:
        f.write(pretty_time_delta(elapsed_time))

    return rdir


def pwidget(name, num, style):
    return w.IntProgress(
        value=0,
        min=0,
        max=num,
        step=1,
        description='%s:' % name,
        bar_style=style,
        orientation='horizontal'
    )
