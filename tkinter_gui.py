from shutil import copy2, make_archive, unpack_archive, rmtree
from distutils.dir_util import copy_tree
import subprocess
import tkinter as tk
from tkinter import Widget, filedialog
import glob
import wget
from PIL import Image, ImageTk
import getpass
import os
import json
from urllib.request import urlopen
from urllib.error import HTTPError
from io import BytesIO

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
    

def require_sudo(funcs, after):
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
    tmp_sudo_accept = tk.Button(tmp_sudo_label, text="Accept", relief=tk.SUNKEN, command=lambda: sudo_pass(funcs, after))
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
    upload = tk.Button(toolbar, text="Create", font=("Calibri", 20), command=lambda: upload_menu())
    upload.place(x=100, y=0, relheight=1, width=100)
    change_button_color(upload, "#2A6CF6")
    

def upload_menu():
    global PackageFolder, PackageExe
    PackageFolderText = tk.Label(pref_body, text="Please select folder to include all required files for package",
                                 bg="white")
    PackageFolderText.place(x=10, y=80)
    
    PackageFolder = tk.Entry(pref_body)
    PackageFolder.place(x=10, y=100, relwidth=0.8)
    
    PackageFolderButton = tk.Button(pref_body, text="select", command=lambda: select_folder())
    PackageFolderButton.place(anchor="w", relx=0.82, y=110)

    PackageBuildText = tk.Label(pref_body, text="Please write package description", bg="white")
    PackageBuildText.place(x=10, y=200)

    PackageBuildDescription = tk.Entry(pref_body)
    PackageBuildDescription.place(x=10, y=220, relwidth=0.8)
    
    PackageExeText = tk.Label(pref_body, text="Please select executable file of package", bg="white")
    PackageExeText.place(x=10, y=120)
    
    PackageExe = tk.Entry(pref_body)
    PackageExe.place(x=10, y=140, relwidth=0.8)
    
    PackageExeButton = tk.Button(pref_body, text="select", command=lambda: select_executable())
    PackageExeButton.place(anchor="w", relx=0.82, y=150)
    
    PackageNameText = tk.Label(pref_body, text="Please write package name", bg="white")
    PackageNameText.place(x=10, y=160)
    
    PackageName = tk.Entry(pref_body)
    PackageName.place(x=10, y=180, relwidth=0.8)
    
    PackageVerText = tk.Label(pref_body, text="Please write package version", bg="white")
    PackageVerText.place(x=10, y=240)
    
    PackageVer = tk.Entry(pref_body)
    PackageVer.place(x=10, y=260, relwidth=0.8)
    
    PackageImageText = tk.Label(pref_body, text="Please enter package icon url", bg="white")
    PackageImageText.place(x=10, y=280)
    
    PackageImage = tk.Entry(pref_body)
    PackageImage.place(x=10, y=300, relwidth=0.8)
    
    PackageThumbnails = tk.Label(pref_body, text="Please enter package screenshots url separated by ;", bg="white")
    PackageThumbnails.place(x=10, y=320)
    
    PackageThumbs = tk.Entry(pref_body)
    PackageThumbs.place(x=10, y=340, relwidth=0.8)

    CreateButton = tk.Button(pref_body, text="Create", command=lambda: GeneratePackage(PackageName.get(),
                                                                                       PackageFolder.get(),
                                                                                       PackageImage.get(),
                                                                                       PackageExe.get(),
                                                                                       PackageBuildDescription.get(),
                                                                                       PackageThumbs.get(),
                                                                                       PackageVer.get()))
    CreateButton.place(relx=0.8, rely=0.9)
    change_button_color(CreateButton, "#2A6CF6")


