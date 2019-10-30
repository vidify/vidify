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
if WINDOWS:
    SPEC = WINDOWS_SPEC
elif LINUX or BSD:
    SPEC = LINUX_SPEC


def main():
    print("Generating executable file with pyinstaller...")

    subprocess.run(["pyinstaller", SPEC, "-y"])


if __name__ == '__main__':
    main()
