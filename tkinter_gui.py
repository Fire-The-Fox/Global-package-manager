import subprocess
import tkinter as tk
from tkinter import Widget, filedialog
from tkinter.constants import X
from wget import download
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
    tmp_sudo.bind("<Escape>", lambda _: tmp_sudo.destroy())
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
    tmp_sudo_decline = tk.Button(tmp_sudo_label, text="Decline", relief=tk.SUNKEN, command=lambda: tmp_sudo.destroy())
    tmp_sudo_decline.place(anchor="center", relx=0.9, rely=0.8)
    bind_help(tmp_sudo_decline, "Cancel Instalation")
    unbind_help(tmp_sudo_decline)
    change_button_color(tmp_sudo_accept, "#2A6CF6")
    change_button_color(tmp_sudo_decline, "#2A6CF6")
    tmp_sudo_text = tk.Label(tmp_sudo_label, text=f"Enter sudo password for user: {getpass.getuser()}", font=("Calibri", 15), background="white")
    tmp_sudo_text.place(relx=0.05, rely=0.1)


def move_window(event):
    pref.geometry('+{0}+{1}'.format(event.x_root, event.y_root))
   

def preferences():
    global pref, pref_body
    output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
    x, y = str(output).split("x")
    x = x.strip("b'")
    y = y[:-3]
    x = int(x) / 2
    y = int(y) / 2
    pref = tk.Toplevel(root)
    pref.wm_overrideredirect(True)
    pref.wm_geometry("+%d+%d" % (x-300, y-40))
    pref.bind("<Escape>", lambda _: pref.destroy())
    pref_body = tk.Frame(pref, width=500, height=525, bg="white")
    pref_body.pack(ipadx=1)
    
    topbar = tk.Frame(pref_body, bg="black")
    topbar.place(x=0, y=0, relwidth=1, height=25)
    topbar.bind("<B1-Motion>", move_window)
    
    close_bar = tk.Button(topbar, text="X", font=("Calibri", 15), relief=tk.SUNKEN, foreground="white", activeforeground="white", bd=0, command=lambda: pref.destroy())
    close_bar.place(anchor="center", rely=0.5, x=480)
    change_button_color(close_bar, "black")
    
    toolbar = tk.Frame(pref_body, bg="lightgray")
    toolbar.place(x=0,y=25, relwidth=1, height=45)
    
    settings = tk.Button(toolbar, text="Settings", font=("Calibri", 20))
    settings.place(x=0, y=0, relheight=1, width=100)
    change_button_color(settings, "#2A6CF6")
    upload = tk.Button(toolbar, text="Upload", font=("Calibri", 20), command=lambda: upload_menu())
    upload.place(x=100, y=0, relheight=1, width=100)
    change_button_color(upload, "#2A6CF6")
    

def upload_menu():
    PackageFileText = tk.Label(pref_body, text="Please select executable file", bg="white")
    PackageFileText.place(x=10, y=80)
    
    # PackageFile = filedialog.askopenfile()
    # print(PackageFile.name)

def sudo_pass():
    global password, tmp_sudo_entry, DoThis
    password = tmp_sudo_entry.get()
    DoThis = DoThis.replace("pass", password)
    tmp_sudo.destroy()
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

names = []
urls = []
main_images = []
main_images_names = []
screenshots = {}
versions = []
for i in range(len(packages)):
    names.append(list(packages.keys())[i])
    urls.append(packages[list(packages.keys())[i]]["url"])
    main_images.append(packages[list(packages.keys())[i]]["thumbnail"])
    main_images_names.append(packages[list(packages.keys())[i]]["image_name"])
    screenshots[list(packages.keys())[i]] = []
    for ii in packages[list(packages.keys())[i]]["screenshots_url"]:
        screenshots[list(packages.keys())[i]].append(ii)
    versions.append(packages[list(packages.keys())[i]]["version"])
    if os.path.exists(main_images_names[i]):
        pass
    else:
        download(packages[list(packages.keys())[i]]["thumbnail"])

# ROOT

root = tk.Tk()
root.configure(width=WIDTH)
root.configure(height=HEIGHT)
root.configure(background="white")
root.title("Some package manager")
# root.minsize(height=500, width=875)
root.resizable(False, False)

# IMAGES

preferences_button_image = ImageTk.PhotoImage(Image.open("images/settings_button_image.png").resize(size=(25, 25)))
menu_button_image = tk.PhotoImage(file="images/menu_button_image.png")
search_image = ImageTk.PhotoImage(Image.open("images/search_button_image.png").resize(size=(25, 25)))

# GUI BASE

PackageScroll = tk.Scrollbar(root)
PackagesPanel = tk.Canvas(root, background="#1C72A9", yscrollcommand=PackageScroll.set, highlightthickness=0)
PackagesPanel.place(x=0, y=0, height=HEIGHT, width=WIDTH-13)


top_bar = tk.Frame(root, background="lightgray")
top_bar.place(x=0, y=0, relwidth=1, height=50)

search_bar = tk.Frame(top_bar, background="lightgray")
search_bar.place(anchor="center", relx=0.48, rely=0.5, width=500, relheight=1)

menu_panel = tk.Label(root, background="lightgray")

# GUI BUTTONS

preferences_button = tk.Button(top_bar, image=preferences_button_image, relief=tk.SUNKEN, bd=0, command=lambda: preferences())
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

# Packages Generation
x = 0
y = 49
specy = HEIGHT
PackageImage = []
for i in range(len(names)):
    Package = PackagesPanel.create_rectangle(x, y, x+250, y+250, fill="#1C72A9", outline="#1C72A9")
    PackageImage.append(ImageTk.PhotoImage(Image.open(main_images_names[i]).resize(size=(175, 175))))
    PackageThumb = PackagesPanel.create_image(x+250/2, y+250/2-15, image=PackageImage[i])
    PackagesPanel.tag_bind(PackageThumb, "<Button-1>", lambda _, tmp_i=i: print(names[tmp_i]))
    PackageText = PackagesPanel.create_text(x+250/2, y+250-25, text=names[i], font=("Calibri", 15))
    x += 250
    if x >= 1000:
        x = 0
        y += 250
        specy += 250
PackagesPanel.configure(scrollregion=(0, 0, 0, specy))
PackageScroll.place(anchor="n", x=WIDTH-7, y=50, height=500)
PackageScroll.config(command=PackagesPanel.yview)
# LOOP

root.mainloop()