from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
from tkinter.ttk import Combobox
import pyttsx3
import easyocr
import threading
from tkinter.ttk import Progressbar
from tkinter import Toplevel
import time

# Convert windows path into usable format
def convert_path(path):
    path = path.replace(r"C:\\", "/")
    path = path.replace("\\", "/")
    return path

# Convert image into text using OCR
def ImagetoText(path):
    global imageto_text_done  # Declare the flag as global
    reader = easyocr.Reader(['en'])  # Initialize the OCR tool
    result = reader.readtext(convert_path(path))  # Read the text from the image

    textfull = ''

    line_length = 0
    for (bbox, text, prob) in result:
        words = text.split()
        line_length = 0
        for word in words:
            if line_length + len(word) + 1 > 100:  # Add 1 for the space character
                textfull += '\n'
                line_length = 0
            textfull += word + ' '
            line_length += len(word) + 1

    entry.delete(1.0, END)  # Clear the text box
    entry.insert('1.0', textfull)  # Insert the recognized text into the text box
    imageto_text_done = True  # Set the flag to indicate that the OCR is done

    progress.stop()  # Stop the progress bar
    progress_window.destroy()  # Close the progress bar window

# Initial directory for the file dialog
askopenfiledirectory = r'C:\Users\DELL\Pictures'

# Global variable for the image
global my_image

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Main window
window = Tk()
window.title('Screenshot To Text/Audio')
window.geometry('1100x730')
window.configure(background='#968d8e')
window.resizable(False, False)

# To open the window at the middle of the screen
# Get screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Calculate position for window to be at the center
x_coordinate = int((screen_width/2) - (1100/2))
y_coordinate = int((screen_height/2) - (830/2))

# Set the position of the window to the center of the screen
window.geometry(f'{1100}x{730}+{x_coordinate}+{y_coordinate}')

# Frame for image preview
frame_picture = Frame(master=window, relief=SUNKEN, borderwidth=5, width=500, height=532)
frame_picture.place(x=30, y=60)
Label(master=frame_picture, text='---------Image Preview-----------', font='Helvatica 24', fg='black').place(x=25, y=230)

# Open Button
my_image_label = None

def open():
    global my_image, window_filename, my_image_label

    # Destroy the existing label widget if it exists
    if my_image_label is not None:
        my_image_label.destroy()

    window_filename = filedialog.askopenfilename(initialdir=convert_path(askopenfiledirectory), title='Select A Image',
                                                 filetypes=(("png files", "*.png"), ("jpg files", "*.jpg"), ('all files', '*.*')))
    my_img = Image.open(convert_path(window_filename))
    resized = my_img.resize((500, 532))
    my_image = ImageTk.PhotoImage(resized)
    my_image_label = Label(master=frame_picture, image=my_image)
    my_image_label.pack()

# Play Button with threading
def play():
    global engine
    engine = pyttsx3.init()
    threading.Thread(target=speak_text).start()

# Speak text (which run through the play function)
def speak_text():
    engine = pyttsx3.init()  # Initialize the engine here
    text = entry.get(1.0, END)
    speed = speedCombobox.get()
    gender = genderCombobox.get()
    voices = engine.getProperty('voices')

    # Map speed values to rate values
    speed_to_rate = {'x1': 200, 'x1.25': 250, 'x2': 400}

    # Get the rate for the selected speed
    rate = speed_to_rate.get(speed, 200)  # Default to 200 if speed is not in the dictionary

    # Set the voice based on the selected gender
    if gender == 'Male':
        engine.setProperty('voice', voices[0].id)
    else:
        engine.setProperty('voice', voices[1].id)

    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

# Copy to clipboard button
def copy():
    textCopy = entry.get(1.0, END)
    window.clipboard_clear()
    window.clipboard_append(textCopy)

imageto_text_done = False

# Progress bar
def start_progress_bar():
    direction = 1
    value = 0
    while not imageto_text_done:  # Check the flag in the loop condition
        # Update the progress bar
        progress['value'] = value

        # Reverse direction if the progress bar is at the ends
        if value >= 100:
            direction = -1
        elif value <= 0:
            direction = 1

        value += direction * 10     # Update the value for the next iteration

        progress_window.update()    # Update the window to redraw the progress bar

        time.sleep(0.1)             # Sleep for a bit to control the speed of the progress bar


