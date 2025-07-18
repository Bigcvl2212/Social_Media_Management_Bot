"""
Sample Test Module for Social Media Management Bot

This module demonstrates how to structure and write tests for the bot.
Add your future tests here following this pattern.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main


class TestSocialMediaBot(unittest.TestCase):
    """
    Sample test class demonstrating test structure.
    
    This class shows how to organize tests for the Social Media Management Bot.
    Follow this pattern when adding new tests for your features.
    """

    def test_main_function_exists(self):
        """Test that the main function exists and is callable."""
        self.assertTrue(callable(main.main))

    def test_main_runs_without_error(self):
        """Test that the main function can be called without raising exceptions."""
        try:
            # Capture stdout to avoid cluttering test output
            import io
            import contextlib
            
            stdout_capture = io.StringIO()
            with contextlib.redirect_stdout(stdout_capture):
                main.main()
            
            # Check that some output was produced
            output = stdout_capture.getvalue()
            self.assertIn("Welcome", output)
            self.assertIn("Social Media Management Bot", output)
            
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")

    def test_welcome_message_content(self):
        """Test that the welcome message contains expected content."""
        import io
        import contextlib
        
        stdout_capture = io.StringIO()
        with contextlib.redirect_stdout(stdout_capture):
            main.main()
        
        output = stdout_capture.getvalue()
        
        # Check for key phrases in the welcome message
        self.assertIn("Welcome to the Social Media Management Bot", output)
        self.assertIn("Ready for expansion", output)


if __name__ == "__main__":
    unittest.main()