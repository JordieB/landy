import os
import subprocess
import time
import signal
import nose.tools as nt


def test_bot_runs():
    """
    Test whether the bot runs without erroring out.
    """
    try:
        # Get the absolute path of the directory containing the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct a file path relative to the script's directory
        fp = os.path.join(script_dir, '..', 'bot.py')
        # Run the bot in a subprocess
        p = subprocess.Popen(['python', fp])
        # Wait for 5 seconds before checking the process status
        time.sleep(5)
        # Send a KeyboardInterrupt signal to the subprocess to force it to close
        p.send_signal(signal.SIGINT)
        # Check if subprocess has completed successfully/does not return exit code 0
        nt.assert_equal(p.wait(), 0)
    except Exception as e:
        # If there was a Python exception, print it and fail the test
        print(e)
        nt.assert_false(True)
    finally:
        # Terminate the subprocess
        p.terminate()
