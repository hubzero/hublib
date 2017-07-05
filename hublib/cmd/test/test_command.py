# -*- coding: utf-8 -*-

from __future__ import print_function
import pytest
import sys
import os
from subprocess import check_output
sys.path.insert(0, os.path.abspath('../../..'))
from hublib.cmd import runCommand, executeCommand


class TestRunCommand:

    def test_basic(self):
        host = check_output('hostname')
        code, out, err = runCommand('hostname', stream=False)
        assert code == 0
        assert host == out
        assert err == b''

    def test_stream(self, capsys):
        host = check_output('hostname')
        code, out, err = runCommand('hostname', stream=True)
        sout, serr = capsys.readouterr()
        assert host == out
        assert host == sout.encode('utf-8')

    def test_unicode_stream(self, capsys):
        actual = u"""ಬಾ ಇಲ್ಲಿ ಸಂಭವಿಸು ಇಂದೆನ್ನ ಹೃದಯದಲಿ
ನಿತ್ಯವೂ ಅವತರಿಪ ಸತ್ಯಾವತಾರ
ಮಣ್ಣಾಗಿ ಮರವಾಗಿ ಮಿಗವಾಗಿ ಕಗವಾಗೀ...
ಮಣ್ಣಾಗಿ ಮರವಾಗಿ ಮಿಗವಾಗಿ ಕಗವಾಗಿ
ಭವ ಭವದಿ ಭತಿಸಿಹೇ ಭವತಿ ದೂರ
ನಿತ್ಯವೂ ಅವತರಿಪ ಸತ್ಯಾವತಾರ || ಬಾ ಇಲ್ಲಿ ||"""

        code, out, err = runCommand('cat ಕನ್ನಡ.txt', stream=True)
        sout, serr = capsys.readouterr()
        out = out.decode('utf-8')
        assert out == actual
        assert actual == sout

    def test_unicode_no_stream(self, capsys):
        actual = u"""ಬಾ ಇಲ್ಲಿ ಸಂಭವಿಸು ಇಂದೆನ್ನ ಹೃದಯದಲಿ
ನಿತ್ಯವೂ ಅವತರಿಪ ಸತ್ಯಾವತಾರ
ಮಣ್ಣಾಗಿ ಮರವಾಗಿ ಮಿಗವಾಗಿ ಕಗವಾಗೀ...
ಮಣ್ಣಾಗಿ ಮರವಾಗಿ ಮಿಗವಾಗಿ ಕಗವಾಗಿ
ಭವ ಭವದಿ ಭತಿಸಿಹೇ ಭವತಿ ದೂರ
ನಿತ್ಯವೂ ಅವತರಿಪ ಸತ್ಯಾವತಾರ || ಬಾ ಇಲ್ಲಿ ||"""
        code, out, err = runCommand('cat ಕನ್ನಡ.txt', stream=False)
        sout, serr = capsys.readouterr()
        out = out.decode('utf-8')
        assert out == actual
        assert sout == ''

    def test_exe_not_exist(self):
        code, out, err = runCommand('does_not_exist')
        assert code != 0
        assert out == b''
        assert err.decode('utf-8').endswith('not found\n')

    def test_exe_not_exist2(self):
        code, out, err = executeCommand('does_not_exist')
        assert code != 0
        assert out == b''
        assert err.decode('utf-8').startswith('No such file or directory')

    def test_file_not_exist(self):
        code, out, err = runCommand('ls -l does_not_exist')
        assert code != 0
        assert out == b''
        assert err.decode('utf-8').endswith('No such file or directory\n')

    def test_unicode_command(self, capsys):
        actual = u"""ಬಾ ಇಲ್ಲಿ ಸಂಭವಿಸು ಇಂದೆನ್ನ ಹೃದಯದಲಿ
ನಿತ್ಯವೂ ಅವತರಿಪ ಸತ್ಯಾವತಾರ
ಮಣ್ಣಾಗಿ ಮರವಾಗಿ ಮಿಗವಾಗಿ ಕಗವಾಗೀ...
ಮಣ್ಣಾಗಿ ಮರವಾಗಿ ಮಿಗವಾಗಿ ಕಗವಾಗಿ
ಭವ ಭವದಿ ಭತಿಸಿಹೇ ಭವತಿ ದೂರ
ನಿತ್ಯವೂ ಅವತರಿಪ ಸತ್ಯಾವತಾರ || ಬಾ ಇಲ್ಲಿ ||

👍👍👍👍👍👍👍👍👍👍
"""
        code, out, err = executeCommand(u'./UnicodeTestλ.py',
                                        stdin='ಕನ್ನಡ.txt',
                                        streamOutput=True)
        sout, serr = capsys.readouterr()
        assert code == 0
        out = out.decode('utf-8')
        assert out == actual
        assert sout == actual

    def test_unicode_command_fh(self, capsys):
        actual = u"""ಬಾ ಇಲ್ಲಿ ಸಂಭವಿಸು ಇಂದೆನ್ನ ಹೃದಯದಲಿ
ನಿತ್ಯವೂ ಅವತರಿಪ ಸತ್ಯಾವತಾರ
ಮಣ್ಣಾಗಿ ಮರವಾಗಿ ಮಿಗವಾಗಿ ಕಗವಾಗೀ...
ಮಣ್ಣಾಗಿ ಮರವಾಗಿ ಮಿಗವಾಗಿ ಕಗವಾಗಿ
ಭವ ಭವದಿ ಭತಿಸಿಹೇ ಭವತಿ ದೂರ
ನಿತ್ಯವೂ ಅವತರಿಪ ಸತ್ಯಾವತಾರ || ಬಾ ಇಲ್ಲಿ ||

👍👍👍👍👍👍👍👍👍👍
"""
        fh = open('ಕನ್ನಡ.txt')
        code, out, err = executeCommand(u'./UnicodeTestλ.py',
                                        stdin=fh,
                                        streamOutput=True)
        sout, serr = capsys.readouterr()
        assert code == 0
        out = out.decode('utf-8')
        assert out == actual
        assert sout == actual

    def test_unicode_command_fd(self, capsys):
        actual = u"""ಬಾ ಇಲ್ಲಿ ಸಂಭವಿಸು ಇಂದೆನ್ನ ಹೃದಯದಲಿ
ನಿತ್ಯವೂ ಅವತರಿಪ ಸತ್ಯಾವತಾರ
ಮಣ್ಣಾಗಿ ಮರವಾಗಿ ಮಿಗವಾಗಿ ಕಗವಾಗೀ...
ಮಣ್ಣಾಗಿ ಮರವಾಗಿ ಮಿಗವಾಗಿ ಕಗವಾಗಿ
ಭವ ಭವದಿ ಭತಿಸಿಹೇ ಭವತಿ ದೂರ
ನಿತ್ಯವೂ ಅವತರಿಪ ಸತ್ಯಾವತಾರ || ಬಾ ಇಲ್ಲಿ ||

👍👍👍👍👍👍👍👍👍👍
"""
        fh = open('ಕನ್ನಡ.txt')
        code, out, err = executeCommand(u'./UnicodeTestλ.py',
                                        stdin=fh.fileno(),
                                        streamOutput=True)
        sout, serr = capsys.readouterr()
        assert code == 0
        out = out.decode('utf-8')
        assert out == actual
        assert sout == actual
