# -*- coding: utf-8 -*-
from __future__ import print_function
import ipywidgets as w
import sys
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


class RunCommand(object):
    """
    A widget to run a Linux command and monitor progress.

    Use this to run external code locally that might take a couple of
    minutes.  Results are optionally cached.

    If you are using 'submit' on a hub,
    you should use the Submit widget.

    :param label: The label for the start button.
    :param tooltip: The tooltip for the start button.
    :param start_func: Required. Function to be called when the
        start button is pressed.
    :param done_func: Optional function to be called when the
        command is completed.
    :param outcb: Optional function to be called when
        standard output is received..
    :param cachename: Optional. Name of the tool or other unique
        name that will be used for the cache directory.
    :param width: Default is 'auto'.
    """

    SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n)
        for n in dir(signal) if n.startswith('SIG') and '_' not in n)

    def __init__(self, 
                 label='Run',
                 tooltip='Run Simulation',
                 start_func=None,
                 done_func=None,
                 outcb=None,
                 width='auto',
                 cachename=None,
                 cachedir=None):
        self.label = label
        self.tooltip = tooltip
        self.start_func = start_func
        self.done_func = done_func
        self.outcb = outcb
        self.cachename = cachename
        self.q = Queue()
        self.thread = 0
        self.status = None
        self.output = None
        self.width = width

        if start_func is None:
            print("start_func is required", file=sys.stderr)

        if cachename:
            # set up cache
            if cachedir is None:
                try:
                    cachedir = os.environ['CACHEDIR']
                except:
                    print("ERROR: cachename is set, but CACHEDIR is not", file=sys.stderr)
                    print("Set the environment variable 'CACHEDIR' to the directory", file=sys.stderr)
                    print("where you want the cache to be located.", file=sys.stderr)
                    sys.exit(1)

            self.cachedir = os.path.join(cachedir, cachename)
            self.cachetabdir = os.path.join(self.cachedir, '.cache_table')
            if not os.path.isdir(self.cachedir):
                os.makedirs(self.cachedir)
            memory = Memory(cachedir=self.cachetabdir, verbose=0)

            @memory.cache
            def make_rname(*args):
                # uuid should be unique, but check just in case
                while True:
                    fname = str(uuid.uuid4()).replace('-', '')
                    if not os.path.isdir(os.path.join(self.cachedir, fname)):
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

    def run(self, cmd, runname=None):
        """
        Starts the command.

        :param cmd: The Linux shell command to run.        
        :param runname: (Optional) Name for the results.
                        Required when caching is enabled.
        """

        if self.thread:
            # cleanup old thread
            self.thread.join()

        self.runname = runname

        # FIXME. Output set by cache too!
        if self.output is None:
            self.output = w.Textarea(
                layout={'width': '100%', 'height': '400px'}
            )
            self.acc = w.Accordion(children=[self.output])
            self.acc.set_title(0, 'Output')
            self.acc.selected_index = None
        else:
            self.output.value = ""
        self.w.children = (self.acc, self.but)

        if cmd == '':
            return 

        # check cache
        if self.cachename:
            if runname is None:
                print("ERROR: run method should be called a runname when caching is on.", file=sys.stderr)
                return
            rdir = os.path.join(self.cachedir, runname)
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
                outfile = os.path.join(rdir, '.output')
                try:
                    with open(outfile) as f:
                        self.output.value = f.read()
                except:
                    self.output.value = ''
                self.w.children = [self.acc, self.status, self.but]
                # notify callback we are finished
                self.cached = True
                if self.done_func:
                    self.done_func(self, rdir)
                return
        
        self.cached = False

        self.but.description = 'Cancel'
        self.but.button_style = 'danger'

        self.thread = threading.Thread(target=poll_thread, args=(cmd, self))
        self.thread.start()
        self.pid = os.getpgid(self.q.get())

    def clear_cache(self, x):
        x.disabled = True
        if x.description == "Clear All":
            if os.path.exists(self.cachedir):
                shutil.rmtree(self.cachedir)
            if os.path.exists(self.cachetabdir):
                shutil.rmtree(self.cachetabdir)
            return
        rdir = os.path.join(self.cachedir, self.runname)
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
  
    def copy_files(self, start_time, elapsed_time):
        rdir = os.path.join(self.cachedir, self.runname)

        # shouldn't happen, but overwrite if it does
        if os.path.exists(rdir):
            shutil.rmtree(rdir)

        # Results are in current working directory.
        # Use the timestamp to copy all newer files to the cacheName.
        os.makedirs(rdir)

        # save output to cache dir
        outfile = os.path.join(rdir, '.output')
        with open(outfile, 'w') as f:
            f.write(self.output.value)

        files = os.listdir('.')
        for f in files:
            if os.path.getmtime(f) > start_time:
                shutil.copy2(f, rdir)

        with open(os.path.join(rdir, '.submit_time'), 'w') as f:
            f.write(pretty_time_delta(elapsed_time))

        return rdir


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
    self.status = self.statusbar(errNum, errState)
    self.w.children = [self.acc, self.status, self.but]

    # copy files to cache dir and return full pathname for it
    if self.cachename:
        rdir = self.copy_files(start_time, elapsed_time)
    else:
        rdir = self.runname

    if self.done_func and errNum == 0:
        if self.cachename:
            self.done_func(self, rdir)
        else:
            self.done_func(self)


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


