import os
import sys
import unittest


try:
    from swank.lisp import *
except ImportError:
    root = os.path.realpath(os.path.dirname(__file__))
    modpath = os.path.join(root, "..")
    sys.path.insert(0, modpath)
    from swank.lisp import *


class ReaderWritterTests(unittest.TestCase):

    # def __init__(self, *args, **kwargs):
    #     super(ReaderWritterTests, self).__init__(*args, **kwargs)
    #     self.maxDiff = None

    def _test(self, code, expected):
        parsed = read_lisp(code)
        self.assertEqual(str(parsed), str(expected))
        self.assertEqual(str(parsed), write_lisp(expected))

    def test_read_write(self):

        code = """
        (:emacs-rex
          (swank:connection-info
            "a string \\" yo"
            1.2 2 'thasym
            '(1 2 3 4))
          nil t 1)"""
        expected = llist([
            symbol(':emacs-rex'),
            llist([
                symbol('swank:connection-info'),
                lstring('a string \\" yo'),
                1.2,
                2,
                symbol("'thasym"),
                quoted(
                    llist([
                        1, 2, 3, 4
                    ])
                )
            ]),
            lbool(False), lbool(True), 1
        ])
        self._test(code, expected)

        code = """'(:emacs-rex (swank:connection-info '(1 . 2)))"""
        expected = quoted(llist([
            symbol(':emacs-rex'),
            llist([
                symbol('swank:connection-info'),
                cons(1, 2)
            ])
        ]))
        self._test(code, expected)

        code = """
        (:emacs-rex
          (swank:connection-info
            "a string \\" yo"  ;;; comment #1
            1.2 2 'thasym
            '(1 2 3 4))
          nil t 1) ;;; comment # 2"""
        expected = llist([
            symbol(':emacs-rex'),
            llist([
                symbol('swank:connection-info'),
                lstring('a string \\" yo'),
                1.2,
                2,
                symbol("'thasym"),
                quoted(
                    llist([
                        1, 2, 3, 4
                    ])
                )
            ]),
            lbool(False), lbool(True), 1
        ])
        self._test(code, expected)

        code = """
        (:return
          (:ok
            (:pid 23082 :style nil
             :encoding
               (:coding-systems
                ("utf-8-unix" "iso-latin-1-unix"))
             :lisp-implementation
               (:type "CLISP"
                :name "clisp"
                :version "2.49 (2010-07-07) (built on archlinux.lan [192.168.1.1])"
                :program nil)
             :machine
               (:instance "localhost.localdomain [127.0.0.1]"
                :type "X86_64"
                :version "X86_64")
             :features
               (:swank :readline :regexp :syscalls :i18n :loop :compiler
                :clos :mop :clisp :ansi-cl :common-lisp :lisp=cl :interpreter
                :sockets :generic-streams :logical-pathnames :screen :ffi
                :gettext)
             :modules
               ("readline" "regexp" "syscalls" "i18n")
             :package
               (:name "COMMON-LISP-USER" :prompt "CL-USER")
             :version "2012-07-13")) 1)"""
        expected = llist([
            symbol(':return'), llist([
                symbol(':ok'), llist([
                    symbol(':pid'), 23082, symbol(':style'), lbool(False),
                    symbol(':encoding'), llist([
                        symbol(':coding-systems'), llist([
                            lstring('utf-8-unix'),
                            lstring('iso-latin-1-unix')
                        ])
                    ]),
                    symbol(':lisp-implementation'), llist([
                        symbol(':type'), lstring('CLISP'),
                        symbol(':name'), lstring('clisp'),
                        symbol(':version'), lstring('2.49 (2010-07-07) (built on archlinux.lan [192.168.1.1])'),
                        symbol(':program'), lbool(False),
                    ]),
                    symbol(':machine'), llist([
                        symbol(':instance'), lstring('localhost.localdomain [127.0.0.1]'),
                        symbol(':type'), lstring('X86_64'),
                        symbol(':version'), lstring('X86_64')
                    ]),
                    symbol(':features'), llist([
                        symbol(':swank'), symbol(':readline'),
                        symbol(':regexp'), symbol(':syscalls'),
                        symbol(':i18n'), symbol(':loop'),
                        symbol(':compiler'), symbol(':clos'),
                        symbol(':mop'), symbol(':clisp'),
                        symbol(':ansi-cl'), symbol(':common-lisp'),
                        symbol(':lisp=cl'), symbol(':interpreter'),
                        symbol(':sockets'), symbol(':generic-streams'),
                        symbol(':logical-pathnames'), symbol(':screen'),
                        symbol(':ffi'), symbol(':gettext')
                    ]),
                    symbol(':modules'), llist([
                        lstring('readline'), lstring('regexp'),
                        lstring('syscalls'), lstring('i18n')
                    ]),
                    symbol(':package'), llist([
                        symbol(':name'), lstring('COMMON-LISP-USER'),
                        symbol(':prompt'), lstring('CL-USER')
                    ]),
                    symbol(':version'), lstring('2012-07-13')
                ])
            ]), 1
        ])
        self._test(code, expected)



def main():
    unittest.main()


if __name__ == '__main__':
    main()
