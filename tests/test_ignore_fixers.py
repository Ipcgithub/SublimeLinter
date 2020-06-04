import sublime

from unittesting import DeferrableTestCase
from SublimeLinter.tests.mockito import unstub, when
from SublimeLinter.tests.parameterized import parameterized as p


from SublimeLinter.highlight_view import add_eol, fix_flake8_eol


class TestIgnoreFixers(DeferrableTestCase):
    @classmethod
    def setUpClass(cls):
        # make sure we have a window to work with
        sublime.run_command("new_window")
        cls.window = sublime.active_window()
        s = sublime.load_settings("Preferences.sublime-settings")
        s.set("close_windows_when_empty", False)

    @classmethod
    def tearDownClass(cls):
        cls.window.run_command('close_window')

    def tearDown(self):
        unstub()

    def create_view(self, window):
        view = window.new_file()
        self.addCleanup(self.close_view, view)
        return view

    def close_view(self, view):
        view.set_scratch(True)
        view.close()

    @p.expand([
        (
            "clean line",
            "view = window.new_file()",
            "view = window.new_file()  # noqa: E203"
        ),
        (
            "extend one given",
            "view = window.new_file()  # noqa: F402",
            "view = window.new_file()  # noqa: F402, E203",
        ),
        (
            "extend two given",
            "view = window.new_file()  # noqa: F402, E111",
            "view = window.new_file()  # noqa: F402, E111, E203",
        ),
        (
            "normalize joiner",
            "view = window.new_file()  # noqa: F402,E111,E203",
            "view = window.new_file()  # noqa: F402, E111, E203",
        ),
        (
            "handle surrounding whitespace",
            "    view = window.new_file()  ",
            "    view = window.new_file()  # noqa: E203",
        ),
        (
            "keep existing comment",
            "view = window.new_file()  # comment ",
            "view = window.new_file()  # comment  # noqa: E203",
        ),
        (
            "keep existing comment with only one space preceding",
            "view = window.new_file() # comment",
            "view = window.new_file() # comment  # noqa: E203",
        ),
        (
            "keep existing comment while extending",
            "view = window.new_file()  # comment  # noqa: F403",
            "view = window.new_file()  # comment  # noqa: F403, E203",
        ),
        (
            "keep python comment position while extending",
            "view = window.new_file()  # noqa: F403  # comment",
            "view = window.new_file()  # noqa: F403, E203  # comment",
        ),
        (
            "keep informal comment position while extending",
            "view = window.new_file()  # noqa: F403, comment",
            "view = window.new_file()  # noqa: F403, E203, comment",
        ),
    ])
    def test_flake8(self, _description, BEFORE, AFTER):
        view = self.create_view(self.window)
        view.run_command("insert", {"characters": BEFORE})
        fix_flake8_eol("E203", 4, view)
        view_content = view.substr(sublime.Region(0, view.size()))
        self.assertEquals(AFTER, view_content)
