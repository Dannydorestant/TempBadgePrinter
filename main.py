import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import time
import argparse
import glob

import win32print
from reportlab.pdfgen import canvas
import os
import win32api


class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.ok = False

        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas_pic = tk.Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas_pic.grid(row=0, column=0)

        # Employee Info Canvas
        self.canvas_employee = tk.Canvas(window)
        self.canvas_employee.grid(row=0, column=1)

        # Employee Info Labels
        self.name = tk.Label(self.canvas_employee, text="Name:")
        self.name.grid(row=0, column=0)

        self.dept = tk.Label(self.canvas_employee, text="Department:")
        self.dept.grid(row=1, column=0)

        self.issue_date = tk.Label(self.canvas_employee, text="Issue Date:")
        self.issue_date.grid(row=2, column=0)

        self.exp_date = tk.Label(self.canvas_employee, text="Expiration Date:")
        self.exp_date.grid(row=3, column=0)

        # Employee Info Entires
        self.name_entry = tk.Entry(self.canvas_employee)
        self.name_entry.grid(row=0, column=1)

        self.dept_entry = tk.Entry(self.canvas_employee)
        self.dept_entry.grid(row=1, column=1)

        self.issue_date_entry = tk.Entry(self.canvas_employee)
        self.issue_date_entry.grid(row=2, column=1)

        self.exp_date_entry = tk.Entry(self.canvas_employee)
        self.exp_date_entry.grid(row=3, column=1)

        # Buttons
        self.btn_snapshot = tk.Button(self.canvas_employee, text="Snapshot", command=self.snapshot)
        self.btn_snapshot.grid(row=10, column=0)

        self.btn_print_badge = tk.Button(self.canvas_employee, text="Print Badge", command=self.get_input)
        self.btn_print_badge.grid(row=11, column=0)

        self.btn_quit = tk.Button(self.canvas_employee, text='QUIT', command=quit)
        self.btn_quit.grid(row=12, column=0)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 10
        self.update()

        self.window.mainloop()

    def get_input(self):
        name = self.name_entry.get()
        dept = self.dept_entry.get()
        issue_date = self.issue_date_entry.get()
        exp_date = self.exp_date_entry.get()

        list_of_files = glob.glob('*.jpg')  # * means all if need specific format then *.csv
        latest_pic= max(list_of_files, key=os.path.getctime)

        self.generate_pdf()
        #os.startfile(f"{name}.pdf", "print")

        GHOSTSCRIPT_PATH = "C:/Program Files (x86)gs/gs9.09/bin/gswin32.exe"
        GSPRINT_PATH = "C:/Users/admindan/PycharmProjects/TempBadgePrinter/GSPRINT/gsprint.exe"

        # YOU CAN PUT HERE THE NAME OF YOUR SPECIFIC PRINTER INSTEAD OF DEFAULT
        currentprinter = win32print.GetDefaultPrinter()

        win32api.ShellExecute(0, 'open', GSPRINT_PATH,
                              '-ghostscript "' + GHOSTSCRIPT_PATH + '" -printer "' + currentprinter + f'" "{name}.pdf"',
                              '.', 0)



    def generate_pdf(self,name='Test',dept='',issue_date='',exp_date='',latest_pic=''):
        my_canvas = canvas.Canvas(f"{name}.pdf", pagesize=(288,144))
        my_canvas.drawString(200, 72, "Welcome to Reportlab!")
        my_canvas.save()




    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def open_camera(self):
        self.ok = True
        self.timer.start()
        print("camera opened => Recording")

    def close_camera(self):
        self.ok = False
        self.timer.stop()
        print("camera closed => Not Recording")

    def update(self):

        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        if self.ok:
            self.vid.out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas_pic.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(self.delay, self.update)


class VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Command Line Parser
        args = CommandLineParser().args

        # create videowriter

        # 1. Video Type
        VIDEO_TYPE = {
            'avi': cv2.VideoWriter_fourcc(*'XVID'),
            # 'mp4': cv2.VideoWriter_fourcc(*'H264'),
            'mp4': cv2.VideoWriter_fourcc(*'XVID'),
        }

        self.fourcc = VIDEO_TYPE[args.type[0]]

        # 2. Video Dimension
        STD_DIMENSIONS = {
            '480p': (640, 480),
            '720p': (1280, 720),
            '1080p': (1920, 1080),
            '4k': (3840, 2160),
        }
        res = STD_DIMENSIONS[args.res[0]]
        print(args.name, self.fourcc, res)
        self.out = cv2.VideoWriter(args.name[0] + '.' + args.type[0], self.fourcc, 10, res)

        # set video sourec width and height
        self.vid.set(3, res[0])
        self.vid.set(4, res[1])

        # Get video source width and height
        self.width, self.height = res

    # To get frames
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            self.out.release()
            cv2.destroyAllWindows()


class CommandLineParser:

    def __init__(self):
        # Create object of the Argument Parser
        parser = argparse.ArgumentParser(description='Script to record videos')

        # Create a group for requirement
        # for now no required arguments
        # required_arguments=parser.add_argument_group('Required command line arguments')

        # Only values is supporting for the tag --type. So nargs will be '1' to get
        parser.add_argument('--type', nargs=1, default=['avi'], type=str,
                            help='Type of the video output: for now we have only AVI & MP4')

        # Only one values are going to accept for the tag --res. So nargs will be '1'
        parser.add_argument('--res', nargs=1, default=['480p'], type=str,
                            help='Resolution of the video output: for now we have 480p, 720p, 1080p & 4k')

        # Only one values are going to accept for the tag --name. So nargs will be '1'
        parser.add_argument('--name', nargs=1, default=['output'], type=str, help='Enter Output video title/name')

        # Parse the arguments and get all the values in the form of namespace.
        # Here args is of namespace and values will be accessed through tag names
        self.args = parser.parse_args()


def main():

    # Create a window and pass it to the Application object
    App(tk.Tk(), 'Video Recorder')



main()