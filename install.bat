@echo off
set b=%cd%
sc create SchedFileCopyService binpath="%b%/schedfilecopy.exe" type=share start=auto displayname=SchedFileCopy