def GeneratePackage(name, dir, image, exe, description, screenshot, version):
    old_dir = os.getcwd()
    GeneratorData = [name, dir, image, exe, description, screenshot, version]
    for i in GeneratorData:
        if len(i) == 0:
            tk.messagebox.showinfo(title="Package Builder", message="Fill empty fields!")
            return
        else:
            continue
    try:
        for i in screenshot.split(";"):
            ImgURL = i
            u = urlopen(ImgURL)
            raw_data = u.read()
            u.close()
            del (raw_data)
    except HTTPError:
        tk.messagebox.showinfo(title="Package Builder",
                               message="One of Screenshot images url gives error 403 please type new url")
        return
    try:
        ImgURL = image
        u = urlopen(ImgURL)
        raw_data = u.read()
        u.close()
        del(raw_data)
    except HTTPError:
        tk.messagebox.showinfo(title="Package Builder",
                               message="Thumbnail image url gives error 403 please type new url")
        return
    DesktopFile = """[Desktop Entry]
Name={name}
Comment=Python Calculator
Exec=/home/{user}/SpecialSoftware/{name}{exe}
Icon=/home/{user}/SpecialSoftware/{name}Icons/{icon}
Terminal=false
Type=Application
Categories=Utility"""

    Packagejson = '''"{name}": {
        "url": "PackageHostUrl",
        "description": "{description}",
        "thumbnail": "{image}",
        "screenshots_url": {screenshots},
        "version": "{version}"
    }'''
    exe = exe.replace(dir, "")
    DesktopFile = DesktopFile.replace("{name}", name)
    os.mkdir(name)
    os.chdir(name)
    os.mkdir(name)
    copy_tree(dir, os.curdir+f"/{name}")
    Packagejson = Packagejson.replace("{description}", description)
    Packagejson = Packagejson.replace("{screenshots}", str(screenshot.split(";")))
    Packagejson = Packagejson.replace("{image}", image)
    Packagejson = Packagejson.replace("{version}", version)
    Packagejson = Packagejson.replace("{name}", name)
    Packagejson = Packagejson.replace("'", '"')
    wget.download(image)
    list_of_files = glob.glob('*.png')
    latest_file = max(list_of_files, key=os.path.getctime)
    os.mkdir(f"{name}Icons")
    copy2(latest_file, f"{name}Icons")
    os.remove(latest_file)
    DesktopFile = DesktopFile.replace("{icon}", latest_file)
    DesktopFile = DesktopFile.replace("{exe}", exe)
    DesktopFile = DesktopFile.replace("{user}", getpass.getuser())
    with open(f"{name}.desktop", "w") as file:
        file.write(DesktopFile)
    os.chdir(old_dir)
    make_archive(name, "zip", old_dir, name)
    rmtree(name)
    print("Then upload that file to some url and then put this into test.json and replace"
          " PackageHostUrl with url of that file on cloud")
    print(Packagejson)

def select_folder():
    file = filedialog.askdirectory()
    PackageFolder.delete(0, len(PackageFolder.get()))
    PackageFolder.insert(0, file)
    

def select_executable():
    file = filedialog.askopenfile()
    PackageExe.delete(0, len(PackageExe.get()))
    PackageExe.insert(0, file.name)


def sudo_pass(funcs, after):
    global password, tmp_sudo_entry, DoThis, old_dir, latest_file, Pname
    password = tmp_sudo_entry.get()
    try:
        DoThis = DoThis.replace("pass", password)
    except NameError:
        pass
    tmp_sudo.destroy()
    try:
        os.system(DoThis)
    except NameError:
        try:
            funcs2 = []
            for i in funcs:
                funcs2.append(i.replace("pass", password))
            for i in funcs2:
                os.system(i)
            try:
                for i in after:
                    exec(i)
                tk.messagebox.showinfo(title="Package Installer",
                                   message="Package was successfully installed")
            except NameError as E:
                return
        except NameError:
            return


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
    global DoThis
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


def on_mousewheel(event):
    global PackagesPanel
    if event.num == 5:
        PackagesPanel.yview_scroll(int(-1*(event.num*-48/120)), "units")
    if event.num == 4:
        PackagesPanel.yview_scroll(int(-1*((event.num+1)*48/120)), "units")


