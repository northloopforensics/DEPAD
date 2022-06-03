#python3 script to walk directory and strip first or last bytes from each file under that directory
#It also adds 'AMENDED' to the front of the file name so you know what is new
#This does not look at file headers. It is not smart. 
#
#   Tool workflow
#  1. ID a target folder containing files that need bytes removed
#   |
#  2. Choose an output folder to store changed files
#   |
#  3. Select # of bytes to remove from start OR end of files
#   |
#   <OPTIONAL>
#   |
#  4. Preview window to see raw binary of a sample file


#   TO DO 
#   X   Functioning GUI 
#   X   Preview window to show user the expected outcome of their data on hex view of a sample file. Use color or strikethru?
#   X   Progress bar
#   X   Activity report - txt format include time/date, user settings, files processed. This will be text?
#       Should there be logic to check for known file signatures? Probably not unless this thing becomes a carver.
#   X   Fix automatic hex read to bypass folders


import os
import PySimpleGUI as sg
import itertools
import datetime
import hashlib
import tempfile

ASCII_character_start = 33       #ASCII characters to interpret 33 to 126
ASCII_character_end = 126        #in hex view

#********************* LAND OF FUNCTIONS ***********************

def auto_preview():                                 #this function walks the source directory and finds the 
                                                    #smallest file that is between 100 bytes and 100mb for binary preview
    size_dictionary = {}
    direct = values["SOURCE"]         
    all_files = os.listdir(direct)                  #list directory contents
    try:
        for file in all_files:
            if os.path.isfile(os.path.join(direct, file)) == True:   #just files, removes folders
                pathway = (direct + '/' + file)
                sized = os.path.getsize(pathway)            #gets file size
                if sized > 100:                             #minimum file size to 100 bytes
                    if sized < 100000000:                   #limits file size to 100mb
                        size_dictionary[file]=sized         #adds appropriate files to dictionary
                        
        smallest = min(size_dictionary, key=size_dictionary.get)       #reads the dictionary and gets smallest key for smallest file size 
        global Auto_preview_file
        Auto_preview_file = (direct + '/' + smallest)
        
        return(Auto_preview_file)
    except:
        window['-ML1-'+sg.WRITE_ONLY_KEY].print("Unable to load a file between 100 bytes and 100mb from the target directory. Manually select a file to preview.")
        print("Unable to load a file between 100 bytes and 100mb from the target directory. Manually select a file to preview.")        
    # else:
    #     window['-ML1-'+sg.WRITE_ONLY_KEY].print("Auto-preview not available. Select a file for preview.")  # Error msg
    

def hex_group_formatter(iterable):
    chunks = [iter(iterable)] * 8              #iter * 8byte groupings
    return '   '.join(
        ' '.join(format(x, '0>2x') for x in chunk)
        for chunk in itertools.zip_longest(*chunks, fillvalue=0))

def ascii_group_formatter(iterable):                        # formats the ascii interpreter
    return ''.join(
        chr(x) if ASCII_character_start <= x <= ASCII_character_end else '.'
        for x in iterable)

def hex_viewer(filename, chunk_size=16):                #This reads 16 bytes at a time and creates a formatted line of the Address - Hex Values - ASCII interpretation on each line

    header = hex_group_formatter(range(chunk_size))     #This approach may not be ideal. How the hell am I going to update hex value colors this way?!?  Will have more coffee and rethink.
    yield 'ADDRESS     {:<53}      ASCII'.format(header)
    yield ''
    template = '{:0>8x}    {:<53}{}'

    with open(filename, 'rb') as reduce:
        with tempfile.NamedTemporaryFile(mode="rb+") as stream:
            
            n = values["BYTE_COUNT"]
            n = int(n)
            reduced_file_size = n + 512
            if values["SMALLERHEX"] == True:
                if values["STARTOFFILE"] == True:
                    smaller = reduce.read()[n:reduced_file_size]
                if values["ENDOFFILE"] == True:
                    smaller = reduce.read()[-reduced_file_size:-n]
            else:
                if values["STARTOFFILE"] == True:
                    smaller = reduce.read()[n:]
                if values["ENDOFFILE"] == True:
                    smaller = reduce.read()[:-n]
            stream.write(smaller)
            stream.seek(0)
            for chunk_count in itertools.count(0):              #starts the hex address count at x00
                chunk = stream.read(chunk_size)                 # reads in 16 byte iterations
                if not chunk:
                    return
                yield template.format(
                    chunk_count * chunk_size,
                    hex_group_formatter(chunk),
                    ascii_group_formatter(chunk))



