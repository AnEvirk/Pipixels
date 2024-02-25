@echo off
rem 
set sz="C:\Program Files\7-Zip\7z.exe"
%sz% a pixel_archive.tar anims\
%sz% a pixel_archive.tar __main__.py
%sz% a pixel_archive.tar pixel.py
%sz% a pixel_archive.tar __init__.py
pscp -pw raspberry H:\0python\pipixels\pixel_archive.tar pi@192.168.0.101:/home/pi/pipixels/pixel_archive.tar
pause
exit /b
rem pscp -pw ubuntu C:\Users\gyxep\Downloads\openvswitch-2.11.1.tar.gz ubuntu@192.168.0.100:/home/ubuntu/downloads/openvswitch-2.11.1.tar.gz
