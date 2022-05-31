# DEPAD
DEPAD is a tool intended to help investigators dealing with large data productions containing superfluous or padded data that prevents a review of 
files.

This project started after a law enforcemnt agency received a legal production containing several thousand files related to a child exploitation investigation.  Each produced file had around 150 bytes of data tacked onto the start of its data.  This superfluous data prevented the investigator from being able to open any of the files using normal tools.  

The immediate solution was to create a small script to solve the problem, but DEPAD is a continuation of this solution which now includes a GUI interface and a file preview option within the tool to help determine what bytes need to be removed. 


How it works:

1.  Working with a copy, select the directory containing padded files. 
2.  Select an output.
3.  Define the number of bytes to be removed from the start or end of the file data.
4.  DEPAD will then write file copies from the input/source directory to the output directory less the bytes defined by the user.
5.  These copies will have their file name altered to include "AMENDED_" so the user can easily tell the difference from original files.
6.  DEPAD also creates a text report showing the files copied, their original MD5 hash value, and the MD5 of the amended file. 

![DEPADPREVIEW](https://user-images.githubusercontent.com/73806121/171286358-3d1aac1c-5d44-4bde-8c7b-64cf165000b0.png)