def Cut_What_Where():                                                       #    Function to remove selected binary values from file
    BYTES_TO_REMOVE_FROM_START = values["BYTE_COUNT"]                       #   Gui input for bytes to remove from start
    if BYTES_TO_REMOVE_FROM_START != "":                                    #   Checks that something is entered for bytes
        try:
            BYTES_TO_REMOVE_FROM_START = int(BYTES_TO_REMOVE_FROM_START)        #   Getting the Byte input for starting bytes and converting from str to integer
        except(ValueError):
            print("Error - Byte count must be a decimal numeric value")
    
    BYTES_TO_REMOVE_FROM_END = values["BYTE_COUNT"]                           #   Getting the GUI Byte input for ending bytes and converting from str to integer
    if BYTES_TO_REMOVE_FROM_END != "":                                      #   Checks that something is entered for bytes
        try:
            BYTES_TO_REMOVE_FROM_END = int(BYTES_TO_REMOVE_FROM_END)
        except(ValueError):
            print("ValueError - Byte count must be a decimal numeric value")
            
    input_directory = values['SOURCE']  
    output_directory = values['OUT']                                        
    byte_NUM_start = values["STARTOFFILE"]
    byte_NUM_end = values['ENDOFFILE']
    file_count = sum(len(files) for _, _, files in os.walk(input_directory))  #gets a recursive count of all files in input directory.  
                                                                              #The "_" in the sum function are just skipped variables for root and dir
    go_up = 0                        #   This value is a baseline, see below that it increments by +1 for each loop that happens below. Need this for 
                                     #   progress bar. 

    if isinstance(BYTES_TO_REMOVE_FROM_START, int) and byte_NUM_start == True:  # check - Did the user input an integer
        pass
    elif isinstance(BYTES_TO_REMOVE_FROM_END, int) and byte_NUM_end  == True:   # check - Did the user input an integer
        pass
    else:
        return sg.Popup("TypeError - Byte count must be a decimal numeric value")  #popup window showing error that interupts the process
    #   This starts the reporting process
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d %H-%M-%S')
    now = str(now)
    txt_report = (values['OUT'] + '/DEPAD_Activity_Report-' + now + '.txt')
    with open(txt_report, 'a') as report:
        report.write("DEPAD - Data Management Tool\n")
        report.write("Activity Report: " + now + '\n')
        if values['STARTOFFILE'] == True:
            report.write("User selected to remove " + values['BYTE_COUNT'] + ' bytes from the start of the listed files.\n\n')
        if values['ENDOFFILE'] == True:
            report.write("User selected to remove " + values['BYTE_COUNT'] + ' bytes from the end of the listed files.\n\n')
        report.write("\n")
        try:    
            for root, dirs, files in os.walk(input_directory):                      #walks directory, subdirectories, and files
                for file in files:                                                  #iterates to address each found file
                    go_up = go_up + 1
                    sg.OneLineProgressMeter('progress', go_up, file_count, orientation="H")     #   progress bar
                    filepath = os.path.join(root,file)                              #creates an absolute path for each found file
                    out_name = os.path.join(output_directory, "AMENDED_" + file)    #creates a new name for altered files
                    #print(file)
                    with open(filepath, 'rb') as get_hash:
                        in_data = get_hash.read()
                        in_hash = hashlib.md5(in_data).hexdigest()

                    with open(filepath, 'rb') as in_file:                           #reads binary data of original file
                    
                        with open(out_name, 'wb') as out_file:                      #makes a new output file
                            try:
                                if byte_NUM_start == True:
                                
                                    out_file.write(in_file.read()[BYTES_TO_REMOVE_FROM_START:])     #writes binary data less first N bytes from original file to new file
                                    
                                elif byte_NUM_end == True:
                                    #add get md5 of output
                                    out_file.write(in_file.read()[:-BYTES_TO_REMOVE_FROM_END])       #writes binary data less last N bytes from original file to new file
                                    
                            except(TypeError):
                                sg.Popup("TypeError - Byte count must be a decimal numeric value")  #popup window showing error
                        
                        with open(out_name, 'rb') as out_bin:                                       #   gets an output hash for the report
                            out_data = out_bin.read()
                            out_hash = hashlib.md5(out_data).hexdigest()
                            report.write('File:  ' + file)                                          #   adds data to the report file
                            report.write('  Original MD5:  ' + in_hash)
                            report.write('  Amended MD5:  ' + out_hash + '\n\n')
        except(FileNotFoundError):
            sg.Popup("Check that you selected a valid input and output folder")   #popup for error.  
            print('test')
        except(TypeError):
            sg.Popup("TypeError - Byte count must be a decimal numeric value")  #popup window showing error
            window.refresh()
        # print(file_count)   # for testing   
        sg.Popup("DEPAD process complete.")  #popup window showing completion
    
#***************************** GUI-VILLE *********************************************


sg.theme('lightgray6')  #GUI color scheme

