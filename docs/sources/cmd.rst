Command Module
==============

Convenience functions to run a command, optionally streaming
stdin and stderr.  Return code, stdout, and stderr are returned.

If the shell is used, via executeCommand(shell=True), or by using runCommand(), it is the application’s responsibility to ensure that all whitespace and metacharacters are quoted appropriately to avoid shell injection vulnerabilities.

.. function:: executeCommand(command,
                   stdin=None,
                   streamOutput=False,
                   shell=False)

    Runs a command, optionally streaming the output to the notebook cell.

   :param command: The command to run.  If it is a list, it should contain the executable
                   followed by any parameters.  Strings will be parsed into a list, unless **shell** is set.
                   If shell is set, the command will be executed throught the shell (normally bash).
   :type list or string:
   :param stdin:  A file that will be used as stdin for the command. Necessary to set stdin
                  when shell is False.
   :type string, int, or file object:
   :param streamOutput: Streams output to the cell as the command is executing.
   :type boolean:
   :param shell: If shell is True, the command string is passed to the shell.
   :type boolean:
   :return: A tuple containing the (return_code, stdout, stderr).  return_code is 0 when executing completed successfully. stdout and stderr are bytestrings.

    >>> executeCommand(['date'])
    (0, 'Wed Jul  5 10:54:06 EDT 2017\n', '')

    >>> executeCommand(['date'], streamOutput=True)
    Wed Jul  5 10:54:08 EDT 2017
    (0, 'Wed Jul  5 10:54:08 EDT 2017\n', '')

    >>> executeCommand(['date', '--utc'], streamOutput=True)
    Wed Jul  5 14:54:23 UTC 2017
    (0, 'Wed Jul  5 14:54:23 UTC 2017\n', '')

.. function:: runCommand(command, stream=True)

    Runs a shell command, optionally streaming the output to the notebook cell.
    Internally calls executeCommand() with shell set to True.

   :param command: The command to run.  The command will be executed throught the shell (normally bash).
   :type list or string:
   :param stream: Streams output to the cell as the command is executing.
   :type boolean:
   :return: A tuple containing the (return_code, stdout, stderr).  return_code is 0 when executing completed successfully. stdout and stderr are bytestrings.

    >>> runCommand('date')
    Wed Jul  5 10:59:54 EDT 2017
    (0, 'Wed Jul  5 10:59:54 EDT 2017\n', '')

    >>> runCommand('date', stream=False)
    (0, 'Wed Jul  5 11:00:00 EDT 2017\n', '')

    >>> runCommand('date --utc', stream=False)
    (0, 'Wed Jul  5 15:00:12 UTC 2017\n', '')


