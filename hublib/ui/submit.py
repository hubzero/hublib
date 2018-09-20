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
from filelock import Timeout, FileLock

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
        self.attachid = None

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

    def _check_cache(self):
        # Returns the attachid if the cached job is still running.
        # Otherwise returns None.  Called with a lock on the cache dir.

        try:
            tfile = os.path.join(self.rdir, '.submit_time')
            with open(tfile, 'r') as f:
                etime = f.read() 
        except:
            return '', 0.0  # invalid cache

        try:
            idname = os.path.join(self.rdir, '.attachid')
            with open(idname, 'r') as f:
                attachid = f.read().strip()
            return attachid, float(etime)
        except:
            pass

        try:
            ctime = time.localtime(os.path.getctime(tfile))
            ctime = time.strftime('%d %b %Y', ctime)
        except:
            ctime = 'unknown'
        errState = "Cached: (%s, RunTime: %s)" % (ctime, etime)

        self.status = self.statusbar(0, errState)
        self.w.children = [self.status, self.but]
        # notify callback we are finished
        self.cached = True
        if self.done_func:
            self.done_func(self, self.rdir)
        return None, None

    def run(self, runname, cmd):
        """
        Starts the submit command.

        :param runname: Name for the results.
        :param cmd: The command to pass along to the
            command-line submit. Do not include runName
            or progress.
        """
        self.but.disabled = True

        if self.thread:
            # cleanup old thread
            self.thread.join()

        self.runname = runname
        self.attachid = None
        
        # cmd should not have 'submit', '--runName' or '--progress'
        if cmd.startswith('submit'):
            print("ERROR: run method should be called with args passed to submit", file=sys.stderr)
            print("and should not contain 'submit'.", file=sys.stderr)
            self.but.disabled = False
            return

        if '--runName' in cmd:
            print("ERROR: run method should be called with args passed to submit", file=sys.stderr)
            print("and should not contain '--runName'.", file=sys.stderr)
            self.but.disabled = False
            return

        if '--progress' in cmd:
            print("ERROR: run method should be called with args passed to submit", file=sys.stderr)
            print("and should not contain '--progress'.", file=sys.stderr)
            self.but.disabled = False
            return

        is_local = False
        if '--local' in cmd:
            is_local = True

        if self.cachename:
            self.rdir = os.path.join(Submit.CACHEDIR, self.cachename, runname)
        else:
            self.rdir = runname

        self.start_time = 0.0
        # check cache
        if self.cachename and os.path.exists(self.rdir):
            lockfile = os.path.join(self.rdir, '.lock')
            lock = FileLock(lockfile)
            try:
                with lock.acquire(timeout=120):
                    self.attachid, self.start_time = self._check_cache()
            except Timeout:
                print("ERROR: Could not acquire lock '%s'" % lockfile)
                print("If another process is not holding it, you should remove the file.")
                sys.exit(1)
            if self.attachid is None:
                # job finished. cache is complete
                self.but.disabled = False
                return

        self.cached = False

        if self.start_time == 0.0:
            self.start_time = time.time()

        # Remove any old local directory results
        if self.attachid:
            cmd = "submit --attach %s" % (self.attachid)
        else:
            if os.path.exists(runname):
                shutil.rmtree(runname)

            # create cache directory
            if self.cachename and not os.path.exists(self.rdir):
                os.makedirs(self.rdir)

            # Run submit and immediately detach.  This gives us the attach id so we
            # can attach even if we are later disconnected.
            if is_local or self.cachename is None or self.cachename == '':
                cmd = "submit --runName=%s --progress submit %s" % (runname, cmd)
            else:
                cmd = "submit --detach --runName=%s --progress submit %s" % (runname, cmd)
                stdout = subprocess.check_output(cmd, shell=True)
                x = re.search(r"--attach (\d+)", stdout.decode('UTF-8'))
                if x is None:
                    print("Error:", cmd)
                    print(stdout.decode('UTF-8'))
                    self.but.disabled = False
                    return
                self.attachid = x.group(0).split()[1]
                cmd = "submit --attach %s" % (self.attachid)
                lockfile = os.path.join(self.rdir, '.lock')
                lock = FileLock(lockfile)
                try:
                    with lock.acquire(timeout=120):
                        with open(os.path.join(self.rdir, '.attachid'), 'w') as f:
                            f.write(self.attachid)
                        with open(os.path.join(self.rdir, '.submit_time'), 'w') as f:
                            f.write(str(self.start_time))
                except Timeout:
                    print("ERROR: Could not acquire lock '%s'" % lockfile)
                    print("If another process is not holding it, you should remove the file.")
                    sys.exit(1)

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
        # FIXME: need to lock each directory
        x.disabled = True
        if x.description == "Clear All":
            tooldir = os.path.join(Submit.CACHEDIR, self.cachename)
            if os.path.exists(tooldir):
                shutil.rmtree(tooldir)
            tabdir = os.path.join(Submit.CACHETABDIR, self.cachename)
            if os.path.exists(tabdir):
                shutil.rmtree(tabdir)
            return

        if os.path.exists(self.rdir):
            shutil.rmtree(self.rdir)

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
  
    def copy_files(self, errnum, etime):
        try:
            os.remove(os.path.join(self.rdir, '.attachid'))
        except OSError:
            pass

        # FIXME: Lock
        
        if os.path.isdir(self.runname):
            # output directory was created.  Must have been a parametric run
            if errnum > 0:
                shutil.rmtree(self.rdir)
            else:
                os.system('/bin/cp -pr %s/* %s' % (self.runname, self.rdir))
                shutil.rmtree(self.runname)
        else:
            # nonparametric run.  Results are in current working directory.
            # Use the timestamp to copy all newer files to the cacheName.
            if errnum == 0:
                files = os.listdir('.')
                for f in files:
                    if os.path.getmtime(f) >= self.start_time:
                        shutil.copy2(f, self.rdir)

        if errnum == 0:
            with open(os.path.join(self.rdir, '.submit_time'), 'w') as f:
                f.write(pretty_time_delta(etime))

        return self.rdir


def poll_thread(cmd, self):
    # set the output encoding
    outenc = sys.stdout.encoding
    errState = "Start Time: %s" % time.strftime("%H:%M:%S", time.localtime(self.start_time))
    errNum = 3

    self.status = self.statusbar(errNum, errState)
    self.but.disabled = False
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
    elapsed_time = time.time() - self.start_time
    self.but.description = self.label
    self.but.button_style = 'success'  # green
    self.but.disabled = True
    
    errStr = ""
    errNum = 0
    errState = "Last Run: OK"
    
    if exitStatus != 0:
        if os.WIFSIGNALED(exitStatus):
            signame = Submit.SIGNALS_TO_NAMES_DICT[os.WTERMSIG(exitStatus)]
            errStr = "\"%s\" failed w/ signal %s\n" % (cmd, signame)
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
    if self.cachename:
        rdir = self.copy_files(errNum, elapsed_time)
    else:
        rdir = self.runname

    # callback for processing the data
    if self.done_func and errNum == 0:
        self.done_func(self, rdir)
    self.but.disabled = False


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
