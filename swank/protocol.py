# -*- coding: utf-8 -*-
import logging
import os.path
import platform

import logconfig
from lisp import cons, lbool, llist, lstring, read_lisp, symbol, write_lisp


__all__ = ['SwankProtocol']


logconfig.configure()
logger = logging.getLogger(__name__)


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

    def __init__(self, socket, locals=None, prompt="Python> "):
        self.locals = locals or {}
        self.package = None
        self.thread = True
        self.id = 0
        self.socket = socket
        self.prompt = prompt

    def dispatch(self, data):
        """Parses an :emacs-rex command an returns lisp response."""
        command, form, package, thread, rid = read_lisp(data)
        self.package = package;
        self.thread = thread;
        self.id = rid;
        fn = form[0];
        args = form[1:]
        method_name = fn.replace(":", "_").replace("-", "_")
        logger.debug(method_name)
        logger.debug(args)
        for i, arg in enumerate(args):
            if hasattr(arg, 'unquote'):
                args[i] = arg.unquote()
        try:
            response = [
                symbol(":return"),
                {":ok": getattr(self, method_name)(*args)},
                self.id
            ]
        except Exception as e:
            return [
                symbol(":debug"), 0, 1,
                [e, False],
                [],
                [],
                self.id
            ]
        lisp_response = write_lisp(response)
        header = "{0:06x}".format(len(lisp_response))
        return header + lisp_response

    def indentation_update(self):
        response = [symbol(":indentation-update"), [
            cons("def", 1),
            cons("class", 1),
            cons("if", 1),
            cons("else", 1),
            cons("while", 1),
            cons("for", 1),
            cons("try", 1),
            cons("except", 1),
            cons("finally", 1)
        ]]
        lisp_response = write_lisp(response)
        header = "{0:06x}".format(len(lisp_response))
        return header + lisp_response

    def swank_connection_info(self):
        """Return connection info available"""
        machine = platform.machine().upper()
        version = platform.python_version()
        pid = os.getpid()
        host, ipaddr = self.socket.getsockname()
        return llist([
            symbol(':return'), llist([
                symbol(':ok'), llist([
                    symbol(':pid'), pid, symbol(':style'), lbool(False),
                    symbol(':encoding'), llist([
                        symbol(':coding-systems'), llist([
                            lstring('utf-8-unix'),
                            lstring('iso-latin-1-unix')
                        ])
                    ]),
                    symbol(':lisp-implementation'), llist([
                        symbol(':type'), lstring('PYTHON'),
                        symbol(':name'), lstring('python'),
                        symbol(':version'), lstring(version),
                        symbol(':program'), lbool(False),
                    ]),
                    symbol(':machine'), llist([
                        symbol(':instance'), lstring("{0} [{1}]".format(host,ipaddr)),
                        symbol(':type'), lstring(machine),
                        symbol(':version'), lstring(machine)
                    ]),
                    symbol(':package'), llist([
                        symbol(':name'), lstring('python'),
                        symbol(':prompt'), self.prompt
                    ]),
                    symbol(':version'), lstring('2012-07-13')
                ])
            ]), self.id
        ])

    def swank_buffer_first_change(self, filename):
        return lbool(False)

    def swank_eval(self, string):
        """Eval string"""
        exec((compile(string, '<string>', 'exec')), self.locals)
        return "Evaled region"

    def swank_interactive_eval(self, string):
        return self.swank_eval(string)

    def swank_interactive_eval_region(self, string):
        return self.swank_eval(string)

    def swank_pprint_eval(self, string):
        return self.swank_eval(string)

    def swank_simple_completions(self, string, trash):
        try:
            import readline
        except ImportError:
            return [[], string]
        else:
            import rlcompleter
            readline.set_completer(rlcompleter.Completer().complete)
            completions = []
            try:
                i = 0
                while True:
                    res = readline.get_completer()(string, i)
                    if not res: break
                    i += 1
                    completions.append(res)
            except NameError:
                pass
            newinput = os.path.commonprefix(completions)
            return [[completions], newinput]

    def swank_apropos_list_for_emacs(self):
        pass

    def swank_backtrace(self):
        pass

    def swank_commit_edited_value(self):
        pass

    def swank_compile_file_for_emacs(self):
        pass

    def swank_compile_multiple_strings_for_emacs(self):
        pass

    def swank_compile_string_for_emacs(self):
        pass

    def swank_create_server(self):
        pass

    def swank_debug_nth_thread(self):
        pass

    def swank_debugger_info_for_emacs(self):
        pass

    def swank_default_directory(self):
        pass

    def swank_describe_definition_for_emacs(self):
        pass

    def swank_describe_function(self):
        pass

    def swank_describe_symbol(self):
        pass

    def swank_disassemble_form(self):
        pass

    def swank_documentation_symbol(self):
        pass

    def swank_eval_and_grab_output(self):
        pass

    def swank_eval_string_in_frame(self):
        pass

    def swank_find_definitions_for_emacs(self):
        pass

    def swank_flow_control_test(self):
        pass

    def swank_frame_locals_and_catch_tags(self):
        pass

    def swank_frame_package_name(self):
        pass

    def swank_frame_source_location(self):
        pass

    def swank_init_inspector(self):
        pass

    def swank_inspect_current_condition(self):
        pass

    def swank_inspect_frame_var(self):
        pass

    def swank_inspect_in_frame(self):
        pass

    def swank_inspect_nth_part(self):
        pass

    def swank_inspector_eval(self):
        pass

    def swank_inspector_history(self):
        pass

    def swank_inspector_pop(self):
        pass

    def swank_inspector_range(self):
        pass

    def swank_inspector_reinspect(self):
        pass

    def swank_kill_nth_thread(self):
        pass

    def swank_list_all_package_names(self):
        pass

    def swank_load_file(self):
        pass

    def swank_pprint_eval(self):
        pass

    def swank_pprint_eval_string_in_frame(self):
        pass

    def swank_pprint_inspector_part(self):
        pass

    def swank_profile_by_substring(self):
        pass

    def swank_profile_package(self):
        pass

    def swank_profile_reset(self):
        pass

    def swank_quit_inspector(self):
        pass

    def swank_quit_thread_browser(self):
        pass

    def swank_re_evaluate_defvar(self):
        pass

    def swank_restart_frame(self):
        pass

    def swank_set_default_directory(self):
        pass

    def swank_sldb_abort(self):
        pass

    def swank_sldb_break(self):
        pass

    def swank_sldb_break_on_return(self):
        pass

    def swank_sldb_break_with_default_debugger(self):
        pass

    def swank_sldb_disassemble(self):
        pass

    def swank_sldb_next(self):
        pass

    def swank_sldb_out(self):
        pass

    def swank_sldb_return_from_frame(self):
        pass

    def swank_sldb_step(self):
        pass

    def swank_start_server(self):
        pass

    def swank_swank_compiler_macroexpand(self):
        pass

    def swank_swank_expand(self):
        pass

    def swank_swank_format_string_expand(self):
        pass

    def swank_swank_macroexpand(self):
        pass

    def swank_swank_macroexpand_all(self):
        pass

    def swank_throw_to_toplevel(self):
        pass

    def swank_toggle_break_on_signals(self):
        pass

    def swank_toggle_debug_on_swank_error(self):
        pass

    def swank_undefine_function(self):
        pass

    def swank_unintern_symbol(self):
        pass

    def swank_unprofile_all(self):
        pass

    def swank_untrace_all(self):
        pass

    def swank_update_indentation_information(self):
        pass

    def swank_value_for_editing(self):
        pass

    def swank_xref(self):
        pass

    def swank_xrefs(self):
        pass
