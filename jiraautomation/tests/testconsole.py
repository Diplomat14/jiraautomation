from unittest import TestCase
from jiraorm.console.command_line import main

class TestConsole(TestCase):
    def test_basic(self):
        main()