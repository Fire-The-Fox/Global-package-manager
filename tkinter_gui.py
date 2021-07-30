import subprocess
import tkinter as tk
from PIL import Image, ImageTk
import getpass
import os
import json

# FUNCTIONS


def show_hint(object, text : str):
    global tmp_top, tmp_top_label
    x = y = 0
    x += object.winfo_rootx() + 25
    y += object.winfo_rooty() + 20
    tmp_top = tk.Toplevel(object)
    tmp_top.wm_overrideredirect(True)
    tmp_top.wm_geometry("+%d+%d" % (x, y))
    tmp_top_label = tk.Label(tmp_top, text=text, justify='left', background="#ffffff", relief='solid', borderwidth=1)
    tmp_top_label.pack(ipadx=1)
    

def require_sudo():
    global tmp_sudo, tmp_sudo_entry
    output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
    x, y = str(output).split("x")
    x = x.strip("b'")
    y = y[:-3]
    x = int(x) / 2
    y = int(y) / 2
    tmp_sudo = tk.Toplevel(root)
    tmp_sudo.wm_overrideredirect(True)
    tmp_sudo.wm_geometry("+%d+%d" % (x-300, y-40))
    tmp_sudo.bind("<Escape>", lambda _: kill_sudo())
    tmp_sudo_label = tk.Label(tmp_sudo, width=75, height=10, background="white")
    tmp_sudo_label.pack(ipadx=1)
    tmp_sudo_entry = tk.Entry(tmp_sudo_label, show="*", font=("Calibri", 20))
    tmp_sudo_entry.place(anchor="w", relx=0.05, rely=0.5, relheight=0.3, relwidth=0.9)
    bind_help(tmp_sudo_entry, f"Enter sudo password for user {getpass.getuser()}")
    unbind_help(tmp_sudo_entry)
    tmp_sudo_accept = tk.Button(tmp_sudo_label, text="Accept", relief=tk.SUNKEN, command=lambda: sudo_pass())
    tmp_sudo_accept.place(anchor="center", relx=0.1, rely=0.8)
    bind_help(tmp_sudo_accept, "Continue installation")
    unbind_help(tmp_sudo_accept)
    tmp_sudo_decline = tk.Button(tmp_sudo_label, text="Decline", relief=tk.SUNKEN, command=lambda: kill_sudo())
    tmp_sudo_decline.place(anchor="center", relx=0.9, rely=0.8)
    bind_help(tmp_sudo_decline, "Cancel Instalation")
    unbind_help(tmp_sudo_decline)
    change_button_color(tmp_sudo_accept, "#2A6CF6")
    change_button_color(tmp_sudo_decline, "#2A6CF6")
    tmp_sudo_text = tk.Label(tmp_sudo_label, text=f"Enter sudo password for user: {getpass.getuser()}", font=("Calibri", 15), background="white")
    tmp_sudo_text.place(relx=0.05, rely=0.1)


def kill_sudo():
    tmp_sudo.destroy()


def sudo_pass():
    global password, tmp_sudo_entry, DoThis
    password = tmp_sudo_entry.get()
    DoThis = DoThis.replace("pass", password)
    kill_sudo()
    os.system(DoThis)


def hide_hint():
    global tmp_top_label, tmp_top, triggered
    try:
        tmp_top_label.destroy()
        tmp_top.destroy()
        triggered = False
    except:
        pass


def change_button_color(button : tk.Button, color : str):
    button.configure(background=color, highlightcolor=color, activebackground=color, highlightthickness=0)


def show_menu():
    global menu_shown, WIDTH, menu_panel
    if not menu_shown:
        menu_shown = True
        menu_panel.place(relx=0, y=49.5, relheight=1, relwidth=0.25)
    else:
        menu_shown = False
        menu_panel.place_forget()


def update_os():
    global  DoThis
    DoThis = "echo pass | sudo -S pacman --noconfirm -Syu"
    require_sudo()


def update_repo():
    global DoThis
    DoThis = "echo pass | sudo -S pacman --noconfirm -Syy"
    require_sudo()


def bind_help(object, text):
    object.bind("<Enter>", lambda _: object.after(500, show_hint(object, text=text)))


def unbind_help(object):
    object.bind("<Leave>", lambda _: hide_hint())


# VARIABLES

WIDTH = 1000
HEIGHT = 550
menu_shown = False
menu_options = ["Update System", "Update Package Repository"]
menu_help = ["This will update your entire system", "This will update packages on repository"]
menu_options_functions = [ 'update_os()', 'update_repo()']
max_height_of_generation = 1 / len(menu_options)

with open("test.json") as file:
    packages = json.load(file)

# ROOT

root = tk.Tk()
root.configure(width=WIDTH)
root.configure(height=HEIGHT)
root.configure(background="white")
root.title("Some package manager")
root.minsize(height=500, width=875)

# IMAGES

preferences_button_image = ImageTk.PhotoImage(Image.open("images/settings_button_image.png").resize(size=(25, 25)))
menu_button_image = tk.PhotoImage(file="images/menu_button_image.png")
search_image = ImageTk.PhotoImage(Image.open("images/search_button_image.png").resize(size=(25, 25)))

# GUI BASE

top_bar = tk.Frame(root, background="lightgray")
top_bar.place(x=0, y=0, relwidth=1, height=50)

search_bar = tk.Frame(top_bar, background="lightgray")
search_bar.place(anchor="center", relx=0.48, rely=0.5, width=500, relheight=1)

menu_panel = tk.Label(root, background="lightgray")

# GUI BUTTONS

preferences_button = tk.Button(top_bar, image=preferences_button_image, relief=tk.SUNKEN, bd=0)
preferences_button.place(anchor="center", relx=0.97, rely=0.48, relheight=0.6, relwidth=0.03)
bind_help(preferences_button, "Preferences button")
unbind_help(preferences_button)
preferences_button.bind("<ButtonPress>", lambda _: hide_hint())
change_button_color(preferences_button, "lightgray")
menu_button = tk.Button(top_bar, image=menu_button_image, bd=0, relief=tk.SUNKEN, command=show_menu)
menu_button.place(anchor="center", x=25, rely=0.48)
bind_help(menu_button, "Menu button")
unbind_help(menu_button)

search_button = tk.Button(search_bar, image=search_image, bd=0, relief=tk.SUNKEN)
search_button.place(anchor="center", relx=0.93, rely=0.5)
bind_help(search_button, "Button for searching packages")
unbind_help(search_button)
change_button_color(search_button, "lightgray")

change_button_color(menu_button, "lightgray")

# SEARCH

search = tk.Entry(search_bar, font=("Calibri", 15))
search.place(anchor="center", relx=0.5, width=400, rely=0.5, relheight=0.65)
search.bind("<Return>", lambda _: print("enter"))
search.bind("<Enter>", lambda _: search.after(500, show_hint(search, "Entry where you can type what keyword search for")))
bind_help(search, "Entry where you can type what keyword search for")
unbind_help(search)

# MENU GENERATION

for i in range(len(menu_options)):
    tmp_button = tk.Button(menu_panel, text=menu_options[i], command=lambda tmp_i=i: exec(menu_options_functions[tmp_i]))
    tmp_button.pack()
    bind_help(tmp_button, text=menu_help[i])
    unbind_help(tmp_button)

# LOOP

root.mainloop()