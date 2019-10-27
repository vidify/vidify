import sys
import subprocess


BSD = sys.platform.find('bsd') != -1
LINUX = sys.platform.startswith('linux')
MACOS = sys.platform.startswith('darwin')
WINDOWS = sys.platform.startswith('win')

# Using a single file?
ONEFILE = True
WINDOWS_SPEC = "windows_onefile.spec" if ONEFILE else "windows.spec"
LINUX_SPEC = "linux_onefile.spec" if ONEFILE else "linux.spec"


def main():
    print("Generating executable file with pyinstaller...")

    if WINDOWS:
        try:
            subprocess.run(["pyinstaller", WINDOWS_SPEC, "-y"])
        except PermissionError:
            print("ERROR: This script has to be run with admin privileges")
    elif LINUX or BSD:
        subprocess.run(["pyinstaller", LINUX_SPEC, "-y"])

if __name__ == '__main__':
    main()
