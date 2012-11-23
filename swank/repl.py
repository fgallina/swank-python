import logging
import sys

from code import InteractiveConsole


logger = logging.getLogger(__name__)


class REPL(InteractiveConsole):

    def __init__(self, locals=None, prompt=None, stdin=None, stderr=None):
        """Closely emulate the behavior of the interactive Python interpreter.

        This class builds on InteractiveConsole and ignores sys.ps1
        and sys.ps2 to use some slime friendly values.

        """
        InteractiveConsole.__init__(self, locals=locals, filename="<console>");
        self.prompt = prompt or "Python> "
        self.stdin = stdin or sys.stdin
        self.stderr = stderr or sys.stderr

    def interact(self, banner=None):
        old_ps1 = getattr(sys, 'ps1', '')
        old_ps2 = getattr(sys, 'ps2', '')
        sys.ps1 = self.prompt
        sys.ps2 = ""
        stdin, stdout, stderr = (sys.stdin, sys.stdout, sys.stderr)
        sys.stdin, sys.stdout, sys.stderr = (self.stdin, self.stderr, self.stderr)
        logger.debug(self.locals)
        InteractiveConsole.interact(self, banner=banner);
        sys.stdin, sys.stdout, sys.stderr = (stdin, stdout, stderr)
        sys.ps1 = old_ps1
        sys.ps2 = old_ps2

    def write(self, data):
        """Write a string.

        The base implementation writes to sys.stderr; a subclass may
        replace this with a different implementation.

        """
        self.stderr.write(data)


def repl(**kwargs):
    shell = REPL(**kwargs)
    shell.interact("REPL started")


if __name__ == '__main__':
    repl(prompt="Python> ")