# Submit Button
def submit():
    global progress, progress_window, imageto_text_done
    imageto_text_done = False
    # Create a new window for the progress bar
    progress_window = Toplevel(window)
    progress_window.title('Processing...')
    progress_window.geometry('250x85')

    # Remove the window decorations
    progress_window.overrideredirect(True)

    # Change the background color to black
    progress_window.configure(bg='#282C34')

    # Calculate the position to center the new window
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    window_x = window.winfo_x()
    window_y = window.winfo_y()

    progress_window_x = window_x + window_width//2 - 200//2
    progress_window_y = window_y + window_height//2 - 50//2

    progress_window.geometry(f"+{progress_window_x}+{progress_window_y}")

    # Create the progress bar
    progress = Progressbar(progress_window, length=200, mode='determinate')
    progress.place(relx=0.5, rely=0.7, anchor='center')

    label = Label(progress_window, text="Converting into Text", font=('Helvatica 12'), fg='#FFFFFF', bg='#282C34')
    label.place(x=5, y=5)

    # Start the progress bar in a separate thread
    threading.Thread(target=start_progress_bar).start()

    # Run ImagetoText in a separate thread
    threading.Thread(target=ImagetoText, args=(convert_path(window_filename),)).start()

# Function to save the text to an MP3 file
def SavetoMP3():
    # Open a file dialog to select the save location and file name
    MP3File = filedialog.asksaveasfilename(defaultextension=".wav", initialdir=convert_path(askopenfiledirectory), title="Save File",
                                           filetypes=(("WAV Files", "*.wav"), ("All Files", "*.*")))

    text = entry.get(1.0, END)
    speed = speedCombobox.get()
    gender = genderCombobox.get()
    voices = engine.getProperty('voices')

    # Map speed values to rate values
    speed_to_rate = {'x1': 200, 'x1.25': 250, 'x2': 400}

    # Get the rate for the selected speed
    rate = speed_to_rate.get(speed, 200)  # Default to 200 if speed is not in the dictionary

    # Set the voice based on the selected gender
    if MP3File is not None:
        if gender == 'Male':
            engine.setProperty('voice', voices[0].id)
        else:
            engine.setProperty('voice', voices[1].id)

        engine.setProperty('rate', rate)
        engine.save_to_file(text, MP3File)
        engine.runAndWait()

# Save as Button
def SaveAs():
    # Open a file dialog to select the save location and file name
    textfile = filedialog.asksaveasfile(defaultextension=".*", initialdir=convert_path(askopenfiledirectory), title="Save File",
                                        filetypes=(("Text Files", ".txt"), ("HTML Files", ".html"), ("Python File", ".py"), ("All Files", ".*")))

    if textfile is not None:
        text_to_save = entry.get(1.0, END)
        textfile.write(text_to_save)
        textfile.close()


#Button definitions
openButton = Button(window, text='Open file', relief=RAISED, font=('Helvetica 12 bold italic'), command=open).place(x=30, y=10)
submitButton = Button(window, text='Submit', relief=RAISED, font=('Helvetica 12 bold italic'), command=submit).place(x=150, y=10)
copyButton = Button(window, text='Copy to Clipboard', relief=RAISED, font=('Helvetica 12 bold italic'), command=copy).place(x=750, y=610)
saveasButton = Button(window, text='Save As', relief=RAISED, font=('Helvetica 16 bold italic'), command=SaveAs).place(x=30, y=657)


#PLay Button
playimage = Image.open(convert_path(r'C:\Users\DELL\PycharmProjects\pythonProject1\Images\PLay.png'))
playimage = playimage.resize((30, 30), Image.LANCZOS)  # Resize the image
playimageicon = ImageTk.PhotoImage(playimage)
playButton = Button(window, text='Play', compound=LEFT, image=playimageicon, fg='blue', relief=RAISED, command=play,
                    font=('Helvetica 16 bold italic'), height=30, width=80)
playButton.place(x=610, y=657)


#SaveAudioButton
image = Image.open(convert_path(r'C:\Users\DELL\PycharmProjects\pythonProject1\Images\audio.png'))
image = image.resize((30, 30), Image.LANCZOS)
mp3imageicon = ImageTk.PhotoImage(image)
saveMP3Button = Button(window, text='Save as Audio', compound=LEFT, image=mp3imageicon, relief=RAISED,
                       font=('Helvetica 16 bold italic'), command=SavetoMP3).place(x=200, y=657)


#Speed Combobox definitions
speedCombobox = Combobox(window, values=['x1', '1.25', 'x1.5', 'x2'], font='Helvatica 16', state='r', width=5)
speedCombobox.place(x=760, y=663)
speedCombobox.set('x1')


#Gender Combobox definitions
genderCombobox = Combobox(window, values=['Male', 'Female'], font='Helvatica 16', state='r', width=7)
genderCombobox.place(x=920, y=663)
genderCombobox.set('Male')


#Entry Definitions
entry = Text(window, height=33, width=60, wrap=WORD)
entry.place(x=580, y=60)

window.mainloop()

