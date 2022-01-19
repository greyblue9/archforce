from os import getcwd
from os.path import isfile
from platform import machine
from json import load, dump
from webbrowser import open_new_tab
from threading import Thread
from asyncio import get_event_loop_policy, sleep
from zipfile import ZipFile, BadZipFile
from tarfile import TarFile
from tkinter import Tk, Toplevel, filedialog, Menu, StringVar, Label, Button, Entry, Text
from tkinter.messagebox import showinfo, showerror, askyesno

try:
    with open("json.json", "r") as f:
        _json = load(f)
except:
    showerror(title="Error - ArchForce", message="json.json couldn't be loaded, please check if it exists, or reinstall ArchForce.", icon="error")

    exit()

VERSION = "v1.0.0a"
DESCRIPTION = "ArchForce is an archive bruteforcer, it takes a dictionary of passwords and tries to extract the archive with it. If there are any issues or you want a feature to be added, please open an issue in the project's GitHub repository."
INSTRUCTIONS = "To bruteforce a file, firstly, choose the type of the archive you're going to bruteforce, secondly, choose the target archive you want to bruteforce, then choose a dictionary (A file) with the list of passwords that could potentially be the password for the archive seperated by newlines. Then just click \"Bruteforce\" and the bruteforcing process will start, you will be alerted when the password has been found."

archive = None
passwords = None
window = Tk()

window.title("ArchForce")
window.resizable(False, False)
window.geometry("300x210")

def about():
    showinfo(title="About - ArchForce", message=f"""Version: {VERSION}

{DESCRIPTION}""", icon="info")

def instructions():
    showinfo(title="Instructions - ArchForce", message=INSTRUCTIONS, icon="info")

def github():
    open_new_tab("https://github.com/lthon09/archforce")

menu = Menu(window)

_help = Menu(menu, tearoff=0)

menu.add_cascade(label="Help", menu=_help)

_help.add_command(label="About", command=about)
_help.add_command(label="Instructions", command=instructions)
_help.add_command(label="GitHub Repository", command=github)

def save_json():
    with open("json.json", "w") as f:
        dump(_json, f, indent=4)

def prefs1():
    if _json["prefs"]["saveInputs"][0]:
        _json["prefs"]["saveInputs"] = False
    else:
        _json["prefs"]["saveInputs"] = True

    save_json()

def reset_prefs():
    for pref in _json["prefs"]:
        _json["prefs"][pref][0] = _json["prefs"][pref][1]

    save_json()

prefs = Menu(menu, tearoff=0)

menu.add_cascade(label="Preferences", menu=prefs)

prefs.add_command(label="Save Inputs", command=prefs1)
prefs.add_command(label="Reset", command=reset_prefs)

window.config(menu=menu)

def validate_ext(ext):
    exts = ["zip", "gz", "bz2", "lzma"]

    if ext in exts:
        return True
    else:
        return False

def open_file(mode):
    global archive, passwords

    dialog = filedialog.askopenfilename(
        title="Open a File - ArchForce",
        initialdir=getcwd(),
        filetypes=(
            ("All Files", "*.*"),
        )
    )

    if dialog:
        if mode == "archive":
            archive = dialog
        elif mode == "passwords":
            passwords = dialog

        if _json["prefs"]["saveInputs"][0]:
            _json["inputs"]["archive"] = archive
            _json["inputs"]["passwords"] = passwords

            save_json()

stopped = False

