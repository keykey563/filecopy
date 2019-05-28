@echo off
set src_path=%~dp0
set pyinstaller="D:\\PyInstaller-3.4\\pyinstaller.py"
call python %pyinstaller% -F "%src_path%\schedfilecopy.py"

pause;w