def PackageInfo(package_name):
    global ScreenShots, currentScreenshot, PackageImageSwitch, PackagePanel
    PackagePanel = tk.Label(root, background="#1C72A9", highlightthickness=0)
    PackagePanel.place(x=0, y=50, height=HEIGHT, width=WIDTH)
    PackagesPanel.place_forget()
    PackageScroll.place_forget()

    PackageName = tk.Label(PackagePanel, text=package_name, background="#1C72A9", font=("Calibri", 25))
    PackageName.place(x=60, y=10)
    currentScreenshot = 0
    ScreenShots = []
    for i in screenshots[package_name]:
        Description = Descriptions[package_name]
        ImgURL = i
        u = urlopen(ImgURL)
        raw_data = u.read()
        u.close()
        Tmp_Image = Image.open(BytesIO(raw_data))
        tmp_height, tmp_width = Tmp_Image.size
        if tmp_width > 256:
            Tmp_Image = Tmp_Image.resize(size=(256, 256))
        else:
            Tmp_Image = Tmp_Image.resize(size=(256, tmp_width))
        ScreenShots.append(Tmp_Image)

    BackButton = tk.Button(PackagePanel, text="Back", command=ReturnToPackages)
    BackButton.place(x=0, y=0)
    Imag = ImageTk.PhotoImage(ScreenShots[currentScreenshot])
    PackageImageSwitch = tk.Label(PackagePanel, image=Imag, highlightthickness=0, bd=0)
    PackageImageSwitch.photo = Imag
    PackageImageSwitch.place(x=60, y=50)

    PackageButtonLeft = tk.Button(PackagePanel, text="->", command=right_image)
    PackageButtonLeft.place(x=20+297, y=150)

    PackageButtonRight = tk.Button(PackagePanel, text="<-", command=left_image)
    PackageButtonRight.place(x=20, y=150)

    PackageDescription = tk.Text(PackagePanel, bg="#1C72A9", bd=0, font=("Calibri", 15), highlightthickness=0, selectbackground="#1C72A9")
    PackageDescription.insert(tk.INSERT, Description)
    PackageDescription.configure(state=tk.DISABLED)
    PackageDescription.place(relx=0.37, y=50, width=500, height=HEIGHT-150)

    PackageInstall = tk.Button(PackagePanel, text="Install", command=lambda: InstallThatBoi(package_name))
    PackageInstall.place(relx=0.9, y=50)


def InstallThatBoi(name):
    global old_dir, latest_file, Pname
    old_dir = os.getcwd()
    try:
        os.mkdir(f"/home/{getpass.getuser()}/SpecialSoftware")
    except FileExistsError:
        pass
    try:
        wget.download(urls[name])
        list_of_files = glob.glob('*.zip')
        latest_file = max(list_of_files, key=os.path.getctime)
    except ValueError:
        tk.messagebox.showinfo(title="Package Installer",
                               message="Package gives error 404 please wait till package owner update's package "
                                       "download url")
        return
    unpack_archive(latest_file, "")
    os.remove(latest_file)
    os.chdir(latest_file[:-4])
    Pname = os.listdir()[0]
    Pname = Pname.replace("Icons", "")
    Pname = Pname.replace(".desktop", "")
    require_sudo([f"echo pass | sudo -S cp -R {Pname} /home/{getpass.getuser()}/SpecialSoftware/",
                  f"echo pass | sudo -S cp -R {Pname}Icons /home/{getpass.getuser()}/SpecialSoftware/",
        f"echo pass | sudo -S cp {Pname}.desktop /home/{getpass.getuser()}/.local/share/applications/{Pname}.desktop",
                  f"echo pass | sudo -S chmod +x /home/{getpass.getuser()}/SpecialSoftware/{Pname}/*"],
                 [f"os.chdir('{old_dir}')", f'rmtree("{latest_file[:-4]}")'])


def ReturnToPackages():
    global PackagePanel
    PackagePanel.destroy()
    del(PackagePanel)
    PackagesPanel.place(x=0, y=0, height=HEIGHT, width=WIDTH - 13)
    PackageScroll.place(anchor="n", x=WIDTH - 7, y=50, height=500)