preview_tab = [[sg.Button('Preview Byte Selection', key="PREVIEW"), sg.Text(" "*60)],               # Preview Tab Window
        [sg.Text('     '), sg.Radio('Automactically Select Preview File from Input Directory', font=('Arial', 12), group_id=3, default=True, key="AUTO")],
        [sg.Text('     '), sg.Radio("Manually Select Preview File", font=('Arial', 12), group_id=3, key="ChooseFile")],  
        [sg.Text('     '), sg.Text('Select a sample file to preview the results before execution:', font=('Arial', 12))],
        [sg.Text('     '), sg.Input(key='PREVIEWFILE',), sg.FileBrowse(key='PREVIEWFILE')],
        [sg.Text('     '), sg.Checkbox("", default=True, key="SMALLERHEX"), sg.Text('Limit Preview to 512 Bytes of Output', font=('Arial', 8))],
        [sg.MLine(key='-ML1-'+sg.WRITE_ONLY_KEY,font='courier',size=(82,14))]]      # Console window in GUI

Gouger_tab = [[sg.Text('')],                                                                        #Cutting Tab Window
        [sg.Text('        '), sg.Text('Select Input and Output Directory:', font=('Arial', 12))],
        [sg.Text('        '),sg.Input("INPUT FOLDER - Source Data", font=('Arial', 12), key='SOURCE',), sg.FolderBrowse(key='SOURCE'), sg.Text(' '*10)], 
        [sg.Text('')],
        [sg.Text('        '),sg.Input("OUTPUT FOLDER - Amended Data & Report", font=('Arial', 12), key='OUT',), sg.FolderBrowse(key='OUT')],
        [sg.Text('        '),sg.Text('')],
        [sg.Text('          Bytes to Remove (Dec)', font=('Arial', 12)), sg.Input(size=(21,2), default_text=0 ,key="BYTE_COUNT")],
        [sg.Text('        '), sg.Radio('From Start of Files', key="STARTOFFILE", font=('Arial', 12), default=True, group_id=1.), sg.Radio('From End of Files', enable_events=True ,key="ENDOFFILE", font=('Arial', 12), group_id=1)],
        #[sg.Text('_'*82)],      
        [sg.Text('')],
        [sg.Text('')],
        [sg.Text('        '),sg.Button('REMOVE PADDED DATA FROM SELECTED FILES', key='Ok')]]

layout = [[sg.Text('DEPAD   ', font=('Impact', 40, 'bold italic'))], 
        [sg.Text('A Tool to Remove Padded Data from the Start or End of Bulk Files.', font=('Arial', 12,'bold'))],                                # Main Window
        [sg.TabGroup([[sg.Tab('Removal', Gouger_tab, font=('Arial', 12)), sg.Tab("Previewing", preview_tab)]])]]
        

#******************** BRINGS GUI & FUNCTIONS TOGETHER ********************************


# Create the Window
window = sg.Window('North Loop Consulting', layout, no_titlebar=False, alpha_channel=1, grab_anywhere=False)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit': # if user closes window or clicks cancel
        break
    if event == 'Ok':
        try:
            Cut_What_Where()
        except FileNotFoundError:
            sg.Popup("You must select valid Input and Output folders.")
    if event == 'PREVIEW':
        start = values["BYTE_COUNT"]
        
        try:
            start = int(start)
            if values["AUTO"] == True:
                try:
                    auto_preview()      #function to find a file for binary preview
                except(FileNotFoundError):
                    window['-ML1-'+sg.WRITE_ONLY_KEY].print("*****  You must choose a source directory  *****\n")
                prefile = Auto_preview_file
                window['-ML1-'+sg.WRITE_ONLY_KEY].print("Preview file selected: " + prefile + " \n")
                window['-ML1-'+sg.WRITE_ONLY_KEY].print("*****  Preview of sample file with " + values["BYTE_COUNT"] + " bytes removed.  *****\n")
                for line in hex_viewer(prefile):
                    window['-ML1-'+sg.WRITE_ONLY_KEY].print(line)
                window['-ML1-'+sg.WRITE_ONLY_KEY].print(" ")           
            elif values["ChooseFile"] == True:  #Checkbox for manual preview file selection
                try:
                    prefile = values["PREVIEWFILE"]
                    if len(prefile) <= 5:           #checks length of file path to prevent empty entries
                        window['-ML1-'+sg.WRITE_ONLY_KEY].print("*****  You must select a preview file  *****\n")   # In-console error msg
                        
                    if len(prefile) > 5:            #checks length of file path to allow entries with actual path
                        window['-ML1-'+sg.WRITE_ONLY_KEY].print("Preview file selected: " + prefile + " \n")
                        window['-ML1-'+sg.WRITE_ONLY_KEY].print("*****  Preview of sample file with " + values["BYTE_COUNT"] + " bytes removed.  *****\n")
                        for line in hex_viewer(prefile):
                            window['-ML1-'+sg.WRITE_ONLY_KEY].print(line)
                            window.refresh()
                        window['-ML1-'+sg.WRITE_ONLY_KEY].print(" ")    
                except:
                    window['-ML1-'+sg.WRITE_ONLY_KEY].print("*****  You must select a preview file  *****\n")  # In-console error msg
        except ValueError:
            sg.Popup("Bytes to Remove value must be a positive integer.")
            window.refresh()
    window.refresh()
window.close()
