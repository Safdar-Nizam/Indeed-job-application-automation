import subprocess, sys, os
script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apply.py")
subprocess.Popen([sys.executable, script], cwd=os.path.dirname(script), creationflags=0x00000010)