def bruteforce():
    global stopped
    stopped = False
    if not archive or not passwords:
        showerror(title="Error - ArchForce", message="You have to choose an archive and a passwords dictionary in order to bruteforce.", icon="error")
    elif not validate_ext(archive.split(".")[-1]):
        showerror(title="Error - ArchForce", message="The archive chosen isn't supported. Supported archive extensions: .zip, .gz, .bz2, .lzma", icon="error")
    else:
        window.withdraw()

        global index
        index = 0

        def pause():
            pause_btn.config(state="disabled")
            resume_btn.config(state="normal")
            loop.call_soon_threadsafe(loop.stop)

        def resume():
            pause_btn.config(state="normal")
            resume_btn.config(state="disabled")
            loop.call_soon_threadsafe(loop.run_forever)

        def stop():
            pause_btn.config(state="disabled")
            resume_btn.config(state="disabled")
            stop_btn.config(state="disabled")

            loop.call_soon_threadsafe(loop.stop)

        def _stop():
            question = askyesno(title="Stop - ArchForce", message="Are you sure you wanna stop the bruteforcer?", icon="question")

            if question:
                stop()

        def __stop():
            print("Stopped")
            stopped = True
            _window.destroy()
            window.deiconify()

        def write_logs(log, plus):
            logs.config(state="normal")
            logs.insert("end", f"#{index + 1 if plus else index}: {log}")
            logs.config(state="disabled")

        def _bruteforce():
            async def __bruteforce():
                global index

                with open(passwords, "r") as f:
                    pwds = f.readlines()

                if archive.endswith(".zip"):
                    try:
                        with ZipFile(archive, "r") as _f:
                            pass
                    except BadZipFile:
                        showerror(title="Error - ArchForce", message="The archive is corrupted.", icon="error")

                        write_logs("The archive is corrupted.", True)

                        stop()

                    with ZipFile(archive, "r") as _f:
                        while not stopped:
                            index += 1

                            try:
                                _f.extractall(path="temp/extracted", pwd=bytes(pwds[index], "utf-8"))

                                write_logs(f"Password Found: {pwds[index]}. Archive extracted into \"temp\".", False)

                                logs.see("end")

                                showinfo(title="Extracted - ArchForce", message="The password has been found.", icon="info")

                                stop()
                            except RuntimeError:
                                write_logs(f"Tried Password: {pwds[index]}", False)

                                logs.see("end")
                            except IndexError:
                                raise
                            except Exception as error:
                                write_logs(f"Error Occured: {error}", False)

                                showerror(title="Error - ArchForce", message=f"An error occured:\n{error}", icon="error")

                                return

                            await sleep(int(sleep_var.get()))
                elif archive.endswith(".gz"):
                    pass
                elif archive.endswith(".bz2"):
                    pass
                elif archive.endswith(".lzma"):
                    pass

            ## end def __bruteforce
            loop.run_until_complete(__bruteforce())

        _window = Toplevel()

        _window.title("Bruteforcer - ArchForce")
        _window.resizable(False, False)
        _window.geometry("800x650")

        sleep_time_info = Label(_window, text=f"Sleep Time: {sleep_var.get()} second(s)")

        logs = Text(_window, height=30)

        logs.config(state="disabled")

        pause_btn = Button(_window, text="Pause", command=pause)
        resume_btn = Button(_window, text="Resume", command=resume)
        stop_btn = Button(_window, text="Stop", command=stop)

        resume_btn.config(state="disabled")

        place = {
            sleep_time_info: [30, 5],
            logs: [73, 55],
            pause_btn: [450, 570],
            resume_btn: [540, 570],
            stop_btn: [640, 570]
        }

        for widget in place:
            widget.place(x=place[widget][0], y=place[widget][1])

        loop = get_event_loop_policy().get_event_loop()
        Thread(target=_bruteforce).start()

        _window.protocol("WM_DELETE_WINDOW", __stop)

        _window.mainloop()


sleep_time = Label(window, text="Sleep Time:")

sleep_var = StringVar()

def sleep_callback(*args):
    try:
        int(sleep_var.get())

        if len(sleep_var.get()) > 2:
            sleep_var.set(sleep_var.get()[:-1])

        _json["inputs"]["sleepTime"] = sleep_var.get()

        save_json()
    except ValueError:
        sleep_var.set(sleep_var.get()[:-1])

_sleep_time = Entry(window, width=2, textvariable=sleep_var)

_sleep_time.insert(0, "0")

sleep_var.trace_add("write", sleep_callback)

__sleep_time = Label(window, text="second(s)")

choose_arch = Button(window, text="Choose Archive", command=lambda : open_file("archive"))
choose_pwds = Button(window, text="Choose Passwords", command=lambda : open_file("passwords"))

_bruteforce = Button(window, text="Bruteforce", command=bruteforce)

author = Label(window, text="Tool by lthon09")

place = {
    sleep_time: [75, 10],
    _sleep_time: [145, 10],
    __sleep_time: [163, 10],
    choose_arch: [25, 60],
    choose_pwds: [164, 60],
    _bruteforce: [115, 118],
    author: [103, 180]
}

for widget in place:
    widget.place(x=place[widget][0], y=place[widget][1])

if _json["prefs"]["saveInputs"][0]:
    sleep_var.set(_json["inputs"]["sleepTime"])

    if isfile(_json["inputs"]["archive"]):
        archive = _json["inputs"]["archive"]
    else:
        _json["inputs"]["archive"] = ""

    if isfile(_json["inputs"]["passwords"]):
        passwords = _json["inputs"]["passwords"]
    else:
        _json["inputs"]["passwords"] = ""

    save_json()

window.mainloop()
