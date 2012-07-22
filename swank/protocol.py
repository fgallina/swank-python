import os
import platform
import sys
from lisp import read_lisp, write_lisp, symbol


class SwankProtocol(object):
    """Swank Protocol implementation for Python.

    The most important function here is the dispatch function that
    takes care of parsing lisp data to detect the correct method to
    call and its arguments. Once the appropiate method is called it
    also takes care of converting to python result to a lisp
    expression to be returned to the client.

    All other functions part of the Swank protocol wont do any Lisp
    conversion or parsing. All of them get what they need in python
    code and return Python results.

    The read_lisp and write_lisp take care of doing proper conversions
    for all datatypes.

    """

    def __init__(self, socket):
        self.globals = {}
        self.locals = {}
        self.package = None,
        self.thread = True,
        self.id = 0
        self.socket = socket

    def dispatch(self, data):
        """Parses an :emacs-rex command an returns lisp response."""
        command, form, package, thread, rid = read_lisp(data)
        self.package = package;
        self.thread = thread;
        self.id = rid;
        fn = form[0];
        args = form[1:]
        method_name = fn.replace(":", "_").replace("-", "_")
        method = getattr(self, method_name)
        response = method(*args)
        lisp_response = write_lisp(response)
        header = "{0:06x}".format(len(lisp_response))
        return header + lisp_response

    def swank_connection_info(self):
        """Return connection info available"""
        machine = platform.machine().upper()
        version = sys.version
        pid = os.getpid()
        host, ip_addr = self.socket.getsockname()
        return [
            symbol(":return"), {
                ":ok": {
                    ":pid": pid,
                    ":package": {
                        ":name": "python",
                        ":prompt": "PYTHON"
                    },
                    ":lisp-implementation": {
                        ":type": "PYTHON",
                        ":name": "python",
                        ":version": version
                    }
                }
            },
            self.id
        ]

    def swank_eval(self, string):
        """Eval string"""
        try:
            exec((compile(string, '<string>', 'exec')), self.globals)
            return [
                ":return",
                {":ok": string.splitlines()[0]},
                self.id
            ]
        except Exception as e:
            return [
                symbol(":debug"), 0, 1,
                [e, nil],
                [],
                [],
                self.id
            ]

    def swank_interactive_eval(self, string):
        return self.swank_eval(string)

    def swank_interactive_eval_region(self, string):
        return self.swank_eval(string)

    def swank_pprint_eval(self, string):
        return self.swank_eval(string)

    def swank_compile_file(self, name):
        pass

    def swank_compile_string(self, form):
        pass

    def swank_completions(self, symbol):
        pass

    def swank_create_repl(self):
        pass

    def swank_debug_thread(self, index):
        pass

    def swank_describe_function(self, fn):
        pass

    def swank_describe_symbol(self, symbol):
        pass

    def swank_disassemble(self, symbol):
        pass

    def swank_eval_in_frame(self, expr, index):
        pass

    def swank_frame_call(self, frame):
        pass

    def swank_frame_locals(self, frame):
        pass

    def swank_frame_source_loc(self, frame):
        pass

    def swank_fuzzy_completions(self, symbol):
        pass

    def swank_inspect(self, symbol):
        pass

    def swank_inspect_in_frame(self, symbol, index):
        pass

    def swank_inspect_nth_part(self, index):
        pass

    def swank_inspector_nth_action(self, index):
        pass

    def swank_inspector_pop(self):
        pass

    def swank_inspector_range(self):
        pass

    def swank_interrupt(self):
        pass

    def swank_invoke_abort(self):
        pass

    def swank_invoke_continue(self):
        pass

    def swank_invoke_restart(self, level, restart):
        pass

    def swank_kill_thread(self, index):
        pass

    def swank_list_threads(self):
        pass

    def swank_load_file(self, name):
        pass

    def swank_macroexpand(self, form):
        pass

    def swank_macroexpand_all(self, form):
        pass

    def swank_op_arglist(self, op):
        pass

    def swank_profile_report(self):
        pass

    def swank_profile_reset(self):
        pass

    def swank_profile_substring(self, string, package):
        pass

    def swank_profiled_functions(self):
        pass

    def swank_quit_inspector(self):
        pass

    def swank_require(self, contrib):
        pass

    def swank_return_string(self, string):
        pass

    def swank_set_break(self, symbol):
        pass

    def swank_set_package(self, pkg):
        pass

    def swank_throw_toplevel(self):
        pass

    def swank_toggle_profile(self, symbol):
        pass

    def swank_toggle_trace(self, symbol):
        pass

    def swank_undefine_function(self, fn):
        pass

    def swank_unprofile_all(self):
        pass

    def swank_untrace_all(self):
        pass

    def swank_xref(self, fn, type):
        pass
