@ECHO OFF
ECHO Copying module...
IF EXIST .\vidify\ (
rmdir /s /q .\vidify\
) ELSE (
mkdir .\vidify\
)
xcopy /s /q ..\vidify .\vidify\

ECHO Running PyInstaller...
pyinstaller windows.spec --noconfirm

ECHO Applying patches...
Rem The version may change depending on tekore
mkdir .\dist\vidify\tekore
ECHO "1.1.0" > .\dist\vidify\tekore\VERSION
