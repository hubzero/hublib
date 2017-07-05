# ----------------------------------------------------------------------
# Convenience functions to run a command, optionally streaming
# stdin and stderr.  Return code, stdout, and stderr are returned.
# Works for Python 2 and 3.
# ======================================================================
#  AUTHOR: Martin Hunt, Purdue University
#   based on previous versions by
#  AUTHOR:  Derrick S. Kearney, Purdue University
#  AUTHOR:  Steve Clark, Purdue University
#  Copyright (c) 2004-2017  HUBzero Foundation, LLC
#  See LICENSE file for details.
# ======================================================================

from __future__ import print_function
import sys
import os
import subprocess
import shlex
import select
import signal
import traceback
import io
import locale

# Python 2 <-> 3 compatibility
if (sys.version_info > (3, 0)):
    # python 3 does not have a 'file' type
    file_type = io.IOBase
    usplit = shlex.split
else:
    file_type = file

    # Python2 shlex cannot handle unicode
    def usplit(cmd):
        enc = locale.getpreferredencoding()
        if isinstance(cmd, str):
            cmd = cmd.decode(enc)
        return map(lambda s: s.decode(enc), shlex.split(cmd.encode(enc)))


commandPid = 0
SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n)
    for n in dir(signal) if n.startswith('SIG') and '_' not in n)


def sig_handler(signalType, frame):
    global commandPid
    if commandPid:
        os.kill(commandPid, signal.SIGTERM)


def get_stdin(stdin):
    # returns filehandle, needs_closed, error_string
    if stdin is None:
        return None, 0, ''

    if isinstance(stdin, file_type):
        return stdin, False, ''

    if isinstance(stdin, int):
        return stdin, False, ''

    try:
        if os.path.isfile(stdin):
            try:
                # fpStdin = codecs.open(stdin, 'r', encoding='utf-8')
                fpStdin = open(stdin, 'r')
            except (IOError, OSError):
                return None, 0, "File '%s' could not be opened.\n" % (stdin)
            else:
                # success
                return fpStdin, True, ''
        else:
            return None, 0, "File %s does not exist.\n" % (stdin)
    except TypeError:
        return None, 0, "Bad argument type specified for stdin.\n"
    return None, 0, "Error trying to open file '%s'.\n" % stdin


def swrite(stream, data, enc):
    stream.write(data.decode(enc))
    stream.flush()


def executeCommand(command,
                   stdin=None,
                   streamOutput=False,
                   shell=False):
    """Execute a command.

    Arguments:
        command -- A list or string containing the command to run.
                   Strings will be converted to a list internally with shlex.

    Keyword arguments:
    stdin -- A file, fileno, or filename that will be piped as input.
    streamOuput -- Boolean. Default False. True means the output is streamed.

    Returns:
    A tuple containing three values:
        code -- Exit code. 0 is normal.
        stdout -- String containing the standard output.
        stderr -- String containing the standard error output.
    """
    global commandPid

    exitStatus = 0
    fpClose = 0
    outData = []
    errData = []
    BUFSIZ = 4096

    # set the output encoding
    if sys.stdout.encoding is None:
        outenc = locale.getpreferredencoding()
    else:
        outenc = sys.stdout.encoding

    try:
        sig_INT_handler = signal.signal(signal.SIGINT, sig_handler)
        sig_HUP_handler = signal.signal(signal.SIGHUP, sig_handler)
        sig_TERM_handler = signal.signal(signal.SIGTERM, sig_handler)
    except ValueError:
        # happens when used in a thread
        pass
    except:
        print(traceback.format_exc())

    commandStdin, fpClose, errStr = get_stdin(stdin)
    if errStr:
        if streamOutput:
            sys.stderr.write(errStr)
            sys.stderr.flush()
        return 1, "", errStr

    if shell is True or isinstance(command, list):
        commandArgs = command
    else:
        commandArgs = usplit(command)

    try:
        child = subprocess.Popen(commandArgs, bufsize=BUFSIZ,
                             stdin=commandStdin,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=shell,
                             close_fds=True)
    except Exception as e:
        # swrite(sys.stderr, e.strerror, outenc)
        sys.stderr.write(e.strerror)
        return 1, b"", e.strerror.encode(outenc)

    poller = select.poll()
    poller.register(child.stdout, select.POLLIN)
    poller.register(child.stderr, select.POLLIN)

    numfds = 2
    while numfds > 0:
        try:
            r = poller.poll()
        except select.error as err:
            print(err[1], file=sys.stderr)
            break
        for fd, flags in r:
            if flags & (select.POLLIN | select.POLLPRI):
                c = os.read(fd, BUFSIZ)
                if fd == child.stderr.fileno():
                    errData.append(c)
                    if streamOutput:
                        swrite(sys.stderr, c, outenc)
                else:
                    outData.append(c)
                    if streamOutput:
                        swrite(sys.stdout, c, outenc)
            if flags & (select.POLLHUP | select.POLLERR):
                poller.unregister(fd)
                numfds -= 1

    pid, exitStatus = os.waitpid(child.pid, 0)
    commandPid = 0
    if fpClose:
        try:
            commandStdin.close()
        except:
            pass

    try:
        # restore original signal handlers
        signal.signal(signal.SIGINT, sig_INT_handler)
        signal.signal(signal.SIGHUP, sig_HUP_handler)
        signal.signal(signal.SIGTERM, sig_TERM_handler)
    except UnboundLocalError:
        # happens when used in a thread
        pass
    except:
        print(traceback.format_exc())

    if exitStatus != 0:
        if os.WIFSIGNALED(exitStatus):
            signame = SIGNALS_TO_NAMES_DICT[os.WTERMSIG(exitStatus)]
            sys.stderr.write("%s failed w/ signal %s\n" % (command, signame))
        else:
            if os.WIFEXITED(exitStatus):
                exitStatus = os.WEXITSTATUS(exitStatus)
            sys.stderr.write("%s failed w/ exit code %d\n" % (command, exitStatus))
        if not streamOutput:
            sys.stderr.write("%s\n" % ("".join(errData)))

    return exitStatus, b"".join(outData), b"".join(errData)


def runCommand(command, stream=True):

    """Run a shell command

    Arguments:
        command -- A string that will be executed as if you typed it
                   at the command line.

    Keyword arguments:
    stream -- Boolean. Default True. The output is streamed.

    Returns:
    A tuple containing three values:
        code -- Exit code. 0 is normal.
        stdout -- Bytestring containing the standard output.
        stderr -- Bytestring containing the standard error output.
    """
    return executeCommand(command, stdin=None, streamOutput=stream, shell=True)