def right_image():
    global ScreenShots, currentScreenshot
    old_curent = currentScreenshot
    try:
        currentScreenshot += 1
        Imag = ImageTk.PhotoImage(ScreenShots[currentScreenshot])
        PackageImageSwitch.configure(image=Imag)
        PackageImageSwitch.photo = Imag
    except IndexError:
        currentScreenshot = old_curent
        pass


def left_image():
    global ScreenShots, currentScreenshot
    old_curent = currentScreenshot
    try:
        currentScreenshot -= 1
        if currentScreenshot < 0:
            currentScreenshot = 0
        Imag = ImageTk.PhotoImage(ScreenShots[currentScreenshot])
        PackageImageSwitch.configure(image=Imag)
        PackageImageSwitch.photo = Imag
    except IndexError:
        currentScreenshot = old_curent
        pass



# VARIABLES

WIDTH = 1000
HEIGHT = 550
menu_shown = False
menu_options = ["Update System", "Update Package Repository"]
menu_help = ["This will update your entire system", "This will update packages on repository"]
menu_options_functions = ['update_os()', 'update_repo()']
max_height_of_generation = 1 / len(menu_options)

with open("test.json") as file:
    packages = json.load(file)

names = []
urls = {}
main_images = []
screenshots = {}
versions = []
Descriptions = {}
zips = []
for i in range(len(packages)):
    names.append(list(packages.keys())[i])
    urls[list(packages.keys())[i]] = packages[list(packages.keys())[i]]["url"]
    main_images.append(packages[list(packages.keys())[i]]["thumbnail"])
    screenshots[list(packages.keys())[i]] = []
    Descriptions[list(packages.keys())[i]] = packages[list(packages.keys())[i]]["description"]
    for ii in packages[list(packages.keys())[i]]["screenshots_url"]:
        screenshots[list(packages.keys())[i]].append(ii)
    versions.append(packages[list(packages.keys())[i]]["version"])

# ROOT

root = tk.Tk()
root.configure(width=WIDTH)
root.configure(height=HEIGHT)
root.configure(background="white")
root.title("Some package manager")
root.configure(background="#1C72A9")
# root.minsize(height=500, width=875)
root.resizable(False, False)

# IMAGES

preferences_button_image = ImageTk.PhotoImage(Image.open("images/settings_button_image.png").resize(size=(25, 25)))
menu_button_image = tk.PhotoImage(file="images/menu_button_image.png")
search_image = ImageTk.PhotoImage(Image.open("images/search_button_image.png").resize(size=(25, 25)))

# GUI BASE

PackageScroll = tk.Scrollbar(root)
PackagesPanel = tk.Canvas(root, background="#1C72A9", yscrollcommand=PackageScroll.set, highlightthickness=0)
PackagesPanel.bind_all("<Button-4>", on_mousewheel)
PackagesPanel.bind_all("<Button-5>", on_mousewheel)
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
NoSkip = False
PackageImage = []
for i in range(len(names)):
    Package = PackagesPanel.create_rectangle(x, y, x+250, y+250, fill="#1C72A9", outline="#1C72A9")
    ImgURL = main_images[i]
    u = urlopen(ImgURL)
    raw_data = u.read()
    u.close()
    PackageImage.append(ImageTk.PhotoImage(Image.open(BytesIO(raw_data)).resize(size=(175, 175))))
    PackageThumb = PackagesPanel.create_image(x+250/2, y+250/2-15, image=PackageImage[i])
    PackagesPanel.tag_bind(PackageThumb, "<Button-1>", lambda _, tmp_i=i: PackageInfo(names[tmp_i]))
    PackageText = PackagesPanel.create_text(x+250/2, y+250-25, text=names[i], font=("Calibri", 15))
    x += 250
    if x == 250 and y >= 500:
        specy += 250
    if x >= 1000:
        x = 0
        y += 250
PackagesPanel.configure(scrollregion=(0, 0, 0, specy))
PackageScroll.place(anchor="n", x=WIDTH-7, y=50, height=500)
PackageScroll.config(command=PackagesPanel.yview)
# LOOP
if __name__ == '__main__':
    root.mainloop()
