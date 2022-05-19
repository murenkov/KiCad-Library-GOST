import sys
import threading
import subprocess
import base64
import shutil
import zipfile
import webbrowser
import urllib
import io
import json
import os
import platform
import time
from shutil import copyfile
import re
import ctypes


if sys.version_info[0] == 3:
    # Python 3 imports
    import urllib.parse
    import urllib.request
    import tkinter as tk
    import tkinter.messagebox as tkMessageBox
    from io import StringIO as StringIO
    from tkinter import ttk
    
else:
    # Python 2 imports
    import Tkinter as tk
    import tkMessageBox
    from StringIO import StringIO
    import ttk
    import urllib2

class TableView(tk.Frame):
    '''
    Table view for listing the results
    '''

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.is_mac = platform.mac_ver()[0] != ""
        self.is_windows = (os.name == 'nt')
        if self.is_windows:
            self.windata_dir = os.path.join(os.getenv('HOMEDRIVE'),
                                            os.getenv('HOMEPATH'),
                                            "SnapEDA Kicad Plugin")
            self.flip_table_dir = os.path.join(os.getenv('HOMEDRIVE'),
                                               os.getenv('HOMEPATH'),
                                               'AppData',
                                               'Roaming',
                                               'kicad',
                                               'fp-lib-table')
            self.appdata_dir = os.path.join(self.windata_dir, "App")
            if not os.path.exists(self.windata_dir):
                os.makedirs(self.windata_dir)
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir)
            self.kicad_library_dir = os.path.join(self.windata_dir, 'KiCad Library')
            self.snapeda_library_abs_dir = os.path.join(self.kicad_library_dir,
                                                   'SnapEDA Library.pretty')
            if not os.path.exists(self.kicad_library_dir):
                os.makedirs(self.kicad_library_dir)
            if not os.path.exists(self.snapeda_library_abs_dir):
                os.makedirs(self.snapeda_library_abs_dir)
        elif self.is_mac:
            self.macdata_dir = os.path.join(os.path.expanduser("~"), "Documents", "SnapEDA Kicad Plugin")
            self.appdata_dir = os.path.join(self.macdata_dir, "App")
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir)
        else:
            self.appdata_dir = os.path.join(self.dir_path, "assets")
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir)
            self.flip_table_dir = os.path.join(os.path.expanduser("~"),
                                               '.config',
                                               'kicad',
                                               'fp-lib-table')
            home_dir = os.path.expanduser("~")
            self.kicad_library_dir = os.path.join(home_dir, 'KiCad Library')
            self.snapeda_library_abs_dir = os.path.join(self.kicad_library_dir,
                                                   'SnapEDA Library.pretty')
            if not os.path.exists(self.kicad_library_dir):
                os.makedirs(self.kicad_library_dir)
            if not os.path.exists(self.snapeda_library_abs_dir):
                os.makedirs(self.snapeda_library_abs_dir)
        self.icon_bitmap_dir = os.path.join(self.appdata_dir, "32x32.ico")
        self.filter_button_image_dir = os.path.join(self.appdata_dir, "neeo2s8g.png")
        self.settings_button_image_dir = os.path.join(self.appdata_dir, "7svfoe57.png")
        self.about_button_image_dir = os.path.join(self.appdata_dir, "2kdtezsl.png")
        self.passive_components_image_dir = os.path.join(self.appdata_dir, "t3gwhnzh.png")
        self.all_button_image_dir = os.path.join(self.appdata_dir, "dsyrvfl9.png")
        self.powered_image_dir = os.path.join(self.appdata_dir, "orb6glbv.png")
        self.datasheet_button_dir = os.path.join(self.appdata_dir, "oxfarxz8.png")
        self.datasheet_available_dir = os.path.join(self.appdata_dir, "m4lamm2w.png")
        self.datasheet_not_available_dir = os.path.join(self.appdata_dir, "4cnn9kkf.png")
        self.symbol_available_dir = os.path.join(self.appdata_dir, "huaxvbtm.png")
        self.symbol_not_available_dir = os.path.join(self.appdata_dir, "tmuhgmxh.png")
        self.footprint_available_dir = os.path.join(self.appdata_dir, "3ruuehki.png")
        self.footprint_not_available_dir = os.path.join(self.appdata_dir, "62r7iuz7.png")
        self.available_dir = os.path.join(self.appdata_dir, "uku4ceuv.png")
        self.not_available_dir = os.path.join(self.appdata_dir, "zah3n8r4.png")
        self.prev_bg_dir = os.path.join(self.appdata_dir, "iu2ma3jp.png")
        self.next_bg_dir = os.path.join(self.appdata_dir, "witafnjf.png")
        self.selected_page_dir = os.path.join(self.appdata_dir, "izif2qd8.png")
        self.download_button_dir = os.path.join(self.appdata_dir, "download+orange.png")
        self.view_button_dir = os.path.join(self.appdata_dir, "viewonsnapeda+white.png")
        self.search_button_image_dir = os.path.join(self.appdata_dir, "4i2efbui.png")
        self.loading_image_dir = os.path.join(self.appdata_dir, "jwhk6qck.gif")
        self.initialize_user_interface()

    def download_component(self, event):
        if not self.is_downloading:
            self.is_downloading = True
            download_thread = threading.Thread(target=self.download_data)
            download_thread.start()
            self.download_button.config(state="disabled")

    # Runs when download button is clicked
    def download_data(self):
        # webbrowser.open("https://www.snapeda.com" + self.url, new=2)
        token = ""
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # Read saved token
        if self.is_windows:
            with open(os.path.join(self.appdata_dir, ".token"), "r") as f:
                token = str(f.readline())

        else:
            with open(os.path.join(dir_path, ".token"), "r") as f:
                token = str(f.readline())
        url = "https://www.snapeda.com/api/v1/parts/download_part"
        header = {'User-Agent': "Kicad"}
        values = {
            'part_number': str(self.part_number),
            'manufacturer': str(self.manufacturer),
            'has_symbol': self.has_symbol,
            'has_footprint': self.has_footprint,
            'uniqueid': self.uniqueid,
            'token': token,
            'format': "kicad_mod",
            'ref': "kicad-plugin",
        }

        if sys.version_info[0] == 3:
            data = urllib.parse.urlencode(values).encode("utf-8")
            req = urllib.request.Request(url, data, headers=header)
            contents = urllib.request.urlopen(req).read()
        else:
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data, headers=header)
            contents = urllib2.urlopen(req).read()
        self.download_url = json.loads(contents)["url"]
        print(self.download_url)
        header = {'User-Agent': "Kicad"}
        if len(self.download_url) == 0:
            tkMessageBox.showwarning("Warning", "No models for this part")
            self.download_button.config(state="normal", text="Download")
            self.is_downloading = False
            return
        self.part_number = self.part_number.replace('/', '_')
        if sys.version_info[0] == 3:
            download_req = urllib.request.Request(self.download_url, headers=header)
            download_contents = urllib.request.urlopen(download_req)
        else:
            download_req = urllib2.Request(self.download_url, headers=header)
            download_contents = urllib2.urlopen(download_req)
        if self.is_windows:
            kicad_library_dir = os.path.join(self.windata_dir, 'KiCad Library')
            snapeda_library_dir = os.path.join(kicad_library_dir,
                                               'SnapEDA Library')
            snapeda_library_abs_dir = os.path.join(kicad_library_dir,
                                                   'SnapEDA Library.pretty')
            temp_dir = os.path.join(kicad_library_dir, 'temp')
            part_dir = os.path.join(temp_dir, str(self.part_number))
            if not os.path.exists(kicad_library_dir):
                os.makedirs(kicad_library_dir)
            if not os.path.exists(snapeda_library_dir):
                os.makedirs(snapeda_library_dir)
            if not os.path.exists(part_dir):
                os.makedirs(part_dir)
            if not os.path.exists(snapeda_library_abs_dir):
                os.makedirs(snapeda_library_abs_dir)
            with open(os.path.join(part_dir, self.part_number + ".zip"),
                      "wb") as f:
                shutil.copyfileobj(download_contents, f)
            with zipfile.ZipFile(
                    os.path.join(part_dir, self.part_number + ".zip")) as zf:
                zf.extractall(part_dir)
            for file in os.listdir(part_dir):
                if file.endswith(".kicad_mod"):
                    kicad_mod_file_dir = os.path.join(part_dir, file)
                    copyfile(kicad_mod_file_dir, os.path.join(snapeda_library_abs_dir, file))

                if file.endswith(".lib"):
                    kicad_lib_file_dir = os.path.join(part_dir, file)
                    copyfile(kicad_lib_file_dir, os.path.join(snapeda_library_dir, file))

                    self.sym_lib_table_dir = os.path.join(os.getenv('HOMEDRIVE'),
                                               os.getenv('HOMEPATH'),
                                               'AppData',
                                               'Roaming',
                                               'kicad',
                                               'sym-lib-table')

                    if(os.path.exists(self.sym_lib_table_dir) != True):
                        template = '(sym_lib_table\n\n)'
                        with open(self.sym_lib_table_dir, 'w') as d:
                            d.write(template)
                            d.close

                    with open(self.sym_lib_table_dir, "r+") as f:
                        table = f.read()
                        if '(lib (name ' + os.path.splitext(file)[0] + ')(type Legacy)' not in table:
                            new_entry = ('  (lib (name ' + os.path.splitext(file)[0] + ')(type Legacy)(uri "' + snapeda_library_dir + '\\' + str(file) + '")(options "")(descr ""))') + "\n\n)"
                            new_entry = new_entry.replace("'", "")
                            new_entry = new_entry.replace("\\", "/")
                            print(new_entry)
                            new_table = table[:-2] + new_entry
                            f.seek(0)
                            f.write(new_table)
                            f.truncate()
                    
            shutil.rmtree(temp_dir)

        else:
            home_dir = os.path.expanduser("~")
            kicad_library_dir = os.path.join(home_dir, 'KiCad Library')
            snapeda_library_dir = os.path.join(kicad_library_dir,
                                               'SnapEDA Library')
            snapeda_library_abs_dir = os.path.join(kicad_library_dir,
                                                   'SnapEDA Library.pretty')
            temp_dir = os.path.join(kicad_library_dir, 'temp')
            part_dir = os.path.join(temp_dir, str(self.part_number))
            if not os.path.exists(kicad_library_dir):
                os.makedirs(kicad_library_dir)
            if not os.path.exists(snapeda_library_dir):
                os.makedirs(snapeda_library_dir)
            if not os.path.exists(part_dir):
                os.makedirs(part_dir)
            if not os.path.exists(snapeda_library_abs_dir):
                os.makedirs(snapeda_library_abs_dir)
            with open(os.path.join(part_dir, self.part_number + ".zip"),
                      "wb") as f:
                shutil.copyfileobj(download_contents, f)
            zip_path = os.path.join(part_dir, self.part_number + ".zip")
            if self.is_windows:
                zip_path = self.winapi_path(zip_path)
                part_dir = self.winapi_path(part_dir)
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(part_dir)
            for file in os.listdir(part_dir):
                if file.endswith(".kicad_mod"):
                    kicad_mod_file_dir = os.path.join(part_dir, file)
                    copyfile(kicad_mod_file_dir, os.path.join(snapeda_library_abs_dir, file))

                if file.endswith(".lib"):
                    kicad_lib_file_dir = os.path.join(part_dir, file)
                    copyfile(kicad_lib_file_dir, os.path.join(snapeda_library_dir, file))
                    
                    self.sym_lib_table_dir = os.path.join(os.path.expanduser("~"),
                                               '.config',
                                               'kicad',
                                               'sym-lib-table')

                    if(os.path.exists(self.sym_lib_table_dir) != True):
                        template = '(sym_lib_table\n\n)'
                        with open(self.sym_lib_table_dir, 'w') as d:
                            d.write(template)
                            d.close

                    with open(self.sym_lib_table_dir, "r+") as f:
                        table = f.read()
                        if '(lib (name ' + os.path.splitext(file)[0] + ')(type Legacy)' not in table:
                            new_entry = ('  (lib (name ' + os.path.splitext(file)[0] + ')(type Legacy)(uri "' + snapeda_library_dir + '\\' + str(file) + '")(options "")(descr ""))') + "\n\n)"
                            new_entry = new_entry.replace("'", "")
                            new_entry = new_entry.replace("\\", "/")
                            print(new_entry)
                            new_table = table[:-2] + new_entry
                            f.seek(0)
                            f.write(new_table)
                            f.truncate()
                    
            shutil.rmtree(temp_dir)

        tkMessageBox.showinfo("Done", "The download is completed")
        self.download_button.config(state="normal", text="Download")
        self.is_downloading = False

    def winapi_path(self, dos_path, encoding=None):
        if (not isinstance(dos_path, unicode) and encoding is not None):
            dos_path = dos_path.decode(encoding)
        path = os.path.abspath(dos_path)
        if path.startswith(u"\\\\"):
            return u"\\\\?\\UNC\\" + path[2:]
        return u"\\\\?\\" + path

    def contact_us(self):
        webbrowser.open("https://www.snapeda.com/about/#contact_us", new=2)

    def about_snapeda(self):
        webbrowser.open("https://www.snapeda.com/about/", new=2)

    def view_on_snapeda(self, url):
        webbrowser.open("https://www.snapeda.com%s?ref=kicad" % url, new=2)

    def how_it_works_callback(self, event):
        instruction_text = '''
            Instructions:
            1. Search for the part, for example "USB Type C".
            2. Choose from the results and select the part you like.
            3. Click Download.
            4. Click Place > Symbol or Place > Footprint.
            5. Find the downloaded part under "SnapEDA Library".
            6. Use it in your design.
        '''
        tkMessageBox.showinfo("How it works", instruction_text)

    def logout_callback(self, event):
        try:
            if self.is_windows:
                self.windata_dir = os.path.join(os.getenv('HOMEDRIVE'),
                                                os.getenv('HOMEPATH'),
                                                "SnapEDA Kicad Plugin")
                self.appdata_dir = os.path.join(self.windata_dir, "App")
                rem_path = os.path.join(self.appdata_dir, ".token")
                os.remove(rem_path)
            else:
                self.dir_path = os.path.dirname(os.path.realpath(__file__))
                rem_path = os.path.join(self.dir_path, ".token")
                os.remove(rem_path)
        except:
            print('Error removing token.')
        for i in range(5):
            for widget in self.parent.grid_slaves(row=i, column=0):
                widget.destroy()
        LoginScreen(self.master)
        return
    
    def update_process(self):
        
        self.status_text.set("Downloading update...")
        temp_dir = os.path.join(self.kicad_library_dir, 'temp')
        if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
        if sys.version_info[0] == 3:
            with urllib.request.urlopen('https://snapeda.s3.amazonaws.com/plugins/kicad/SnapEDA-KiCad-Plugin.zip') as response, open(os.path.join(temp_dir, 'SnapEDA-KiCad-Plugin.zip'), 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        else:
            download_contents = urllib2.urlopen('https://snapeda.s3.amazonaws.com/plugins/kicad/SnapEDA-KiCad-Plugin.zip')
            with open(os.path.join(temp_dir, 'SnapEDA-KiCad-Plugin.zip'), "wb") as f:
                shutil.copyfileobj(download_contents, f)

        self.status_text.set("Extracting package...")
        
        with zipfile.ZipFile(os.path.join(temp_dir, 'SnapEDA-KiCad-Plugin.zip')) as zf:
            zf.extractall(temp_dir)

        self.status_text.set("Copying files...")
        
        for file in os.listdir(temp_dir):
            if file.endswith(".py"):
                copyfile(os.path.join(temp_dir, file), os.path.join(os.path.dirname(os.path.realpath(__file__)), file))
        
        shutil.rmtree(temp_dir)

        self.status_text.set("Update complete.")

        self.header_text.set("UPDATE COMPLETE")
        self.subheader_text.set("Update successful. Please restart SnapEDA, refresh the plugins, then open SnapEDA.")
        self.status_text.set("")


    def update_callback(self, event):
    
        try:
            is_admin = os.getuid() == 0
        except AttributeError:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

        if not is_admin:
            if self.is_windows:
                tkMessageBox.showwarning("Update", "Please restart KiCAD as administrator, then update again.")
                return
            # else:
            #     tkMessageBox.showwarning("Update", "If you are running on Linux, go to .kicad_plugins, on a terminal, run `sudo snapeda_plugins.py standalone` and update from there.")
            # return
        
        self.update_container = tk.Frame(self.parent, bg="#ff761a")
        self.update_container.grid(row=0, column=0, sticky="NEWS")
        self.update_container.grid_columnconfigure(0, weight=1)
        for i in range(4):
            self.update_container.grid_rowconfigure(i, weight=1, uniform="foo")

        self.header_container = tk.Frame(self.update_container, bg="#ff761a")
        self.header_container.grid(row=1, column=0, columnspan=1, sticky="NEWS")
        self.header_container.grid_columnconfigure(0, weight=1)
        for i in range(3):
            self.header_container.grid_rowconfigure(i, weight=1, uniform="foo")

        self.header_text = tk.StringVar()
        self.header_text.set("UPDATING...")
        self.header_label = tk.Label(self.header_container, bg="#ff761a", fg="white", textvariable=self.header_text, justify=tk.CENTER, font=("Open Sans", "18", "bold"))
        self.header_label.grid(row=0, column=0, columnspan=1, sticky="NEWS")

        self.subheader_text = tk.StringVar()
        self.subheader_text.set("This may take a while, about 3-5 minutes. Mind to have a coffee break?")
        self.subheader_label = tk.Label(self.header_container, textvariable=self.subheader_text, fg="white", bg="#ff761a", font=("Open Sans", "13"))
        self.subheader_label.grid(row=1, column=0, sticky="NEW")

        self.status_text = tk.StringVar()
        self.status_text.set("Starting update...")
        self.status_label = tk.Label(self.header_container, textvariable=self.status_text, fg="white", bg="#ff761a", font=("Open Sans", "13", "italic"))
        self.status_label.grid(row=2, column=0, sticky="NEW")
      
        self.update_thread = threading.Thread(target=self.update_process)
        self.update_thread.setDaemon(True)
        self.update_thread.start()

    def help_me_callback(self, event):
        if(tkMessageBox.askyesno("Help Me", "For any concerns or suggestions in using this plugin, kindly contact us at info@snapeda.com. Do you wish to connect with us now?")):
            webbrowser.open('mailto:?to=info@snapeda.com', new=1)

    def next_page(self, event):
        if self.current_page < self.max_page:
            self.current_page += 1
            self.search_data(event, current_page=self.current_page)

    def prev_page(self, event):
        if self.current_page > 1:
            self.current_page -= 1
            self.search_data(event, current_page=self.current_page)

    # Runs when any item in the listview is clicked
    def on_tree_select(self, event, index=None):
        # self.search_button.config(state="disabled", text="Loading")
        # self.next_button.config(state="disabled")
        # self.prev_button.config(state="disabled")
        # self.treeview.config(selectmode="none")
        if not self.is_loading:
            self.is_loading = True
            # self.details_frame.lower()
            # self.load_gif.lift()
            # self.load_after = self.parent.after(0, self.update_load, 0)
            self.get_component_thread = threading.Thread(target=self.get_component, args=(event, index))
            self.get_component_thread.start()
            # self.top_frame.grid_forget()
            # self.load_gif.config(height=self.top_frame.winfo_height() - 5)

    def get_component(self, event, index):
        # Find which item is selected
        # item_iid = self.treeview.selection()[0]
        # selected_name = str(self.treeview.item(item_iid)['values'][0])
        # Find selected item's json
        # selected_json = ""
        # for result in self.data["results"]:
        #     if str(result["part_number"]) == selected_name:
        #         selected_json = result
        # for widget in self.parent.grid_slaves(row=1, column=0):
        #     widget.destroy()
        if not self.side_opened:
            for names in self.manufacturer_names:
                names.config(fg="#999999")
            for label in self.manufacturer_labels:
                label.grid_forget()
            for label in self.available_labels:
                label.grid_forget()
            self.canvas_frame.grid_columnconfigure(0, weight=0)
            self.canvas_frame.grid_columnconfigure(1, weight=2)
            self.canvas_frame.grid_columnconfigure(2, weight=2)
            self.canvas_frame.grid_columnconfigure(3, weight=0)
            self.canvas_frame.grid_columnconfigure(4, weight=2)
            self.canvas_frame.grid_columnconfigure(5, weight=1)
            self.canvas_frame.grid_columnconfigure(6, weight=3)

        self.side_opened = True
        for i in range(3):
            self.dual_frame.grid_columnconfigure(i, weight=1, uniform="foo")
        self.side_frame = tk.Frame(self.dual_frame, bg="white")
        self.side_frame.grid(row=0, column=2, columnspan=1, sticky="NEWS")
        self.side_frame.grid_columnconfigure(0, weight=1)
        self.side_frame.grid_rowconfigure(0, weight=1)

        self.details_frame = tk.Frame(self.side_frame, bg="#E1E1E1")
        self.details_frame.grid(row=0, column=0, sticky="NEWS", padx=(10, 0), pady=0)
        for i in range(7):
            self.details_frame.grid_rowconfigure(i, weight=1)
        self.details_frame.grid_columnconfigure(0, weight=1)

        self.load_gif = tk.Label(self.side_frame, bg='white')
        self.load_gif.grid(row=0, column=0, sticky="NEWS")
        self.load_gif.lower()

        self.side_header = tk.Frame(self.details_frame, bg="white")
        self.side_header.grid(row=0, column=0, rowspan=1, sticky="NEWS", padx=1, pady=(1, 1))
        self.side_header.grid_columnconfigure(0, weight=1)
        self.side_header.grid_columnconfigure(1, weight=1)
        self.side_header.grid_rowconfigure(0, weight=1)

        self.details_label = tk.Label(self.side_header, bg="white", text="Details", font=("Open Sans", "8", "bold"))
        self.details_label.grid(row=0, column=0, sticky="W", padx=(15, 0))

        selected_json = self.data["results"][index]

        self.part_number = selected_json["part_number"]
        self.has_symbol = selected_json["has_symbol"]
        self.has_footprint = selected_json["has_footprint"]
        self.has_datasheet = selected_json["has_datasheet"]
        self.uniqueid = selected_json["uniqueid"]
        self.manufacturer = selected_json["manufacturer"]
        self.manufacturer_url = selected_json["organization_image_100_20"]

        try:
            organization_image = self.organization_images[index + 1]
            organization_view = tk.Label(self.side_header, image=organization_image, bg="white", font=("Open Sans", 9))
            organization_view.grid(row=0, column=1, sticky="E", padx=(0, 5))
        except KeyError:
            print("No Organization Image")
            organization_view = tk.Label(self.side_header, text=self.manufacturer, bg="white", font=("Open Sans", 9))
            organization_view.grid(row=0, column=1, sticky="E", padx=(0, 5))

        # powered_image = self.resize(self.powered_image, 167, 37)
        # self.parent.images.append(powered_image)
        # self.side_powered = tk.Label(self.side_header, image=powered_image, bg="white")
        # self.side_powered.grid(row=0, column=0, sticky="E", padx=(0, 5))

        # self.part_details = tk.Frame(self.details_frame, bg="white")
        # self.part_details.grid(row=1, column=0, rowspan=3, sticky="NEWS", padx=1, pady=(1, 0))
        # for i in range(3):
        #     self.part_details.grid_rowconfigure(i, weight=1)
        # self.part_details.grid_columnconfigure(0, weight=1)
        # self.side_buttons = tk.Frame(self.part_details, bg="white")
        # self.side_buttons.grid(row=2, column=0, sticky="NEWS", padx=(5, 0))
        # self.side_buttons.grid_rowconfigure(0, weight=1)
        # self.side_buttons.grid_columnconfigure(0, weight=1, uniform="foo")
        # self.side_buttons.grid_columnconfigure(1, weight=1, uniform="foo")
        # # self.side_buttons.grid_columnconfigure(2, weight=1, uniform="foo")
        # self.symbol_frame = tk.Frame(self.details_frame, bg="white")
        # self.symbol_frame.grid(row=4, column=0, rowspan=3, sticky="NEWS", padx=1, pady=(0, 1))
        # self.symbol_frame.grid_columnconfigure(0, weight=1)
        # self.symbol_frame.grid_rowconfigure(0, weight=1)

        # self.parent.after_cancel(self.load_after)

        # for widget in self.details_frame.winfo_children():
        #     widget.destroy()
        self.part_details = tk.Frame(self.details_frame, bg="white")
        self.part_details.grid(row=1, column=0, rowspan=2, sticky="NEWS", padx=1, pady=(0, 0))
        self.part_details.grid_columnconfigure(0, weight=1)
        self.side_buttons = tk.Frame(self.part_details, bg="white")
        self.side_buttons.grid(row=2, column=0, padx=(15, 15), sticky="NEWS")
        self.side_buttons.grid_rowconfigure(0, weight=1)
        self.side_buttons.grid_columnconfigure(0, weight=1, uniform="foo")
        self.side_buttons.grid_columnconfigure(1, weight=1, uniform="foo")
        # self.side_buttons.grid_columnconfigure(2, weight=1, uniform="foo")
        self.symbol_frame = tk.Frame(self.details_frame, bg="white")
        self.symbol_frame.grid(row=3, column=0, rowspan=4, sticky="NEWS", padx=1, pady=(0, 1))
        self.symbol_frame.grid_columnconfigure(0, weight=1, uniform="foo")
        self.symbol_frame.grid_rowconfigure(0, weight=1, uniform="foo")
        self.symbol_frame.grid_rowconfigure(1, weight=1, uniform="foo")

        self.side_part_number = tk.Label(self.part_details, bg="white", fg="#FF761A", font=("Open Sans", 12), text=selected_json["part_number"])
        self.side_part_number.grid(row=0, column=0, sticky="NWS", padx=(15, 0), pady=(15, 0))
        # self.side_manufacturer = tk.Label(self.part_details, bg="white", text=selected_json["manufacturer"])
        # self.side_manufacturer.grid(row=1, column=0, sticky="NWS", padx=(1, 1))
        description_message = tk.Message(
            self.part_details, bg="white", text=selected_json["short_description"], font=(
                "Open Sans", 9), cursor="hand2", justify=tk.LEFT)
        description_message.grid(row=1, column=0, sticky="NWS", pady=(0, 10), padx=(10, 10))
        # datasheet_button_im = tk.PhotoImage(file=self.datasheet_button_dir)
        # datasheet_button_image = self.resize(datasheet_button_im, 120, 30)
        # self.parent.images.append(datasheet_button_image)
        download_button_im = tk.PhotoImage(file=self.download_button_dir)
        download_button_image = self.resize(download_button_im, 90, 24)
        self.parent.images.append(download_button_image)
        view_button_im = tk.PhotoImage(file=self.view_button_dir)
        view_button_image = self.resize(view_button_im, 148, 39)
        self.parent.images.append(view_button_image)

        # self.datasheet_button = tk.Label(self.side_buttons, bg="white", fg="#304E70", cursor="hand2", image=datasheet_button_image)
        # self.datasheet_button.grid(row=0, column=0, sticky="W")
        
        self.is_downloading = False
        # self.download_button.bind("<Button-1>", self.download_component)
        # self.view_button = tk.Label(self.side_buttons, bg="white", fg="#304E70", cursor="hand2", image=view_button_image)
        # self.view_button.grid(row=0, column=1, sticky="W")
        # self.view_button.bind("<Button-1>", lambda event, url=selected_json["_links"]["self"]["href"]: self.view_on_snapeda(url))
        tk.Label(self.side_buttons, bg="#ff761a").grid(row=0, column=0, sticky="EW", ipadx=26, ipady=7, padx=(0, 16))
        self.download_button = tk.Label(self.side_buttons, bg="#ff761a", fg="white", cursor="hand2", text="Download", font=("Open Sans", 9))
        # Set padx to maintain separation
        self.download_button.grid(row=0, column=0, sticky="EW", padx=(1, 15), ipady=6, ipadx=10)
        # self.download_button = tk.Button(self.side_buttons, cursor="hand2", bg="#FF761B", fg="white", text="Download", borderwidth=0, highlightthickness=0)
        # self.download_button.grid(row=0, column=0, sticky="W")
        self.download_button.bind("<Button-1>", self.download_component)
        
        # self.view_button = tk.Button(self.side_buttons, cursor="hand2", bg="white", fg="#FF761B", text="View on SnapEDA",
        #                              borderwidth=0, highlightthickness=1, highlightbackground="#FF761B")
        # self.view_button.grid(row=0, column=1, sticky="W", padx=(20, 0))
        tk.Label(self.side_buttons, bg="#ff761a").grid(row=0, column=1, sticky="EW", ipady=7, ipadx=72)
        self.view_button = tk.Label(self.side_buttons, fg="#ff761a", bg="white", cursor="hand2", text="View on SnapEDA", font=("Open Sans", 9))
        self.view_button.grid(row=0, column=1, sticky="EW", padx=(1, 1), ipady=6, ipadx=10)
        self.view_button.bind("<Button-1>", lambda event, url=selected_json["_links"]["self"]["href"]: self.view_on_snapeda(url))
        # self.side_table = tk.Frame(self.details_frame, bg="white")
        # self.side_table.grid(row=4, column=0, rowspan=3, sticky="NEWS", padx=5, pady=(5, 0))
        # for i in range(5):
        #     self.side_table.grid_rowconfigure(i, weight=1)
        # self.side_table.grid_columnconfigure(0, weight=1)

        # table_data = {
        #     "Current Rating": "1A",
        #     "Frequency": "200kHz",
        #     "Inductance": "80uH",
        #     "Isolation Voltage": "1.5kV",
        #     "Turns Ratio": "5:1",
        # }

        # for index, (key, data) in enumerate(table_data.items()):
        #     if index % 2 == 0:
        #         bg = "#E1E1E1"
        #     else:
        #         bg = "white"
        #     frame = tk.Frame(self.side_table, bg=bg)
        #     frame.grid(row=index, column=0, sticky="NEWS")
        #     frame.grid_columnconfigure(0, weight=1, uniform="foo")
        #     frame.grid_columnconfigure(1, weight=1, uniform="foo")
        #     frame.grid_rowconfigure(1, weight=1)
        #     tk.Label(frame, bg=bg, text=key).grid(row=0, column=0, sticky="W")
        #     tk.Label(frame, bg=bg, text=data).grid(row=0, column=1, sticky="W")
        try:
            symbol_im_path = self.download_image(selected_json["models"][0]["symbol_medium"]["url"])
            symbol_im = tk.PhotoImage(file=symbol_im_path)
            symbol_image = self.resize(symbol_im, 210, 210)
            self.parent.images.append(symbol_image)
            symbol_view = tk.Label(self.symbol_frame, bg="white", image=symbol_image)
            symbol_view.grid(row=0, column=0, sticky="NEWS")
        except KeyError:
            symbol_view = tk.Label(self.symbol_frame, bg="white", text="No Symbol")
            symbol_view.grid(row=0, column=0)
            print("No symbol")
        try:
            package_im_path = self.download_image(selected_json["models"][0]["package_medium"]["url"])
            package_im = tk.PhotoImage(file=package_im_path)
            package_image = self.resize(package_im, 210, 210)
            self.parent.images.append(package_image)
            package_view = tk.Label(self.symbol_frame, bg="white", image=package_image)
            package_view.grid(row=1, column=0, sticky="NEWS")
        except KeyError:
            package_view = tk.Label(self.symbol_frame, bg="white", text="No Package")
            package_view.grid(row=1, column=0)
            print("No package")
        self.is_loading = False
        # self.load_gif.lower()
        # self.load_gif.config(image="")
        self.details_frame.lift()

    def canvas_frame_wh(self, event):
        canvas_width = self.canvas.winfo_width()
        print("break3")
        self.canvas.itemconfigure("inner_frame", width=canvas_width - 4)

    def initialize_user_interface(self):
        if self.is_windows:
            self.parent.iconbitmap(self.icon_bitmap_dir)
        self.parent.title("SnapEDA v" + self.parent.version)
        self.parent.geometry("1150x828")
        self.parent.minsize(width=1150, height=828)
        self.light_gray = "#FAFAFA"
        self.medium_gray = "#E1E1E1"
        self.dark_gray = "#696969"
        self.parent.grid_columnconfigure(0, weight=1, uniform="foo")
        self.parent.grid_rowconfigure(0, weight=1, uniform="foo")
        self.parent_container = tk.Frame(self.parent, bg=self.dark_gray)
        self.parent_container.grid(row=0, column=0, sticky="NEWS")
        for i in range(6):
            self.parent_container.grid_columnconfigure(i, weight=1, uniform="foo")
        self.parent_container.grid_rowconfigure(0, weight=1)
        self.main_frame = tk.Frame(self.parent_container, bg="white")
        self.main_frame.grid(row=0, column=0, columnspan=6, sticky="NEWS")
        # for i in range(5):
        #     # if i < 13:
        #     #     self.main_frame.grid_rowconfigure(i, weight=1, uniform="foo")
        self.main_frame.grid_columnconfigure(0, weight=1, uniform="foo")
        for i in range(6):
            self.main_frame.grid_rowconfigure(i, weight=1, uniform="foo")
        self.parent.images = []
        self.parent.default_images = []
        self.current_page = 1
        self.max_page = 1
        self.top_wh = 75
        self.pages = []
        self.side_opened = False

        # self.buttons_frame = tk.Frame(self.main_frame, bg=self.dark_gray)
        # self.buttons_frame.grid(row=0, column=0, columnspan=1, sticky="W", padx=(19, 0))
        # for i in range(3):
        #     self.buttons_frame.grid_columnconfigure(i, weight=1, uniform="foo")
        # self.buttons_frame.grid_rowconfigure(0, weight=1)

        # filter_button_im = tk.PhotoImage(file=self.filter_button_image_dir)
        # filter_button_image = self.resize(filter_button_im, 55, 55)
        # self.parent.images.append(filter_button_image)

        # self.filter_button = tk.Label(self.buttons_frame,
        #                             text="",
        #                             cursor="hand2",
        #                             bg=self.dark_gray,
        #                             image=filter_button_image)
        # # self.filter_button.bind("<Button-1>", self.check_login_thread)
        # self.filter_button.grid(row=0, column=0, padx=(0, 5))

        # settings_button_im = tk.PhotoImage(file=self.settings_button_image_dir)
        # settings_button_image = self.resize(settings_button_im, 55, 55)
        # self.parent.images.append(settings_button_image)

        # self.settings_button = tk.Label(self.buttons_frame,
        #                             text="",
        #                             cursor="hand2",
        #                             bg=self.dark_gray,
        #                             image=settings_button_image)
        # # self.settings_button.bind("<Button-1>", self.check_login_thread)
        # self.settings_button.grid(row=0, column=1, padx=(0, 5))

        # about_button_im = tk.PhotoImage(file=self.about_button_image_dir)
        # about_button_image = self.resize(about_button_im, 55, 55)
        # self.parent.images.append(about_button_image)

        # self.about_button = tk.Label(self.buttons_frame,
        #                             text="",
        #                             cursor="hand2",
        #                             bg=self.dark_gray,
        #                             image=about_button_image)
        # # self.about_button.bind("<Button-1>", self.check_login_thread)
        # self.about_button.grid(row=0, column=2, padx=(0, 5))

        # passive_components_im = tk.PhotoImage(file=self.passive_components_image_dir)
        # passive_components_image = self.resize(passive_components_im, 120, 25)
        # self.parent.images.append(passive_components_image)
        # self.dropdown_menu = tk.Label(self.main_frame, bg=self.dark_gray, text="", cursor="hand2", image=passive_components_image)
        # self.dropdown_menu.grid(row=0, column=1, columnspan=1, sticky="W", padx=(20, 0))

        self.search_frame = tk.Frame(self.main_frame, bg="white")
        self.search_frame.grid(row=0, column=0, columnspan=1, sticky="EW", padx=(18, 0))
        for i in range(3):
            self.search_frame.grid_columnconfigure(i + 1, weight=1, uniform="foo")
        self.search_frame.grid_rowconfigure(0, weight=0)

        # all_button_im = tk.PhotoImage(file=self.all_button_image_dir)
        # all_button_image = self.resize(all_button_im, 73, 55)
        # self.parent.images.append(all_button_image)
        # self.all_button = tk.Label(self.search_frame, bg="white", text="", cursor="hand2", image=all_button_image)
        # self.all_button.grid(row=0, column=0, sticky="W")

        search_entry_frame = tk.Frame(self.search_frame, bg="white")
        search_entry_frame.grid(row=0, column=1, columnspan=1, sticky="NEWS", pady=2, padx=(0, 0))
        search_entry_frame.grid_columnconfigure(0, weight=1)
        search_entry_frame.grid_rowconfigure(0, weight=1)

        # tk.Frame(search_entry_frame, bg="#E1E1E1").grid(row=0, column=0, sticky="NEWS", padx=(0, 0), pady=(0, 0))
        # tk.Frame(search_entry_frame, bg="white").grid(row=0, column=0, sticky="NEWS", padx=(1, 0), pady=(0, 1))
        
        tk.Frame(search_entry_frame, bg="#E1E1E1").grid(row=0, column=0, sticky="NEWS", padx=(0, 0), pady=(0, 0))
        tk.Frame(search_entry_frame, bg="white").grid(row=0, column=0, sticky="NEWS", padx=(1, 0), pady=(1, 1))

        self.search_entry = tk.Entry(search_entry_frame, fg="#696969", bg="white", font=("Open Sans", 9), borderwidth=0, highlightthickness=0)
        self.search_entry.insert(0, self.parent.search_datum)
        self.search_entry.grid(row=0, column=0, sticky="NEWS", padx=(25, 0), pady=(1, 1))

        search_button_im = tk.PhotoImage(file=self.search_button_image_dir)
        search_button_image = self.resize(search_button_im, 73, 55)
        self.parent.images.append(search_button_image)
        self.search_button = tk.Label(self.search_frame, bg="white", text="", cursor="hand2", image=search_button_image)
        self.is_searching = False
        self.search_button.bind("<Button-1>", self.search_data)
        self.search_entry.bind('<Return>', self.search_data)
        self.search_button.grid(row=0, column=2, sticky="W")

         # Add how-it-works button
        self.menu_container = tk.Frame(self.search_frame, bg="white")
        self.menu_container.grid(row=0, column=3, columnspan=1, sticky="E", padx=(0, 18))
        self.menu_container.grid_rowconfigure(0, weight=1)
        
        # self.update_status = tk.Label(self.menu_container, fg="#FF761B", bg="white", text="UPDATE STATUS", cursor="hand2", font=("Open Sans", "8", "bold", "underline"))
        # self.update_status.grid(row=0, column=0, padx=(0, 0))

        self.how_it_works_button = tk.Label(self.menu_container, fg="#FF761B", bg="white", text="How it works", cursor="hand2", font=("Open Sans", "8", "bold", "underline"))
        self.how_it_works_button.grid(row=0, column=0, padx=(0, 15), sticky="W")
        self.how_it_works_button.bind("<Button-1>", self.how_it_works_callback)

        self.logout_button = tk.Label(self.menu_container, fg="#FF761B", bg="white", text="Logout", cursor="hand2", font=("Open Sans", "8", "bold", "underline"))
        self.logout_button.grid(row=0, column=1, padx=(0, 15))
        self.logout_button.bind("<Button-1>", self.logout_callback)

        self.update_button = tk.Label(self.menu_container, fg="#FF761B", bg="white", text="Update", cursor="hand2", font=("Open Sans", "8", "bold", "underline"))
        self.update_button.grid(row=0, column=2, padx=(0, 15), sticky="W")
        self.update_button.bind("<Button-1>", self.update_callback)

        self.help_me_button = tk.Label(self.menu_container, fg="#FF761B", bg="white", text="Help Me", cursor="hand2", font=("Open Sans", "8", "bold", "underline"))
        self.help_me_button.grid(row=0, column=3, padx=(0, 0), sticky="W")
        self.help_me_button.bind("<Button-1>", self.help_me_callback)

        self.table_frame = tk.Frame(self.main_frame, bg="white")
        self.table_frame.grid(row=1, column=0, rowspan=5, columnspan=1, padx=19, pady=(0, 13), sticky="NEWS")
        # 2 2 2 3 2 1 1 1 1 1 1 1 2

        # for i in range(20):
        #     if i < 7:
        #         self.table_frame.grid_rowconfigure(i, weight=1, uniform="foo")
        #     self.table_frame.grid_columnconfigure(i, weight=1, uniform="foo")
        for i in range(7):
            self.table_frame.grid_rowconfigure(i, weight=1, uniform="foo")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(1, weight=1)

        self.dual_frame = tk.Frame(self.table_frame, bg="#E1E1E1")
        self.dual_frame.grid(row=0, column=0, columnspan=2, rowspan=6, sticky="NEWS")
        self.dual_frame.grid_rowconfigure(0, weight=1)
        for i in range(2):
            self.dual_frame.grid_columnconfigure(i, weight=1, uniform="foo")
        self.results_frame = tk.Frame(self.dual_frame, bg="white")
        self.results_frame.grid(row=0, column=0, columnspan=2, sticky="NEWS", pady=(0, 1))
        self.results_frame.grid_columnconfigure(0, weight=1)
        # self.results_frame.grid_columnconfigure(1, weight=1)
        self.results_frame.grid_rowconfigure(0, weight=1)
        self.results_frame.update()
        self.canvas = tk.Canvas(self.results_frame, bg="white")
        self.canvas.grid(row=0, column=0, sticky="NEWS")
        # style = ttk.Style()
        # style.theme_use('clam')
        # print(style.element_options("Vertical.TScrollbar.thumb"))
        # style.configure("Vertical.TScrollbar", gripcount=0,
        #         background="Green", darkcolor="DarkGreen", lightcolor="LightGreen",
        #         troughcolor="gray", bordercolor="blue", arrowcolor="white")
        self.vsb = tk.Scrollbar(self.results_frame, orient="vertical", command=self.canvas.yview)
        self.vsb.grid(row=0, column=1, sticky='NS')
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.configure(width=self.results_frame.winfo_width() / 16)

        self.canvas_frame = tk.Frame(self.canvas, bg="white")
        # self.canvas_frame.grid(row=0, column=0, sticky="NEWS")
        # for i in range(14):
        #     self.canvas_frame.grid_rowconfigure(i, weight=1, uniform="foo")
        #     self.canvas_frame.grid_columnconfigure(i, weight=1, uniform="foo")

        self.canvas.create_window((0, 0), window=self.canvas_frame, anchor='nw', tag="inner_frame")
        self.canvas.update_idletasks()
        self.canvas_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        # self.table_header.update_idletasks()
        # self.canvas_frame.config(width=self.canvas.winfo_width(), height=self.table_header.winfo_height())
        self.canvas.bind('<Configure>', self.canvas_frame_wh)

        # Set the canvas scrolling region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.pages_frame = tk.Frame(self.table_frame, bg="#E1E1E1")
        self.pages_frame.grid(row=6, column=0, sticky="W", padx=(0, 0))

        # self.frames = [tk.PhotoImage(file=os.path.join(self.appdata_dir, "SnapEDAloading.gif"), format='gif -index %i' % (i)) for i in range(153)]
        self.frames = [tk.PhotoImage(file=os.path.join(self.loading_image_dir), format='gif -index %i' % (i)) for i in range(31)]
        self.search_gif = tk.Label(self.results_frame, bg='white')
        self.search_gif.grid(row=0, column=0, sticky="NEWS")
        self.search_gif.lower()

        self.vsb.update_idletasks()
        powered_im = tk.PhotoImage(file=self.powered_image_dir)
        self.powered_image = self.resize(powered_im, 150, 33)
        self.parent.images.append(self.powered_image)
        self.snapeda_powered = tk.Label(self.table_frame, image=self.powered_image, bg="white")
        self.snapeda_powered.grid(row=6, column=1, sticky="E", padx=(0, self.vsb.winfo_width()))
        self.search_data(self)

    def resize(self, image, w_new, h_new):
        '''
        resize a pil_image object so it will fit into
        a box of size w_box times h_box, but retain aspect ratio
        '''
        if sys.version_info[0] == 3:
            width = image.width()
            height = image.height()
            min_wh = max(width, height)
            min_wh_new = max(w_new, h_new)
            if min_wh > min_wh_new:
                return image.subsample(int(min_wh / min_wh_new))
            else:
                return image.zoom(int(min_wh_new / min_wh))
        else:
            width = image.width()
            height = image.height()
            min_wh = max(width, height)
            min_wh_new = max(w_new, h_new)
            if min_wh > min_wh_new:
                return image.subsample(min_wh / min_wh_new)
            else:
                return image.zoom(min_wh_new / min_wh)

    def image_return(self, path):
        return path

    def download_image(self, url):
        # TODO: convert jpg to png without PIL
        image_name = url[url.rfind('/') + 1:]
        image_path = os.path.join(self.appdata_dir, image_name)
        png_path = image_path[:-3] + "png"
        timer = threading.Timer(2, self.image_return, args=(png_path,))
        timer.start()
        if not os.path.exists(png_path) and not self.is_mac:
            if self.is_windows:
                convert_path = os.path.join(os.path.dirname(__file__), "imagemagick", "convert")
                subprocess.check_call([convert_path, url.replace("https", "http"), png_path], shell=True)
            else:
                subprocess.call("convert " + url.replace("https", "http") + " " + png_path, shell=True)
        if self.is_mac:
            if not os.path.exists(png_path):
                with open(image_path, "wb") as f:
                    if sys.version_info[0] == 3:
                        image_data = urllib.request.urlopen(url).read()
                    else:
                        image_data = urllib2.urlopen(url).read()
                    f.write(image_data)
                    f.close()
                    subprocess.check_call(["sips", "-s", "format", "gif", "%s" % image_path, "--out", "%s" % png_path], shell=True)
        return png_path

    def update_search(self, ind):
        frame = self.frames[ind]
        ind += 1
        if ind == 30:
            ind = 0
        self.search_gif.config(image=frame)
        self.search_after = self.parent.after(30, self.update_search, ind)

    def update_load(self, ind):
        frame = self.frames[ind]
        ind += 1
        if ind == 30:
            ind = 0
        self.load_gif.config(image=frame)
        self.load_after = self.parent.after(30, self.update_load, ind)

    def mouse_wheel_callback(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # Runs when search button clicked
    def search_data(self, event, current_page=1):
        if not self.is_searching and len(self.search_entry.get()) > 0:
            self.is_searching = True
            self.search_button.config(state="disabled")
            # self.next_button.config(state="disabled")
            # self.prev_button.config(state="disabled")
            print("searched page: %d" % current_page)
            self.search_thread = threading.Thread(target=self.insert_data, kwargs={'current_page': current_page})
            self.search_thread.setDaemon(True)
            self.search_thread.start()
            self.table_frame.lower()
            self.pages_frame.destroy()
            self.search_gif.lift()
            self.search_after = self.parent.after(0, self.update_search, 0)

    def insert_data(self, current_page=1):
        """
        Insertion method.
        """
        # Get info.json username 
        info_dir = os.path.join(self.appdata_dir, "info.json")
        with open(info_dir) as json_file:
            data = json.load(json_file)
        username = data['username']

        self.token = "XbBKBKXLpgRYz96cfSaQDpToMmHFg6jH"
        header = {'User-Agent': "Kicad"}
        search_text = str(self.search_entry.get()).replace(" ", "%20")
        url = "https://www.snapeda.com/api/v1/parts/search?q=%s&token=%s&page=%s&ref=%s&username=%s" % (
            search_text, self.token, str(current_page), "kicad-plugin", username)
        print('Search URL: ' + url)
        try:
            if sys.version_info[0] == 3:
                req = urllib.request.Request(url, headers=header)
                contents = urllib.request.urlopen(req, timeout=5).read()
            else:
                req = urllib2.Request(url, headers=header)
                contents = urllib2.urlopen(req, timeout=5).read()
            self.data = json.loads(contents)
            if len(self.data["results"]) == 0:
                raise KeyError
        except:
        # except (urllib.error.HTTPError, KeyError):
            print("503 Error")
            self.canvas.yview_moveto(0)
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            self.search_button.config(state="normal")
            self.parent.after_cancel(self.search_after)
            self.is_searching = False
            self.search_gif.lower()
            self.search_gif.config(image="")
            self.current_page = current_page
            return
        self.page_names = []
        if self.max_page == 0:
            self.max_page = 1
            self.page_names.append(1)
            self.selected_index = 0
        else:
            for page in self.data["pages"]:
                self.page_names.append(int(page["name"]))
                if page["is_current"]:
                    self.selected_index = len(self.page_names) - 1
            if len(self.page_names) > 0:
                self.max_page = max(self.page_names)
            else:
                self.max_page = 0
        # self.page_number.config(text="%d of %d" % (self.current_page, self.max_page))
        # Create a row for each result
        self.canvas.yview_moveto(0)
        self.canvas_frame.grid_rowconfigure(0, weight=0)
        for i in range(19):
            self.canvas_frame.grid_rowconfigure(i + 1, weight=0)
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        # 2 2 1 4 1 2
        # for i in range(12):
        #     self.canvas_frame.grid_columnconfigure(i, weight=1, uniform="foo")
        for i in range(5):
            self.canvas_frame.grid_rowconfigure(i + 1, weight=1)
        for i in range(len(self.data["results"])):
            self.canvas_frame.grid_rowconfigure(i + 1, weight=1)
        self.i = 1
        self.manufacturer_labels = []
        self.available_labels = []
        self.canvas_frame.grid_columnconfigure(0, weight=2)
        self.canvas_frame.grid_columnconfigure(1, weight=2)
        self.canvas_frame.grid_columnconfigure(2, weight=2)
        self.canvas_frame.grid_columnconfigure(3, weight=2)
        self.canvas_frame.grid_columnconfigure(4, weight=2)
        self.canvas_frame.grid_columnconfigure(5, weight=1)
        self.canvas_frame.grid_columnconfigure(6, weight=3)
        self.canvas_frame.update()

        manufacturer_frame = tk.Frame(self.canvas_frame, bg="#E1E1E1")
        manufacturer_frame.grid_columnconfigure(0, weight=1)
        manufacturer_frame.grid_rowconfigure(0, weight=1)
        manufacturer_frame.grid(
            row=0,
            column=0,
            columnspan=1,
            sticky="NEWS",
            padx=(
                5,
                0))
        manufacturer_label = tk.Label(
            manufacturer_frame,
            fg="#FF761A",
            bg="white",
            font=(
                "Open Sans",
                9, "bold"),
            text="Manufacturer")
        manufacturer_label.grid(
            row=0,
            column=0,
            columnspan=1,
            sticky="NEWS",
            pady=(
                0,
                1))
        self.manufacturer_labels.append(manufacturer_frame)
        image_frame = tk.Frame(self.canvas_frame, bg="#E1E1E1")
        image_frame.grid_columnconfigure(0, weight=1)
        image_frame.grid_rowconfigure(0, weight=1)
        image_frame.grid(
            row=0,
            column=1,
            columnspan=1,
            sticky="NEWS",
            padx=(
                0,
                0))
        tk.Label(
            image_frame,
            fg="#FF761A",
            bg="white",
            height=4,
            font=(
                "Open Sans",
                9, "bold"),
            text="Image").grid(
            row=0,
            column=0,
            sticky="NEWS",
            pady=(
                0,
                1))
        part_frame = tk.Frame(self.canvas_frame, bg="#E1E1E1")
        part_frame.grid_columnconfigure(0, weight=1)
        part_frame.grid_rowconfigure(0, weight=1)
        part_frame.grid(
            row=0,
            column=2,
            columnspan=2,
            sticky="NEWS")
        tk.Label(
            part_frame,
            fg="#FF761A",
            bg="white",
            font=(
                "Open Sans",
                9,
                "bold"),
            text="Part").grid(
            row=0,
            column=0,
            columnspan=1,
            pady=(0, 1),
            sticky="NEWS")
        # available_frame = tk.Frame(self.canvas_frame, bg="#E1E1E1")
        # available_frame.grid_columnconfigure(0, weight=1)
        # available_frame.grid_rowconfigure(0, weight=1)
        # available_frame.grid(
        #     row=0,
        #     column=3,
        #     columnspan=1,
        #     sticky="NEWS")

        # available_label = tk.Label(
        #     available_frame,
        #     fg="#FF761A",
        #     bg="white",
        #     font=(
        #         "Open Sans",
        #         9, "bold"),
        #     text="Availability")
        # available_label.grid(
        #     row=0,
        #     column=0,
        #     columnspan=1,
        #     pady=(0, 1),
        #     sticky="NEWS")
        # self.available_labels.append(available_frame)
        description_frame = tk.Frame(self.canvas_frame, bg="#E1E1E1")
        description_frame.grid_columnconfigure(0, weight=1)
        description_frame.grid_rowconfigure(0, weight=1)
        description_frame.grid(
            row=0,
            column=4,
            columnspan=1,
            padx=(0, 0),
            sticky="NEWS")
        tk.Label(
            description_frame,
            fg="#FF761A",
            bg="white",
            anchor="w",
            font=(
                "Open Sans",
                9, "bold"),
            text="       Description").grid(
            row=0,
            column=0,
            columnspan=1,
            pady=(0, 1),
            sticky="NEWS")
        package_frame = tk.Frame(self.canvas_frame, bg="#E1E1E1")
        package_frame.grid_columnconfigure(0, weight=1)
        package_frame.grid_rowconfigure(0, weight=1)
        package_frame.grid(
            row=0,
            column=5,
            columnspan=1,
            sticky="NEWS")
        tk.Label(
            package_frame,
            fg="#FF761A",
            bg="white",
            font=(
                "Open Sans",
                9, "bold"),
            text="Package").grid(
            row=0,
            column=0,
            pady=(0, 1),
            sticky="NEWS")
        data_frame = tk.Frame(self.canvas_frame, bg="#E1E1E1")
        data_frame.grid_columnconfigure(0, weight=1) 
        data_frame.grid_rowconfigure(0, weight=1)
        data_frame.grid(
            row=0,
            column=6,
            columnspan=1,
            sticky="NEWS")
        tk.Label(
            data_frame,
            fg="#FF761A",
            bg="white",
            font=(
                "Open Sans",
                9, "bold"),
            text="Data Available").grid(
            row=0,
            column=0,
            pady=(0, 1),
            sticky="NEWS")
        # self.canvas.update()
        # import pdb; pdb.set_trace()
        self.results_frame.update()
        self.dual_frame.update()
        height = len(self.data["results"]) * self.results_frame.winfo_height() / 6
        self.canvas.update()
        # import pdb; pdb.set_trace()
        # self.vsb.destroy() REMOVE DUE TO EXCEPTION
        self.canvas.itemconfigure("inner_frame", height=400)
        self.canvas_frame.config(height=400)
        if len(self.data["results"]) > 6:
            self.canvas.itemconfigure("inner_frame", height=height)
            self.vsb = tk.Scrollbar(self.results_frame, orient="vertical", command=self.canvas.yview)
            self.canvas.bind_all("<MouseWheel>", self.mouse_wheel_callback)
            self.vsb.grid(row=0, column=1, sticky='NS')
            self.canvas.config(yscrollcommand=self.vsb.set)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            # height = 3 * self.results_frame.winfo_height()
        print("frame height %d" % self.results_frame.winfo_height())
        print("height %d" % height)
        # self.canvas.config(height=self.results_frame.winfo_height())
        print("searched")

        size = 15
        datahsheet_available_im = tk.PhotoImage(file=self.datasheet_available_dir)
        datahsheet_available_image = self.resize(datahsheet_available_im, size, size)
        self.parent.images.append(datahsheet_available_image)
        datahsheet_not_available_im = tk.PhotoImage(file=self.datasheet_not_available_dir)
        datahsheet_not_available_image = self.resize(datahsheet_not_available_im, size, size)
        self.parent.images.append(datahsheet_not_available_image)

        symbol_available_im = tk.PhotoImage(file=self.symbol_available_dir)
        symbol_available_image = self.resize(symbol_available_im, size, size)
        self.parent.images.append(symbol_available_image)
        symbol_not_available_im = tk.PhotoImage(file=self.symbol_not_available_dir)
        symbol_not_available_image = self.resize(symbol_not_available_im, size, size)
        self.parent.images.append(symbol_not_available_image)

        footprint_available_im = tk.PhotoImage(file=self.footprint_available_dir)
        footprint_available_image = self.resize(footprint_available_im, size, size)
        self.parent.images.append(footprint_available_image)
        footprint_not_available_im = tk.PhotoImage(file=self.footprint_not_available_dir)
        footprint_not_available_image = self.resize(footprint_not_available_im, size, size)
        self.parent.images.append(footprint_not_available_image)

        self.organization_images = {}
        self.manufacturer_names = []

        for result in self.data["results"]:
            if self.i % 2 == 0:
                bg = "white"
            else:
                # bg = "#E1E1E1"
                bg = "white"
            data_available = ""
            if any([
                    result["has_footprint"], result["has_datasheet"],
                    result["has_symbol"]
            ]):
                if result["has_footprint"]:
                    data_available += "Footprint, "
                if result["has_datasheet"]:
                    data_available += "Datasheet, "
                if result["has_symbol"]:
                    data_available += "Symbol"
                if data_available.endswith(", "):
                    data_available = data_available[:-2]
            else:
                data_available = "No Data"
            # Download manufacturer logo
            # try:
            #     image_path = self.download_image(image_url)
            #     im = tk.PhotoImage(file=image_path)
            #     image = self.resize(im, 50, 50)
            #     self.treeview.insert(
            #         '',
            #         "end",
            #         image=image,
            #         values=(result["part_number"], result["availability"],
            #                 result["average_price"], data_available))
            #     self.treeview.images.append(image)
            # except (urllib2.HTTPError, tk.TclError, subprocess.CalledProcessError):
            #     print("No Organization Image")
            #     self.treeview.insert(
            #         '',
            #         "end",
            #         text=result["manufacturer"],
            #         values=(result["part_number"], result["availability"],
            #                 result["average_price"], data_available))
            self.is_loading = False

            try:
                organization_image_url = result["organization_image_100_20"]
                image_path = self.download_image(organization_image_url)
                organization_im = tk.PhotoImage(file=image_path)
                organization_image = self.resize(organization_im, 75, 75)
                self.parent.images.append(organization_image)
                self.organization_images[self.i] = organization_image
                organization_view = tk.Label(self.canvas_frame, image=organization_image, bg=bg, font=("Open Sans", 9), cursor="hand2")
                organization_view.grid(row=self.i, column=0, columnspan=1, sticky="NESW")
                organization_view.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
            except BaseException:
                print("No Organization Image")
                self.organization_image = None
                organization_view = tk.Label(self.canvas_frame, text=result["manufacturer"], bg=bg, font=("Open Sans", 9), cursor="hand2")
                organization_view.grid(row=self.i, column=0, columnspan=1, sticky="NESW")
                organization_view.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
            self.manufacturer_labels.append(organization_view)

            try:
                symbol_image_url = result["coverart"][0]["url"]
                image_path = self.download_image(symbol_image_url)
                symbol_im = tk.PhotoImage(file=image_path)
                symbol_image = self.resize(symbol_im, 55, 55)
                self.parent.images.append(symbol_image)
                symbol_image_view = tk.Label(self.canvas_frame, bg=bg, image=symbol_image, cursor="hand2")
                symbol_image_view.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
                symbol_image_view.grid(row=self.i, column=1, columnspan=1, sticky="NESW")
            except BaseException:
                print("No Symbol Image")
                symbol_image_view = tk.Label(self.canvas_frame, bg=bg, cursor="hand2")
                symbol_image_view.grid(row=self.i, column=1, columnspan=1, sticky="NESW")
                symbol_image_view.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))

            part_frame = tk.Frame(self.canvas_frame, bg=bg, cursor="hand2")
            part_frame.grid_rowconfigure(0, weight=1, uniform="foo")
            part_frame.grid_rowconfigure(1, weight=1, uniform="foo")
            part_frame.grid_columnconfigure(0, weight=1, uniform="foo")
            part_frame.grid(row=self.i, column=2, columnspan=2, sticky="NEWS")
            part_frame.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
            part_number = tk.Label(
                part_frame,
                text=result["part_number"],
                fg="#304E70",
                bg=bg,
                font=(
                    "Open Sans",
                    9),
                cursor="hand2")
            part_number.grid(
                row=0,
                column=0,
                columnspan=2,
                sticky="S")
            part_number.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
            manufacturer_view = tk.Label(
                part_frame,
                text=result["manufacturer"],
                bg=bg,
                font=(
                    "Open Sans",
                    9),
                cursor="hand2")
            manufacturer_view.grid(
                row=1,
                column=0,
                sticky="N")
            manufacturer_view.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
            self.manufacturer_names.append(manufacturer_view)

            # availability_label = tk.Label(self.canvas_frame, bg=bg, text="?", font=("Open Sans", 9), cursor="hand2")
            # availability_label.grid(row=self.i, column=3, columnspan=1, sticky="NESW")
            # availability_label.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
            # self.available_labels.append(availability_label)

            description_frame = tk.Message(self.canvas_frame, bg=bg, cursor="hand2")
            description_frame.grid(row=self.i, column=4, columnspan=1, sticky="NEWS")
            description_frame.grid_columnconfigure(0, weight=1)
            description_frame.grid_rowconfigure(0, weight=1)
            description_frame.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
            short_description = result["short_description"]
            if len(short_description) > 85:
                short_description = short_description[:50] + "..."
            description_message = tk.Message(
                description_frame, bg=bg, text=short_description, font=(
                    "Open Sans", 8), cursor="hand2", justify=tk.LEFT)
            description_message.grid(row=0, column=0, sticky="W", padx=(15, 0))
            description_message.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
            if result["package"]["name"] == "--------":
                result["package"]["name"] = "N/A"
            package_label = tk.Label(self.canvas_frame, bg=bg, text=result["package"]["name"], font=("Open Sans", 9), cursor="hand2")
            package_label.grid(row=self.i, column=5, columnspan=1, sticky="NESW")
            package_label.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))

            data_available_frame = tk.Frame(self.canvas_frame, bg=bg)
            data_available_frame.grid_columnconfigure(0, weight=1, uniform="foo")
            data_available_frame.grid_columnconfigure(1, weight=1, uniform="foo")
            data_available_frame.grid_columnconfigure(2, weight=1, uniform="foo")
            data_available_frame.grid_rowconfigure(0, weight=1)
            data_available_frame.grid(row=self.i, column=6, columnspan=1, sticky="NESW")
            data_available_frame.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))

            if result["has_datasheet"]:
                datasheet_available = tk.Label(data_available_frame, bg=bg, image=datahsheet_available_image, cursor="hand2")
                datasheet_available.grid(row=0, column=0, sticky="E")
                datasheet_available.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
            else:
                datasheet_available = tk.Label(data_available_frame, bg=bg, image=datahsheet_not_available_image, cursor="hand2")
                datasheet_available.grid(row=0, column=0, sticky="E")
                datasheet_available.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
            if result["has_symbol"]:
                symbol_available = tk.Label(data_available_frame, bg=bg, image=symbol_available_image, cursor="hand2")
                symbol_available.grid(row=0, column=1, sticky="EW")
                symbol_available.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
            else:
                symbol_available = tk.Label(data_available_frame, bg=bg, image=symbol_not_available_image, cursor="hand2")
                symbol_available.grid(row=0, column=1, sticky="EW")
                symbol_available.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
            if result["has_footprint"]:
                footprint_available = tk.Label(data_available_frame, bg=bg, image=footprint_available_image, cursor="hand2")
                footprint_available.grid(row=0, column=2, sticky="W")
                footprint_available.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))
            else:
                footprint_available = tk.Label(data_available_frame, bg=bg, image=footprint_not_available_image, cursor="hand2")
                footprint_available.grid(row=0, column=2, sticky="W")
                footprint_available.bind("<Button-1>", lambda event, index=self.i - 1: self.on_tree_select(event, index))

            # Increment counter
            self.i = self.i + 1

        prev_bg_im = tk.PhotoImage(file=self.prev_bg_dir)
        prev_bg_image = self.resize(prev_bg_im, 55, 55)
        self.parent.images.append(prev_bg_image)
        next_bg_im = tk.PhotoImage(file=self.next_bg_dir)
        next_bg_image = self.resize(next_bg_im, 55, 55)
        self.parent.images.append(next_bg_image)
        self.pages_frame = tk.Frame(self.table_frame, bg="#E1E1E1") 
        self.pages_frame.grid(row=6, column=0, sticky="W", padx=(0, 0))
        self.pages_frame.grid_rowconfigure(0, weight=1)
        selected_page_im = tk.PhotoImage(file=self.selected_page_dir)
        selected_page_image = self.resize(selected_page_im, 25, 25)
        self.parent.images.append(selected_page_image)
        self.pages = []
        # self.selected_page_view = tk.Label(self.pages_frame, image=selected_page_image, bg="#C4C4C4")
        # self.selected_page_view.grid(row=0, column=self.selected_index + 2)
        for i in range(len(self.page_names)):
            # self.pages_frame.grid_columnconfigure(0, weight=1, uniform="foo")
            self.pages.append(
                tk.Label(
                    self.pages_frame,
                    bg="white",
                    text=str(
                        self.page_names[i]),
                    fg="#304E70",
                    cursor="hand2",
                    font=(
                        "Open Sans",
                        "10",
                        "bold"),
                    width=4,
                    height=2))
            self.pages[i].grid(row=0, column=i + 1, sticky="NEWS", pady=(1, 1))
            self.pages[i].bind("<Button-1>", lambda event, current_page=self.page_names[i]: self.search_data(event, current_page=current_page))

        if self.side_opened:
            for names in self.manufacturer_names:
                names.config(fg="#999999")
            for label in self.manufacturer_labels:
                label.grid_forget()
            for label in self.available_labels:
                label.grid_forget()
            self.canvas_frame.grid_columnconfigure(0, weight=0)
            self.canvas_frame.grid_columnconfigure(1, weight=2)
            self.canvas_frame.grid_columnconfigure(2, weight=2)
            self.canvas_frame.grid_columnconfigure(3, weight=0)
            self.canvas_frame.grid_columnconfigure(4, weight=2)
            self.canvas_frame.grid_columnconfigure(5, weight=1)
            self.canvas_frame.grid_columnconfigure(6, weight=3)

        self.pages[self.selected_index].config(bg="#FF761B", fg="white")
        self.prev_button = tk.Label(self.pages_frame, text="   < Prev   ", fg="#FF761B", bg="white", cursor="hand2", font=("Open Sans", "11", "bold"))
        self.prev_button.grid(row=0, column=0, sticky="NEWS", padx=(1, 0), pady=(1, 1))
        self.prev_button.bind("<Button-1>", self.prev_page)
        self.next_button = tk.Label(self.pages_frame, text="   Next >   ", fg="#FF761B", bg="white", cursor="hand2", font=("Open Sans", "11", "bold"))
        self.next_button.grid(row=0, column=len(self.page_names) + 1, sticky="NEWS", padx=(0, 1), pady=(1, 1))
        self.next_button.bind("<Button-1>", self.next_page)
        # tk.Label(self.pages_frame, bg="#C4C4C4", image=prev_bg_image).grid(row=0, column=0, sticky="NSE")
        # tk.Label(self.pages_frame, bg="#C4C4C4", image=next_bg_image).grid(row=0, column=len(self.page_names) + 3, sticky="NSW")
        self.search_button.config(state="normal")
        self.parent.after_cancel(self.search_after)
        self.is_searching = False
        self.search_gif.lower()
        self.search_gif.config(image="")
        # self.treeview.lift()
        # self.search_button.config(state="normal", text="Search")
        # self.next_button.config(state="normal")
        # self.prev_button.config(state="normal")

class WelcomeScreen(tk.Frame):
    '''
    Welcome Screen
    '''

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.is_mac = platform.mac_ver()[0] != ""
        self.is_windows = (os.name == 'nt')
        if self.is_windows:
            self.windata_dir = os.path.join(os.getenv('HOMEDRIVE'),
                                            os.getenv('HOMEPATH'),
                                            "SnapEDA Kicad Plugin")
            self.flip_table_dir = os.path.join(os.getenv('HOMEDRIVE'),
                                               os.getenv('HOMEPATH'),
                                               'AppData',
                                               'Roaming',
                                               'kicad',
                                               'fp-lib-table')
            self.appdata_dir = os.path.join(self.windata_dir, "App")
            if not os.path.exists(self.windata_dir):
                os.makedirs(self.windata_dir)
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir)
            self.kicad_library_dir = os.path.join(self.windata_dir, 'KiCad Library')
            snapeda_library_abs_dir = os.path.join(self.kicad_library_dir,
                                                   'SnapEDA Library.pretty')
            if not os.path.exists(self.kicad_library_dir):
                os.makedirs(self.kicad_library_dir)
            if not os.path.exists(snapeda_library_abs_dir):
                os.makedirs(snapeda_library_abs_dir)
        elif self.is_mac:
            self.macdata_dir = os.path.join(os.path.expanduser("~"), "Documents", "SnapEDA Kicad Plugin")
            self.appdata_dir = os.path.join(self.macdata_dir, "App")
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir)
        else:
            self.appdata_dir = os.path.join(self.dir_path, "assets")
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir)
            self.flip_table_dir = os.path.join(os.path.expanduser("~"),
                                               '.config',
                                               'kicad',
                                               'fp-lib-table')
            home_dir = os.path.expanduser("~")
            self.kicad_library_dir = os.path.join(home_dir, 'KiCad Library')
            snapeda_library_abs_dir = os.path.join(self.kicad_library_dir,
                                                   'SnapEDA Library.pretty')
            if not os.path.exists(self.kicad_library_dir):
                os.makedirs(self.kicad_library_dir)
            if not os.path.exists(snapeda_library_abs_dir):
                os.makedirs(snapeda_library_abs_dir)

        self.icon_bitmap_dir = os.path.join(self.appdata_dir, "32x32.ico")
        self.welcome_screen_001_dir = os.path.join(self.appdata_dir, "Mask+Group.png")
        self.welcome_screen_002_dir = os.path.join(self.appdata_dir, "icon1.bbe45f7648f7.png")
        self.welcome_screen_003_dir = os.path.join(self.appdata_dir, "ico_deadlines.8ba69c3f942a.png")
        self.welcome_screen_004_dir = os.path.join(self.appdata_dir, "icon2.924b03ebfccc.png")
        self.welcome_screen_005_dir = os.path.join(self.appdata_dir, "powered+by+snapEDA.png")
        self.welcome_screen_006_dir = os.path.join(self.appdata_dir, "snapeda-transparent.png")
        self.usb_type_c_button_dir = os.path.join(self.appdata_dir, "usb+type+c.png")
        self.microcontroller_button_dir = os.path.join(self.appdata_dir, "usb+microcontroller.png")

        self.initialize_user_interface()
    
    def resize(self, image, w_new, h_new):
        '''
        resize a pil_image object so it will fit into
        a box of size w_box times h_box, but retain aspect ratio
        '''
        if sys.version_info[0] == 3:
            width = image.width()
            height = image.height()
            min_wh = max(width, height)
            min_wh_new = max(w_new, h_new)
            if min_wh > min_wh_new:
                return image.subsample(int(min_wh / min_wh_new))
            else:
                return image.zoom(int(min_wh_new / min_wh))
        else:
            width = image.width()
            height = image.height()
            min_wh = max(width, height)
            min_wh_new = max(w_new, h_new)
            if min_wh > min_wh_new:
                return image.subsample(min_wh / min_wh_new)
            else:
                return image.zoom(min_wh_new / min_wh)

    def welcome_screen_search_callback(self, event):
        search_datum = self.search_bar.get()
        if len(search_datum) > 0:
            for i in range(5):
                for widget in self.parent.grid_slaves(row=i, column=0):
                    widget.destroy()
            self.parent.search_datum = search_datum
            # Welcome Screen
            self.search_bar.destroy()
            TableView(self.parent)

    def usb_type_c_button_callback(self, event):
        for i in range(5):
            for widget in self.parent.grid_slaves(row=i, column=0):
                widget.destroy()
        self.parent.search_datum = "usb type c"
        TableView(self.parent)

    def microcontroller_button_callback(self, event):
        for i in range(5):
            for widget in self.parent.grid_slaves(row=i, column=0):
                widget.destroy()
        self.parent.search_datum = "microcontroller"
        TableView(self.parent)

    def how_it_works_callback(self, event):
        instruction_text = '''
            Instructions:
            1. Search for the part, for example USB Type C.
            2. Choose from the results and select the part you like.
            3. Click Download.
            4. Click Place > Symbol or Place > Footprint.
            5. Find the downloaded part under SnapEDA Library.
            6. Use it in your design.
        '''
        tkMessageBox.showinfo("How it works", instruction_text)

    def update_process(self):
        
        self.status_text.set("Downloading update...")
        temp_dir = os.path.join(self.kicad_library_dir, 'temp')
        if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
        if sys.version_info[0] == 3:
            with urllib.request.urlopen('https://snapeda.s3.amazonaws.com/plugins/kicad/SnapEDA-KiCad-Plugin.zip') as response, open(os.path.join(temp_dir, 'SnapEDA-KiCad-Plugin.zip'), 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        else:
            download_contents = urllib2.urlopen('https://snapeda.s3.amazonaws.com/plugins/kicad/SnapEDA-KiCad-Plugin.zip')
            with open(os.path.join(temp_dir, 'SnapEDA-KiCad-Plugin.zip'), "wb") as f:
                shutil.copyfileobj(download_contents, f)

        self.status_text.set("Extracting package...")
        
        with zipfile.ZipFile(os.path.join(temp_dir, 'SnapEDA-KiCad-Plugin.zip')) as zf:
            zf.extractall(temp_dir)

        self.status_text.set("Copying files...")
        
        for file in os.listdir(temp_dir):
            if file.endswith(".py"):
                copyfile(os.path.join(temp_dir, file), os.path.join(os.path.dirname(os.path.realpath(__file__)), file))
        
        shutil.rmtree(temp_dir)

        self.status_text.set("Update complete.")

        self.header_text.set("UPDATE COMPLETE")
        self.subheader_text.set("Update successful. Please restart SnapEDA, refresh the plugins, then open SnapEDA.")
        self.status_text.set("")


    def update_callback(self, event):
    
        try:
            is_admin = os.getuid() == 0
        except AttributeError:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

        if not is_admin:
            if self.is_windows:
                tkMessageBox.showwarning("Update", "Please restart KiCAD as administrator, then update again.")
                return
            # else:
            #     tkMessageBox.showwarning("Update", "If you are running on Linux, go to .kicad_plugins, on a terminal, run `sudo snapeda_plugins.py standalone` and update from there.")
            # return
        
        self.update_container = tk.Frame(self.parent, bg="#ff761a")
        self.update_container.grid(row=0, column=0, sticky="NEWS")
        self.update_container.grid_columnconfigure(0, weight=1)
        for i in range(4):
            self.update_container.grid_rowconfigure(i, weight=1, uniform="foo")

        self.header_container = tk.Frame(self.update_container, bg="#ff761a")
        self.header_container.grid(row=1, column=0, columnspan=1, sticky="NEWS")
        self.header_container.grid_columnconfigure(0, weight=1)
        for i in range(3):
            self.header_container.grid_rowconfigure(i, weight=1, uniform="foo")

        self.header_text = tk.StringVar()
        self.header_text.set("UPDATING...")
        self.header_label = tk.Label(self.header_container, bg="#ff761a", fg="white", textvariable=self.header_text, justify=tk.CENTER, font=("Open Sans", "18", "bold"))
        self.header_label.grid(row=0, column=0, columnspan=1, sticky="NEWS")

        self.subheader_text = tk.StringVar()
        self.subheader_text.set("This may take a while, about 3-5 minutes. Mind to have a coffee break?")
        self.subheader_label = tk.Label(self.header_container, textvariable=self.subheader_text, fg="white", bg="#ff761a", font=("Open Sans", "13"))
        self.subheader_label.grid(row=1, column=0, sticky="NEW")

        self.status_text = tk.StringVar()
        self.status_text.set("Starting update...")
        self.status_label = tk.Label(self.header_container, textvariable=self.status_text, fg="white", bg="#ff761a", font=("Open Sans", "13", "italic"))
        self.status_label.grid(row=2, column=0, sticky="NEW")
      
        self.update_thread = threading.Thread(target=self.update_process)
        self.update_thread.setDaemon(True)
        self.update_thread.start()


    def help_me_callback(self, event):
        if(tkMessageBox.askyesno("Help Me", "For any concerns or suggestions in using this plugin, kindly contact us at info@snapeda.com. Do you wish to connect with us now?")):
            webbrowser.open('mailto:?to=info@snapeda.com', new=1)


    def initialize_user_interface(self):
        if self.is_windows:
            self.parent.iconbitmap(self.icon_bitmap_dir)
        self.parent.title("SnapEDA v" + self.parent.version)
        self.parent.geometry("1150x828")
        self.parent.minsize(width=1150, height=828)
        self.parent.grid_columnconfigure(0, weight=1, uniform="foo")
        self.parent.grid_rowconfigure(0, weight=1, uniform="foo")
        self.parent_container = tk.Frame(self.parent, bg="white")
        self.parent_container.grid(row=0, column=0, sticky="NEWS")
        self.parent_container.grid_columnconfigure(0, weight=1, uniform="foo")
        self.parent_container.grid_rowconfigure(0, weight=1)
        self.main_frame = tk.Frame(self.parent_container, bg="white")
        self.main_frame.grid(row=0, column=0, columnspan=1, sticky="NEWS")
        for i in range(3):
            self.main_frame.grid_columnconfigure(i, weight=1, uniform="foo")
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.left_frame = tk.Frame(self.main_frame, bg="white")
        self.left_frame.grid(row=0, column=0, columnspan=2, sticky="NEWS")
        self.left_frame.grid_columnconfigure(0, weight=1)
        for i in range(5):
            self.left_frame.grid_rowconfigure(i, weight=1, uniform="foo")

        self.right_frame = tk.Frame(self.main_frame, bg="white")
        self.right_frame.grid(row=0, column=2, columnspan=1, sticky="NEWS")
        self.right_frame.grid_columnconfigure(0, weight=1)
        for i in range(5):
            self.right_frame.grid_rowconfigure(i, weight=1, uniform="foo")

        # For the welcome screen numbers, refer to the numbers on the design.
        welcome_screen_006_img = tk.PhotoImage(file=os.path.join(self.welcome_screen_006_dir))
        self.navbar_container = tk.Frame(self.left_frame, bg="white")
        self.navbar_container.grid(row=0, column=0, sticky="NEWS")
        self.navbar_container.grid_columnconfigure(0, weight=1)
        for i in range(2):
            self.navbar_container.grid_rowconfigure(i, weight=1, uniform="foo")
        
        self.welcome_screen_006_image = self.resize(welcome_screen_006_img, 200, 59)
        self.welcome_screen_006_bg = tk.Label(self.navbar_container, image=self.welcome_screen_006_image, bg="white")
        self.welcome_screen_006_bg.grid(row=0, column=0, sticky="NW")

        self.navbar_menu_container = tk.Label(self.navbar_container, bg="white")
        self.navbar_menu_container.grid(row=1, column=0, sticky="NW")

        self.welcome_screen_header = tk.Label(self.left_frame, text="Welcome to SnapEDA", bg="white",  font=("Open Sans", "32", "bold"))
        self.welcome_screen_header.grid(row=1, column=0, rowspan=1, sticky="SEW")
        
        welcome_screen_001_img = tk.PhotoImage(file=os.path.join(self.welcome_screen_001_dir))
        self.welcome_screen_001_image = self.resize(welcome_screen_001_img, 297, 333)
        self.welcome_screen_001_bg = tk.Label(self.right_frame, image=self.welcome_screen_001_image, bg="white")
        self.welcome_screen_001_bg.grid(row=0, column=0, sticky="NE", rowspan=3)
        
        welcome_screen_005_img = tk.PhotoImage(file=os.path.join(self.welcome_screen_005_dir))
        self.welcome_screen_005_image = self.resize(welcome_screen_005_img, 267, 72)
        self.welcome_screen_005_bg = tk.Label(self.right_frame, image=self.welcome_screen_005_image, bg="white")
        self.welcome_screen_005_bg.grid(row=4, column=0, rowspan=1, sticky="SE")

        # Container for subheader and search input and examples
        self.welcome_container = tk.Frame(self.left_frame, bg="white")
        self.welcome_container.grid(row=2, column=0, rowspan=2, sticky="NEWS")
        self.welcome_container.grid_columnconfigure(0, weight=1)
        for i in range(5):
            self.welcome_container.grid_rowconfigure(i, weight=1, uniform="foo")

        self.welcome_screen_subheader = tk.Label(self.welcome_container, text="Let's make your your design a snap. Download ready-to-use\nPCB footprints, schematic symbols, and 3D models.", bg="white", font=("Open Sans", "12"), justify=tk.LEFT)
        self.welcome_screen_subheader.grid(row=0, column=0, rowspan=1, sticky="NEWS")

        self.welcome_screen_search_container = tk.Frame(self.welcome_container, bg="white")
        self.welcome_screen_search_container.grid(row=1, column=0, rowspan=1, sticky="NEW", padx=(40, 40), pady=(20, 0))
        self.welcome_screen_search_container.grid_columnconfigure(0, weight=1)
        # self.welcome_screen_search_container.grid_columnconfigure(1, weight=2)
        self.welcome_screen_search_container.grid_rowconfigure(0, weight=1)
            
        # tk.Frame(self.welcome_screen_search_container, bg="#E1E1E1").grid(row=0, column=0, sticky="NEW", padx=(0, 0), pady=(44, 20))
        # tk.Frame(self.welcome_screen_search_container, bg="white").grid(row=0, column=0, sticky="NEW", padx=(20, 0), pady=(20, 20))
        self.search_bar = tk.Entry(self.welcome_screen_search_container, fg="#696969", bg="white", font=("Open Sans", 13), borderwidth=1, highlightthickness=0)
        self.search_bar.grid(row=0, column=0, sticky="NEWS", padx=(10, 10), pady=(0, 0), ipadx=10)
        
        self.welcome_screen_search_button_im = tk.PhotoImage(file=os.path.join(self.appdata_dir, "4i2efbui.png"))
        self.welcome_screen_search_button_image = self.resize(self.welcome_screen_search_button_im, 73, 55)
        self.welcome_screen_button = tk.Label(self.welcome_screen_search_container, height=50, bg="#ff761a", text="", image=self.welcome_screen_search_button_image, cursor="hand2")
        self.welcome_screen_button.grid(row=0, column=0, sticky="NE", padx=(0, 0), pady=(0, 0))
        self.welcome_screen_button.bind("<Button-1>", self.welcome_screen_search_callback)
        self.search_bar.bind('<Return>', self.welcome_screen_search_callback)

        self.example_frame = tk.Frame(self.welcome_container, bg="white")
        self.example_frame.grid(row=2, column=0, columnspan=1, sticky="NW", padx=(25, 0), pady=(25, 0))
        for i in range(3):
            self.example_frame.grid_columnconfigure(i, weight=1, uniform="foo")
        self.example_frame.grid_rowconfigure(0, weight=1)
        
        self.see_example_label = tk.Label(self.example_frame, text="Or see examples", bg="white", font=("Open Sans", "10", "bold"))
        self.see_example_label.grid(row=0, column=0)

        self.usb_type_c_button_im = tk.PhotoImage(file=self.usb_type_c_button_dir)
        self.usb_type_c_button_image = self.resize(self.usb_type_c_button_im, 89, 21)
        self.usb_type_c_button = tk.Label(self.example_frame, bg="white", text="", image=self.usb_type_c_button_image, cursor="hand2")
        self.usb_type_c_button.grid(row=0, column=1, padx=(0, 0), pady=(0, 0))
        self.usb_type_c_button.bind('<Button-1>', self.usb_type_c_button_callback)

        self.microcontroller_button_im = tk.PhotoImage(file=self.microcontroller_button_dir)
        self.microcontroller_button_image = self.resize(self.microcontroller_button_im, 89, 21)
        self.microcontroller_button = tk.Label(self.example_frame, bg="white", text="", image=self.microcontroller_button_image, cursor="hand2")
        self.microcontroller_button.grid(row=0, column=2, padx=(0, 0), pady=(0, 0))
        self.microcontroller_button.bind('<Button-1>', self.microcontroller_button_callback)

        self.left_003_frame = tk.Frame(self.left_frame, bg="white")
        self.left_003_frame.grid(row=3, column=0, rowspan=2, sticky="NEWS", pady=(70, 0))
        for i in range(3):
            self.left_003_frame.grid_columnconfigure(i, weight=1, uniform="foo")
        for i in range(2):
            self.left_003_frame.grid_rowconfigure(i, weight=1)
        

        welcome_screen_002_img = tk.PhotoImage(file=os.path.join(self.welcome_screen_002_dir))
        self.welcome_screen_002_image = self.resize(welcome_screen_002_img, 100, 113)
        self.welcome_screen_002_bg = tk.Label(self.left_003_frame, image=self.welcome_screen_002_image, bg="white")
        self.welcome_screen_002_bg.grid(row=0, column=0, padx=(30, 25), sticky="S")

        self.label_001 = tk.Label(self.left_003_frame, text="Focus on Design", bg="white", font=("Open Sans", "10", "bold"))
        self.label_001.grid(row=1, column=0, padx=(30, 25), sticky="N")

        welcome_screen_003_img = tk.PhotoImage(file=os.path.join(self.welcome_screen_003_dir))
        self.welcome_screen_003_image = self.resize(welcome_screen_003_img, 100, 113)
        self.welcome_screen_003_bg = tk.Label(self.left_003_frame, image=self.welcome_screen_003_image, bg="white")
        self.welcome_screen_003_bg.grid(row=0, column=1,  padx=(25, 25), sticky="S")

        self.label_002 = tk.Label(self.left_003_frame, text="Crush Deadlines", bg="white", font=("Open Sans", "10", "bold"))
        self.label_002.grid(row=1, column=1, padx=(30, 25), sticky="N")
        
        welcome_screen_004_img = tk.PhotoImage(file=os.path.join(self.welcome_screen_004_dir))
        self.welcome_screen_004_image = self.resize(welcome_screen_004_img, 100, 113)
        self.welcome_screen_004_bg = tk.Label(self.left_003_frame, image=self.welcome_screen_004_image, bg="white")
        self.welcome_screen_004_bg.grid(row=0, column=2, padx=(25, 30), sticky="S")

        self.label_003 = tk.Label(self.left_003_frame, text="Prevent Errors", bg="white", font=("Open Sans", "10", "bold"))
        self.label_003.grid(row=1, column=2, padx=(30, 25), sticky="N")

        # Navbar menu components
        self.how_it_works_button = tk.Label(self.navbar_menu_container, fg="#FF761B", bg="white", text="How it works", cursor="hand2", font=("Open Sans", "8", "bold", "underline"))
        self.update_button = tk.Label(self.navbar_menu_container, fg="#FF761B", bg="white", text="Update", cursor="hand2", font=("Open Sans", "8", "bold", "underline"))
        self.help_me_button = tk.Label(self.navbar_menu_container, fg="#FF761B", bg="white", text="Help Me", cursor="hand2", font=("Open Sans", "8", "bold", "underline"))
        self.how_it_works_button.bind("<Button-1>", self.how_it_works_callback)
        self.update_button.bind("<Button-1>", self.update_callback)
        self.help_me_button.bind("<Button-1>", self.help_me_callback)

        self.help_me_button.grid(row=0, column=3, padx=(0, 0), sticky="W")
        self.how_it_works_button.grid(row=0, column=0, padx=(10, 15), sticky="W")
        self.update_button.grid(row=0, column=2, padx=(0, 15), sticky="W")
        # End of navbar menu components

class LoginScreen(tk.Frame):
    """
    Login screen window.

    Args:
        tk (Tk): The Tk master frame.
    """

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.geometry("458x721")
        self.parent.minsize(width=458, height=721)

        # TODO: check saved token, if it is valid pass login screen
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        # with open(os.path.join(self.dir_path, ".token"), "r") as f:
        #     token = str(f.readline())
        #     token = "GCJFTFB7uV2YtHcBzFMIj3VNRyNkKo5q"
        #     header = {'User-Agent': "Kicad"}
        #     url = "https://www.snapeda.com/api/v1/parts/search?q=%stoken=%s" % (
        #         "ZZZZZ", token)
        #     req = urllib2.Request(url, headers=header)
        #     contents = urllib2.urlopen(req).read()
        #     self.data = json.loads(contents)
        
        # if self.data["status"] == "logged_in":
        
        self.is_windows = (os.name == 'nt')
        token = ''
        try:
            if self.is_windows:
                self.windata_dir = os.path.join(os.getenv('HOMEDRIVE'),
                                                os.getenv('HOMEPATH'),
                                                "SnapEDA Kicad Plugin")
                self.appdata_dir = os.path.join(self.windata_dir, "App")
                with open(os.path.join(self.appdata_dir, ".token"), "r") as f:
                    token = str(f.readline())
                    f.close()
            else:
                self.dir_path = os.path.dirname(os.path.realpath(__file__))
                with open(os.path.join(self.dir_path, ".token"), "r") as f:
                    token = str(f.readline())
                    f.close()
        except:
            token = ''

        try:
            header = {'User-Agent': "Kicad"}
            url = "https://www.snapeda.com/api/v1/parts/search?q=%s&token=%s" % ("test-search", token)

            if sys.version_info[0] == 3:
                req = urllib.request.Request(url, headers=header)
                contents = urllib.request.urlopen(req, timeout=5).read()
            else:
                req = urllib2.Request(url, headers=header)
                contents = urllib2.urlopen(req, timeout=5).read()
            res = json.loads(contents)
            if(res['error'] == None):
                for i in range(5):
                    for widget in self.parent.grid_slaves(row=i, column=0):
                        widget.destroy()
                WelcomeScreen(self.parent)
                return
        except:
            pass

        self.is_mac = platform.mac_ver()[0] != ""
        self.is_windows = (os.name == 'nt')
        if self.is_windows:
            self.windata_dir = os.path.join(os.getenv('HOMEDRIVE'),
                                            os.getenv('HOMEPATH'),
                                            "SnapEDA Kicad Plugin")
            self.appdata_dir = os.path.join(self.windata_dir, "App")
            if not os.path.exists(self.windata_dir):
                os.makedirs(self.windata_dir)
            self.flip_table_dir = os.path.join(os.getenv('HOMEDRIVE'),
                                               os.getenv('HOMEPATH'),
                                               'AppData',
                                               'Roaming',
                                               'kicad',
                                               'fp-lib-table')
            self.appdata_dir = os.path.join(self.windata_dir, "App")
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir)
            if not os.path.exists(self.windata_dir):
                os.makedirs(self.windata_dir)
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir)
            kicad_library_dir = os.path.join(self.windata_dir, 'KiCad Library')
            snapeda_library_dir = os.path.join(kicad_library_dir,
                                               'SnapEDA Library')
            snapeda_library_abs_dir = os.path.join(kicad_library_dir,
                                                   'SnapEDA Library.pretty')
            if not os.path.exists(kicad_library_dir):
                os.makedirs(kicad_library_dir)
            if not os.path.exists(snapeda_library_abs_dir):
                os.makedirs(snapeda_library_abs_dir)
        elif self.is_mac:
            self.macdata_dir = os.path.join(os.path.expanduser("~"), "Documents", "SnapEDA Kicad Plugin")
            self.appdata_dir = os.path.join(self.macdata_dir, "App")
        else:
            self.appdata_dir = os.path.join(self.dir_path, "assets")
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir)
            self.flip_table_dir = os.path.join(os.path.expanduser("~"),
                                               '.config',
                                               'kicad',
                                               'fp-lib-table')
            home_dir = os.path.expanduser("~")
            kicad_library_dir = os.path.join(home_dir, 'KiCad Library')
            snapeda_library_dir = os.path.join(kicad_library_dir,
                                               'SnapEDA Library')
            snapeda_library_abs_dir = os.path.join(kicad_library_dir,
                                                   'SnapEDA Library.pretty')
            if not os.path.exists(kicad_library_dir):
                os.makedirs(kicad_library_dir)
            if not os.path.exists(snapeda_library_abs_dir):
                os.makedirs(snapeda_library_abs_dir)
        self.login_bg_image_dir = os.path.join(self.appdata_dir, "Group+292.png")
        self.username_bg_image_dir = os.path.join(self.appdata_dir, "3xm843ff.png")
        self.password_bg_image_dir = os.path.join(self.appdata_dir, "ek8owdjt.png")
        self.login_button_image_dir = os.path.join(self.appdata_dir, "g4pik2y2.png")
        self.logo_image_dir = os.path.join(self.appdata_dir, "lkeixquo.png")
        self.loading_image_dir = os.path.join(self.appdata_dir, "jwhk6qck.gif")
        self.cover_image_dir = os.path.join(self.appdata_dir, "RefDesign.png")
        self.symbol_image_dir = os.path.join(self.appdata_dir, "Symbol.png")
        self.package_image_dir = os.path.join(self.appdata_dir,
                                              "Footprint.png")
        if not os.path.exists(self.logo_image_dir):
            tkMessageBox.showwarning("Installation", "Installation is started, please click OK and wait for the complete." +
                                     "It may take a time, login screen will be opened when the installation is completed." +
                                     "After the installation is completed, you have to restart the plugin, Pcbnew and KiCad.")
            self.download_image("http://s19.directupload.net/images/200201/lkeixquo.png")
            # self.download_image("https://i.ibb.co/jJG6Pf2/Logo.png")
        if not os.path.exists(self.loading_image_dir):
            self.download_image("http://s19.directupload.net/images/200208/jwhk6qck.gif")
        if not os.path.exists(self.cover_image_dir):
            self.download_image(
                "https://s3.amazonaws.com/snapeda/ulp/RefDesign.png")
        if not os.path.exists(self.symbol_image_dir):
            self.download_image(
                "https://s3.amazonaws.com/snapeda/ulp/Symbol.png")
        if not os.path.exists(self.package_image_dir):
            self.download_image(
                "https://s3.amazonaws.com/snapeda/ulp/Footprint.png")
        if not os.path.exists(self.login_bg_image_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/Group+292.png")
        if not os.path.exists(self.username_bg_image_dir):
            self.download_image(
                "https://s19.directupload.net/images/200224/3xm843ff.png")
        if not os.path.exists(self.password_bg_image_dir):
            self.download_image(
                "https://s19.directupload.net/images/200224/ek8owdjt.png")
        if not os.path.exists(self.login_button_image_dir):
            self.download_image(
                "https://s19.directupload.net/images/200224/g4pik2y2.png")
        
        # Download welcome screen images
        self.welcome_screen_001_dir = os.path.join(self.appdata_dir, "Mask+Group.png")
        self.welcome_screen_002_dir = os.path.join(self.appdata_dir, "icon1.bbe45f7648f7.png")
        self.welcome_screen_003_dir = os.path.join(self.appdata_dir, "ico_deadlines.8ba69c3f942a.png")
        self.welcome_screen_004_dir = os.path.join(self.appdata_dir, "icon2.924b03ebfccc.png")
        self.welcome_screen_005_dir = os.path.join(self.appdata_dir, "powered+by+snapEDA.png")
        self.welcome_screen_006_dir = os.path.join(self.appdata_dir, "snapeda-transparent.png")
        self.usb_type_c_button_dir = os.path.join(self.appdata_dir, "usb+type+c.png")
        self.microcontroller_button_dir = os.path.join(self.appdata_dir, "usb+microcontroller.png")
        
        if not os.path.exists(self.welcome_screen_001_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Designs+-+API/Mask+Group.png")
        if not os.path.exists(self.welcome_screen_002_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/icon1.bbe45f7648f7.png")
        if not os.path.exists(self.welcome_screen_003_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/ico_deadlines.8ba69c3f942a.png")
        if not os.path.exists(self.welcome_screen_004_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/icon2.924b03ebfccc.png")
        if not os.path.exists(self.welcome_screen_005_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Designs+-+API/powered+by+snapEDA.png")
        if not os.path.exists(self.welcome_screen_006_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/snapeda-transparent.png")
        if not os.path.exists(self.usb_type_c_button_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/usb+type+c.png")
        if not os.path.exists(self.microcontroller_button_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/usb+microcontroller.png")
        
        self.filter_button_image_dir = os.path.join(self.appdata_dir, "neeo2s8g.png")
        self.settings_button_image_dir = os.path.join(self.appdata_dir, "7svfoe57.png")
        self.about_button_image_dir = os.path.join(self.appdata_dir, "2kdtezsl.png")
        self.passive_components_image_dir = os.path.join(self.appdata_dir, "t3gwhnzh.png")
        self.all_button_image_dir = os.path.join(self.appdata_dir, "dsyrvfl9.png")
        self.powered_image_dir = os.path.join(self.appdata_dir, "orb6glbv.png")
        self.datasheet_button_dir = os.path.join(self.appdata_dir, "oxfarxz8.png")
        self.datasheet_available_dir = os.path.join(self.appdata_dir, "m4lamm2w.png")
        self.datasheet_not_available_dir = os.path.join(self.appdata_dir, "4cnn9kkf.png")
        self.symbol_available_dir = os.path.join(self.appdata_dir, "huaxvbtm.png")
        self.symbol_not_available_dir = os.path.join(self.appdata_dir, "tmuhgmxh.png")
        self.footprint_available_dir = os.path.join(self.appdata_dir, "3ruuehki.png")
        self.footprint_not_available_dir = os.path.join(self.appdata_dir, "footprint_outline.cebd715affd8.png")
        self.available_dir = os.path.join(self.appdata_dir, "uku4ceuv.png")
        self.not_available_dir = os.path.join(self.appdata_dir, "zah3n8r4.png")
        self.prev_bg_dir = os.path.join(self.appdata_dir, "iu2ma3jp.png")
        self.next_bg_dir = os.path.join(self.appdata_dir, "witafnjf.png")
        self.selected_page_dir = os.path.join(self.appdata_dir, "izif2qd8.png")
        self.download_button_dir = os.path.join(self.appdata_dir, "download+orange.png")
        self.view_button_dir = os.path.join(self.appdata_dir, "viewonsnapeda+white.png")
        self.search_button_image_dir = os.path.join(self.appdata_dir, "4i2efbui.png")
        self.loading_image_dir = os.path.join(self.appdata_dir, "jwhk6qck.gif")
        self.icon_bitmap_dir = os.path.join(self.appdata_dir, "32x32.ico")
        if not os.path.exists(self.filter_button_image_dir):
            self.download_image("https://s19.directupload.net/images/200224/neeo2s8g.png")
        if not os.path.exists(self.settings_button_image_dir):
            self.download_image("https://s19.directupload.net/images/200224/7svfoe57.png")
        if not os.path.exists(self.about_button_image_dir):
            self.download_image("https://s19.directupload.net/images/200224/2kdtezsl.png")
        if not os.path.exists(self.passive_components_image_dir):
            self.download_image("https://s19.directupload.net/images/200224/t3gwhnzh.png")
        if not os.path.exists(self.all_button_image_dir):
            self.download_image("https://s19.directupload.net/images/200311/dsyrvfl9.png")
        if not os.path.exists(self.powered_image_dir):
            self.download_image("https://s19.directupload.net/images/200311/orb6glbv.png")
        if not os.path.exists(self.datasheet_button_dir):
            self.download_image("https://s19.directupload.net/images/200224/oxfarxz8.png")
        if not os.path.exists(self.datasheet_available_dir):
            self.download_image("https://s19.directupload.net/images/200313/m4lamm2w.png")
        if not os.path.exists(self.datasheet_not_available_dir):
            self.download_image("https://s19.directupload.net/images/200313/4cnn9kkf.png")
        if not os.path.exists(self.symbol_available_dir):
            self.download_image("https://s19.directupload.net/images/200313/huaxvbtm.png")
        if not os.path.exists(self.symbol_not_available_dir):
            self.download_image("https://s19.directupload.net/images/200313/tmuhgmxh.png")
        if not os.path.exists(self.footprint_available_dir):
            self.download_image("https://s19.directupload.net/images/200313/3ruuehki.png")
        if not os.path.exists(self.footprint_not_available_dir):
            self.download_image("https://s19.directupload.net/images/200313/62r7iuz7.png")
        if not os.path.exists(self.available_dir):
            self.download_image("https://s19.directupload.net/images/200224/uku4ceuv.png")
        if not os.path.exists(self.not_available_dir):
            self.download_image("https://s19.directupload.net/images/200224/zah3n8r4.png")
        if not os.path.exists(self.prev_bg_dir):
            self.download_image("https://s19.directupload.net/images/200224/iu2ma3jp.png")
        if not os.path.exists(self.next_bg_dir):
            self.download_image("https://s19.directupload.net/images/200224/witafnjf.png")
        if not os.path.exists(self.selected_page_dir):
            self.download_image("https://s19.directupload.net/images/200224/izif2qd8.png")
        if not os.path.exists(self.download_button_dir):
            self.download_image("https://snapeda.s3.amazonaws.com/Kicadplugin/download+orange.png")
        if not os.path.exists(self.view_button_dir):
            self.download_image("https://snapeda.s3.amazonaws.com/Kicadplugin/viewonsnapeda+white.png")
        if not os.path.exists(self.search_button_image_dir):
            self.download_image("https://s19.directupload.net/images/200311/4i2efbui.png")
        if not os.path.exists(self.icon_bitmap_dir):
            self.download_ico("https://snapeda.s3.amazonaws.com/Kicadplugin/32x32.ico")
        
        self.parent.grid_columnconfigure(0, weight=1)
        with open(self.flip_table_dir, "r+") as f:
            table = f.read()
            if "(lib (name \"SnapEDA Library\")(type KiCad)" not in table:
                new_entry = ('  (lib (name "SnapEDA Library")(type KiCad)(uri "%r")(options "")(descr ""))' %
                             snapeda_library_abs_dir) + "\n)"
                new_entry = new_entry.replace("'", "")
                new_table = table[:-2] + new_entry
                f.seek(0)
                f.write(new_table)
                f.truncate()
        print('Login screen initialized.')
        self.initialize_user_interface()

    def download_ico(self, url):
        if sys.version_info[0] == 3:
            urllib.request.urlretrieve(url, self.icon_bitmap_dir)
        else:
            urllib.urlretrieve(url, self.icon_bitmap_dir)

    def download_image(self, url):
        # TODO: convert jpg to png without PIL
        image_name = url[url.rfind('/') + 1:]
        image_path = os.path.join(self.appdata_dir, image_name)
        png_path = image_path[:-3] + "png"
        if image_path[-3:] == "gif" or image_path[-3:] == "GIF":
            png_path = image_path
        if not os.path.exists(png_path) and not self.is_mac:
            if self.is_windows:
                convert_path = os.path.join(os.path.dirname(__file__), "imagemagick", "convert")
                subprocess.check_call([convert_path, url.replace("https", "http"), png_path], shell=True)
            else:
                subprocess.call("convert " + url.replace("https", "http") + " " + png_path, shell=True)
        if self.is_mac:
            if not os.path.exists(png_path):
                with open(image_path, "wb") as f:
                    if sys.version_info[0] == 3:
                        image_data = urllib.request.urlopen(url).read()
                    else:
                        image_data = urllib2.urlopen(url).read()
                    f.write(image_data)
                    f.close()
                    subprocess.check_call(["sips", "-s", "format", "gif", "%s" % image_path, "--out", "%s" % png_path], shell=True)
        return png_path

    # This section is for creating a placeholder for entries
    def on_entry_click_username(self, event):
        if self.username_entry.get() == "Username or Email":
            self.username_entry.delete(0, "end")
            self.username_entry.insert(0, '')
            self.username_entry.config(fg='black')

    def on_focusout_username(self, event):
        if self.username_entry.get() == '':
            self.username_entry.insert(0, "Username or Email")
            self.username_entry.config(fg='black')

    def on_entry_click_password(self, event):
        if self.password_entry.get() == 'Password':
            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, '')
            self.password_entry.config(fg='black', show="*")

    def on_focusout_password(self, event):
        if self.password_entry.get() == '':
            self.password_entry.insert(0, 'Password')
            self.password_entry.config(fg='black', show="")

    # Runs on Login button clicked
    def check_login_thread(self, event):
        self.login_button.config(state="disabled", text="")
        self.login_thread = threading.Thread(target=self.check_login)
        self.login_thread.start()

    def check_login(self):
        header = {'User-Agent': "Kicad"}
        url = "https://www.snapeda.com/account/api-login/"
        values = {
            'username': self.username_entry.get(),
            'password': self.password_entry.get(),
            'ref': "kicad-plugin",
        }
        if sys.version_info[0] == 3:
            data = urllib.parse.urlencode(values).encode("utf-8")
            req = urllib.request.Request(url, data, headers=header)
            contents = urllib.request.urlopen(req).read()
        else:
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data, headers=header)
            contents = urllib2.urlopen(req).read()
        self.data = json.loads(contents)
        # Check if user exists
        if self.data["status"] == "logged_in":
            if self.is_windows:
                # Get info.json username 
                info_dir = os.path.join(self.appdata_dir, "info.json")
                with open(info_dir) as json_file:
                    data = json.load(json_file)
                new_data = {
                    'version': data['version'],
                    'username': self.username_entry.get()
                }
                with open(info_dir, 'w') as outfile:
                    json.dump(new_data, outfile)

                with open(os.path.join(self.appdata_dir, ".token"), "w") as f:
                    f.write(self.data["token"])
                    f.close()
            else:
                # Get info.json username 
                info_dir = os.path.join(self.appdata_dir, "info.json")
                with open(info_dir) as json_file:
                    data = json.load(json_file)
                new_data = {
                    'version': data['version'],
                    'username': self.username_entry.get()
                }
                with open(info_dir, 'w') as outfile:
                    json.dump(new_data, outfile)

                with open(os.path.join(self.dir_path, ".token"), "w") as f:
                    f.write(self.data["token"])
                    f.close()
            # Clear login screen to create table view
            for i in range(5):
                for widget in self.parent.grid_slaves(row=i, column=0):
                    widget.destroy()
            # Create table view
            WelcomeScreen(self.parent)
        else:
            self.label.config(text="The username/email or password you specified are not correct.")
            self.login_button.config(state="normal", text="")

    def resize(self, image, w_new, h_new):
        '''
        resize a pil_image object so it will fit into
        a box of size w_box times h_box, but retain aspect ratio
        '''
        if sys.version_info[0] == 3:
            width = image.width()
            height = image.height()
            min_wh = max(width, height)
            min_wh_new = max(w_new, h_new)
            if min_wh > min_wh_new:
                return image.subsample(int(min_wh / min_wh_new))
            else:
                return image.zoom(int(min_wh_new / min_wh))
        else:
            width = image.width()
            height = image.height()
            min_wh = max(width, height)
            min_wh_new = max(w_new, h_new)
            if min_wh > min_wh_new:
                return image.subsample(min_wh / min_wh_new)
            else:
                return image.zoom(min_wh_new / min_wh)

    def forgot_callback(self, event):
        webbrowser.open("https://www.snapeda.com/account/password_reset/", new=2)

    def register_callback(self, event):
        webbrowser.open("https://www.snapeda.com/account/signup/", new=2)

    # Initializes login screen
    def initialize_user_interface(self):
        if self.is_windows:
            self.parent.iconbitmap(self.icon_bitmap_dir)
        self.parent.title("SnapEDA v" + self.parent.version)
        self.login_frame = tk.Frame(self.parent, bg="white")
        self.login_frame.grid(row=0, column=0, sticky="NEWS")
        login_bg_im = tk.PhotoImage(
            file=os.path.join(self.login_bg_image_dir))
        self.login_bg_image = self.resize(login_bg_im, 458, 721)
        self.login_bg = tk.Label(self.login_frame, image=self.login_bg_image, bg="white")
        self.login_bg.grid(row=0, column=0, sticky="NEWS", rowspan=6, columnspan=2)
        for i in range(6):
            if i < 2:
                self.login_frame.grid_columnconfigure(i, weight=1, uniform="foo")
            self.login_frame.grid_rowconfigure(i, weight=1)
        # Load SnapEDA logo to show
        # logo_im = tk.PhotoImage(
        #     file=os.path.join(self.appdata_dir, "lkeixquo.png"))
        # logo_image = self.resize(logo_im, 150, 150)
        # self.logo_view = tk.Label(self.parent, image=logo_image,
        #                           bg="white")
        # self.logo_view.grid(row=0,
        #                     column=0,
        #                     pady=100,
        #                     sticky='N')
        # self.logo = logo_image
        # Label for welcome and failure messages
        self.label = tk.Label(self.login_frame, text="", bg="white")
        self.label.grid(row=0, column=0, columnspan=2, sticky="S", pady=(250, 0))
        # Usarname entry
        self.userpass_frame = tk.Frame(self.login_frame, bg="white")
        self.userpass_frame.grid(row=1, column=0, columnspan=2)
        username_bg_im = tk.PhotoImage(
            file=os.path.join(self.username_bg_image_dir))
        self.username_bg_image = self.resize(username_bg_im, 229, 34)
        self.username_image = tk.Label(self.userpass_frame, image=self.username_bg_image, bg="white")
        self.username_image.grid(row=0, column=0, sticky="W")
        self.username_entry = tk.Entry(self.userpass_frame, font=("Open Sans", "10"), bg="#C4C4C4", borderwidth=0, highlightthickness=0)
        self.username_entry.insert(0, "Username or Email")
        self.username_entry.grid(row=0, column=0, padx=(5, 0))
        self.username_entry.bind('<FocusIn>', self.on_entry_click_username)
        self.username_entry.bind('<FocusOut>', self.on_focusout_username)
        self.username_entry.config(fg='black')
        # Password entry
        password_bg_im = tk.PhotoImage(
            file=os.path.join(self.password_bg_image_dir))
        self.password_bg_image = self.resize(password_bg_im, 229, 34)
        self.password_image = tk.Label(self.userpass_frame, image=self.password_bg_image, bg="white")
        self.password_image.grid(row=1, column=0, sticky="W", pady=(20, 0))
        self.password_entry = tk.Entry(self.userpass_frame, font=("Open Sans", "10"), bg="#C4C4C4", borderwidth=0, highlightthickness=0)
        self.password_entry.insert(0, "Password")
        self.password_entry.grid(row=1, column=0, padx=(5, 0), pady=(20, 0))
        self.password_entry.bind('<FocusIn>', self.on_entry_click_password)
        self.password_entry.bind('<FocusOut>', self.on_focusout_password)
        self.password_entry.config(fg='black')

        # Bind username and password inputs
        self.username_entry.bind('<Return>', self.check_login_thread)
        self.password_entry.bind('<Return>', self.check_login_thread)

        # Forgot Password?
        self.forgot_password = tk.Label(self.userpass_frame, text="Forgot Password?", fg="#696969", cursor="hand2", bg="white")
        self.forgot_password.grid(row=2, column=0, pady=(11, 0))
        self.forgot_password.bind("<Button-1>", self.forgot_callback)
        # Login button
        login_button_im = tk.PhotoImage(
            file=os.path.join(self.login_button_image_dir))
        self.login_button_image = self.resize(login_button_im, 173, 42)
        self.login_button = tk.Label(self.login_frame,
                                     text="",
                                     cursor="hand2",
                                     bg="white",
                                     image=self.login_button_image)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=(15, 4))
        self.login_button.bind("<Button-1>", self.check_login_thread)
        # Don't have account?
        self.register_frame = tk.Frame(self.login_frame, bg="white")
        self.register_frame.grid(row=2, column=0, columnspan=2, sticky="S")
        dont_have_label = tk.Label(self.register_frame, bg="white", fg="#696969", text="Don't have an account?", font=("Open Sans", "8"))
        dont_have_label.grid(row=0, column=0, sticky="N")
        self.register_button = tk.Label(
            self.register_frame,
            text="Register",
            fg="#FF761B",
            cursor="hand2",
            bg="white",
            font=(
                "Open Sans",
                "8",
                "bold"))
        self.register_button.grid(row=0, column=1, pady=(0, 0), sticky="N")
        self.register_button.bind("<Button-1>", self.register_callback)

class InstallScreen(tk.Frame):
    """
    Installation screen window.

    Args:
        tk (Tk): The Tk master frame.
    """

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.version = parent.version
        self.parent.geometry("458x721")
        self.parent.minsize(width=458, height=721)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        self.initialize_user_interface()

    def image_return(self, path):
        return path

    def download_ico(self, url):
        if sys.version_info[0] == 3:
            urllib.request.urlretrieve(url, self.icon_bitmap_dir)
        else:
            urllib.urlretrieve(url, self.icon_bitmap_dir)
        
    def download_image(self, url):
        image_name = url[url.rfind('/') + 1:]
        image_path = os.path.join(self.appdata_dir, image_name)
        png_path = image_path[:-3] + "png"
        timer = threading.Timer(2, self.image_return, args=(png_path,))
        timer.start()
        if not os.path.exists(png_path) and not self.is_mac:
            if self.is_windows:
                convert_path = os.path.join(os.path.dirname(__file__), "imagemagick", "convert")
                subprocess.check_call([convert_path, url.replace("https", "http"), png_path], shell=True)
            else:
                subprocess.call("convert " + url.replace("https", "http") + " " + png_path, shell=True)
        if self.is_mac:
            if not os.path.exists(png_path):
                with open(image_path, "wb") as f:
                    if sys.version_info[0] == 3:
                        image_data = urllib.request.urlopen(url).read()
                    else:
                        image_data = urllib2.urlopen(url).read()
                    f.write(image_data)
                    f.close()
                    subprocess.check_call(["sips", "-s", "format", "gif", "%s" % image_path, "--out", "%s" % png_path], shell=True)
        return png_path

    def setup_dirs(self):
        """
        Generates all the required directories.
        """
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.is_mac = platform.mac_ver()[0] != ""
        self.is_windows = (os.name == 'nt')
        if self.is_windows:
            self.windata_dir = os.path.join(os.getenv('HOMEDRIVE'),
                                            os.getenv('HOMEPATH'),
                                            "SnapEDA Kicad Plugin")
            self.appdata_dir = os.path.join(self.windata_dir, "App")
            if not os.path.exists(self.windata_dir):
                os.makedirs(self.windata_dir)
            self.flip_table_dir = os.path.join(os.getenv('HOMEDRIVE'),
                                               os.getenv('HOMEPATH'),
                                               'AppData',
                                               'Roaming',
                                               'kicad',
                                               'fp-lib-table')
            self.kicad_common_dir = os.path.join(os.getenv('HOMEDRIVE'),
                                               os.getenv('HOMEPATH'),
                                               'AppData',
                                               'Roaming',
                                               'kicad',
                                               'kicad_common')
            self.appdata_dir = os.path.join(self.windata_dir, "App")
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir)
            if not os.path.exists(self.windata_dir):
                os.makedirs(self.windata_dir)
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir)
            kicad_library_dir = os.path.join(self.windata_dir, 'KiCad Library')
            self.snapeda_library_dir = os.path.join(kicad_library_dir,
                                               'SnapEDA Library')
            self.snapeda_library_abs_dir = os.path.join(kicad_library_dir,
                                                   'SnapEDA Library.pretty')
            if not os.path.exists(kicad_library_dir):
                os.makedirs(kicad_library_dir)
            if not os.path.exists(self.snapeda_library_dir):
                os.makedirs(self.snapeda_library_dir)
            if not os.path.exists(self.snapeda_library_abs_dir):
                os.makedirs(self.snapeda_library_abs_dir)
        elif self.is_mac:
            self.macdata_dir = os.path.join(os.path.expanduser("~"), "Documents", "SnapEDA Kicad Plugin")
            self.appdata_dir = os.path.join(self.macdata_dir, "App")
        else:
            self.appdata_dir = os.path.join(self.dir_path, "assets")
            if not os.path.exists(self.appdata_dir):
                os.makedirs(self.appdata_dir)
            self.flip_table_dir = os.path.join(os.path.expanduser("~"),
                                               '.config',
                                               'kicad',
                                               'fp-lib-table')
            self.kicad_common_dir = os.path.join(os.path.expanduser("~"),
                                               '.config',
                                               'kicad',
                                               'kicad_common')
            home_dir = os.path.expanduser("~")
            kicad_library_dir = os.path.join(home_dir, 'KiCad Library')
            self.snapeda_library_dir = os.path.join(kicad_library_dir,
                                               'SnapEDA Library')
            self.snapeda_library_abs_dir = os.path.join(kicad_library_dir,
                                                   'SnapEDA Library.pretty')
            if not os.path.exists(kicad_library_dir):
                os.makedirs(kicad_library_dir)
            if not os.path.exists(self.snapeda_library_abs_dir):
                os.makedirs(self.snapeda_library_abs_dir)


        # Write/Read JSON Info version
        info_dir = os.path.join(self.appdata_dir, "info.json")
        if not os.path.exists(info_dir):
            data = {
                'version': self.version
            }
            with open(info_dir, 'w') as outfile:
                json.dump(data, outfile)
            print('No info.json')
            self.is_installing = True
        else:
            try:
                with open(info_dir) as json_file:
                    data = json.load(json_file)
                if not data['version'] == self.version:
                    self.is_installing = True
                    data = {
                        'version': self.version
                    }
                    with open(info_dir, 'w') as outfile:
                        json.dump(data, outfile)
                    print('Obsolete info.json')
            except:
                self.is_installing = True
                data = {
                    'version': self.version
                }
                with open(info_dir, 'w') as outfile:
                    json.dump(data, outfile)
                print('Obsolete info.json')
         
        with open(self.flip_table_dir, "r+") as f:
            table = f.read()
            if "(lib (name \"SnapEDA Library\")(type KiCad)" not in table:
                new_entry = ('  (lib (name "SnapEDA Library")(type KiCad)(uri "%r")(options "")(descr ""))' %
                             self.snapeda_library_abs_dir) + "\n)"
                new_entry = new_entry.replace("'", "")
                new_table = table[:-2] + new_entry
                f.seek(0)
                f.write(new_table)
                f.truncate()

        with open(self.kicad_common_dir, "r+") as f:
            table = f.read()
            if "SNAPEDA_SYMBOL_DIR" not in table:
                new_entry = '\nSNAPEDA_SYMBOL_DIR=' + self.snapeda_library_dir  +'\n'
                new_entry = new_entry.replace("\\", "\\\\")
                new_table = table[:-2] + new_entry
                f.seek(0)
                f.write(new_table)
                f.truncate()
                f.close()

    def continue_installation_callback(self, event):
        for widget in self.parent.grid_slaves():
            widget.destroy()
        LoginScreen(self.parent)

    def installation_process(self):
        # Delete token
        try:
            if self.is_windows:
                os.remove(os.path.join(self.appdata_dir, '.token'))
            else:
                os.remove(os.path.join(self.dir_path, ".token"))
        except:
            pass

        self.login_bg_image_dir = os.path.join(self.appdata_dir, "Group+292.png")
        self.username_bg_image_dir = os.path.join(self.appdata_dir, "3xm843ff.png")
        self.password_bg_image_dir = os.path.join(self.appdata_dir, "ek8owdjt.png")
        self.login_button_image_dir = os.path.join(self.appdata_dir, "g4pik2y2.png")
        self.logo_image_dir = os.path.join(self.appdata_dir, "lkeixquo.png")
        self.loading_image_dir = os.path.join(self.appdata_dir, "jwhk6qck.gif")
        self.cover_image_dir = os.path.join(self.appdata_dir, "RefDesign.png")
        self.symbol_image_dir = os.path.join(self.appdata_dir, "Symbol.png")
        self.package_image_dir = os.path.join(self.appdata_dir,
                                              "Footprint.png")
        if not os.path.exists(self.logo_image_dir):
            self.download_image("http://s19.directupload.net/images/200201/lkeixquo.png")
            # self.download_image("https://i.ibb.co/jJG6Pf2/Logo.png")
        if not os.path.exists(self.loading_image_dir):
            self.download_image("http://s19.directupload.net/images/200208/jwhk6qck.gif")
        if not os.path.exists(self.cover_image_dir):
            self.download_image(
                "https://s3.amazonaws.com/snapeda/ulp/RefDesign.png")
        if not os.path.exists(self.symbol_image_dir):
            self.download_image(
                "https://s3.amazonaws.com/snapeda/ulp/Symbol.png")
        if not os.path.exists(self.package_image_dir):
            self.download_image(
                "https://s3.amazonaws.com/snapeda/ulp/Footprint.png")
        if not os.path.exists(self.login_bg_image_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/Group+292.png")
        if not os.path.exists(self.username_bg_image_dir):
            self.download_image(
                "https://s19.directupload.net/images/200224/3xm843ff.png")
        if not os.path.exists(self.password_bg_image_dir):
            self.download_image(
                "https://s19.directupload.net/images/200224/ek8owdjt.png")
        if not os.path.exists(self.login_button_image_dir):
            self.download_image(
                "https://s19.directupload.net/images/200224/g4pik2y2.png")
        
        # Download welcome screen images
        self.welcome_screen_001_dir = os.path.join(self.appdata_dir, "Mask+Group.png")
        self.welcome_screen_002_dir = os.path.join(self.appdata_dir, "icon1.bbe45f7648f7.png")
        self.welcome_screen_003_dir = os.path.join(self.appdata_dir, "ico_deadlines.8ba69c3f942a.png")
        self.welcome_screen_004_dir = os.path.join(self.appdata_dir, "icon2.924b03ebfccc.png")
        self.welcome_screen_005_dir = os.path.join(self.appdata_dir, "powered+by+snapEDA.png")
        self.welcome_screen_006_dir = os.path.join(self.appdata_dir, "snapeda-transparent.png")
        self.usb_type_c_button_dir = os.path.join(self.appdata_dir, "usb+type+c.png")
        self.microcontroller_button_dir = os.path.join(self.appdata_dir, "usb+microcontroller.png")
        
        if not os.path.exists(self.welcome_screen_001_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Designs+-+API/Mask+Group.png")
        if not os.path.exists(self.welcome_screen_002_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/icon1.bbe45f7648f7.png")
        if not os.path.exists(self.welcome_screen_003_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/ico_deadlines.8ba69c3f942a.png")
        if not os.path.exists(self.welcome_screen_004_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/icon2.924b03ebfccc.png")
        if not os.path.exists(self.welcome_screen_005_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Designs+-+API/powered+by+snapEDA.png")
        if not os.path.exists(self.welcome_screen_006_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/snapeda-transparent.png")
        if not os.path.exists(self.usb_type_c_button_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/usb+type+c.png")
        if not os.path.exists(self.microcontroller_button_dir):
            self.download_image(
                "https://snapeda.s3.amazonaws.com/Kicadplugin/usb+microcontroller.png")
        
        self.filter_button_image_dir = os.path.join(self.appdata_dir, "neeo2s8g.png")
        self.settings_button_image_dir = os.path.join(self.appdata_dir, "7svfoe57.png")
        self.about_button_image_dir = os.path.join(self.appdata_dir, "2kdtezsl.png")
        self.passive_components_image_dir = os.path.join(self.appdata_dir, "t3gwhnzh.png")
        self.all_button_image_dir = os.path.join(self.appdata_dir, "dsyrvfl9.png")
        self.powered_image_dir = os.path.join(self.appdata_dir, "orb6glbv.png")
        self.datasheet_button_dir = os.path.join(self.appdata_dir, "oxfarxz8.png")
        self.datasheet_available_dir = os.path.join(self.appdata_dir, "m4lamm2w.png")
        self.datasheet_not_available_dir = os.path.join(self.appdata_dir, "4cnn9kkf.png")
        self.symbol_available_dir = os.path.join(self.appdata_dir, "huaxvbtm.png")
        self.symbol_not_available_dir = os.path.join(self.appdata_dir, "tmuhgmxh.png")
        self.footprint_available_dir = os.path.join(self.appdata_dir, "3ruuehki.png")
        self.footprint_not_available_dir = os.path.join(self.appdata_dir, "footprint_outline.cebd715affd8.png")
        self.available_dir = os.path.join(self.appdata_dir, "uku4ceuv.png")
        self.not_available_dir = os.path.join(self.appdata_dir, "zah3n8r4.png")
        self.prev_bg_dir = os.path.join(self.appdata_dir, "iu2ma3jp.png")
        self.next_bg_dir = os.path.join(self.appdata_dir, "witafnjf.png")
        self.selected_page_dir = os.path.join(self.appdata_dir, "izif2qd8.png")
        self.download_button_dir = os.path.join(self.appdata_dir, "download+orange.png")
        self.view_button_dir = os.path.join(self.appdata_dir, "viewonsnapeda+white.png")
        self.search_button_image_dir = os.path.join(self.appdata_dir, "4i2efbui.png")
        self.loading_image_dir = os.path.join(self.appdata_dir, "jwhk6qck.gif")
        self.icon_bitmap_dir = os.path.join(self.appdata_dir, "32x32.ico")
        if not os.path.exists(self.filter_button_image_dir):
            self.download_image("https://s19.directupload.net/images/200224/neeo2s8g.png")
        if not os.path.exists(self.settings_button_image_dir):
            self.download_image("https://s19.directupload.net/images/200224/7svfoe57.png")
        if not os.path.exists(self.about_button_image_dir):
            self.download_image("https://s19.directupload.net/images/200224/2kdtezsl.png")
        if not os.path.exists(self.passive_components_image_dir):
            self.download_image("https://s19.directupload.net/images/200224/t3gwhnzh.png")
        if not os.path.exists(self.all_button_image_dir):
            self.download_image("https://s19.directupload.net/images/200311/dsyrvfl9.png")
        if not os.path.exists(self.powered_image_dir):
            self.download_image("https://s19.directupload.net/images/200311/orb6glbv.png")
        if not os.path.exists(self.datasheet_button_dir):
            self.download_image("https://s19.directupload.net/images/200224/oxfarxz8.png")
        if not os.path.exists(self.datasheet_available_dir):
            self.download_image("https://s19.directupload.net/images/200313/m4lamm2w.png")
        if not os.path.exists(self.datasheet_not_available_dir):
            self.download_image("https://s19.directupload.net/images/200313/4cnn9kkf.png")
        if not os.path.exists(self.symbol_available_dir):
            self.download_image("https://s19.directupload.net/images/200313/huaxvbtm.png")
        if not os.path.exists(self.symbol_not_available_dir):
            self.download_image("https://s19.directupload.net/images/200313/tmuhgmxh.png")
        if not os.path.exists(self.footprint_available_dir):
            self.download_image("https://s19.directupload.net/images/200313/3ruuehki.png")
        if not os.path.exists(self.footprint_not_available_dir):
            self.download_image("https://s19.directupload.net/images/200313/62r7iuz7.png")
        if not os.path.exists(self.available_dir):
            self.download_image("https://s19.directupload.net/images/200224/uku4ceuv.png")
        if not os.path.exists(self.not_available_dir):
            self.download_image("https://s19.directupload.net/images/200224/zah3n8r4.png")
        if not os.path.exists(self.prev_bg_dir):
            self.download_image("https://s19.directupload.net/images/200224/iu2ma3jp.png")
        if not os.path.exists(self.next_bg_dir):
            self.download_image("https://s19.directupload.net/images/200224/witafnjf.png")
        if not os.path.exists(self.selected_page_dir):
            self.download_image("https://s19.directupload.net/images/200224/izif2qd8.png")
        if not os.path.exists(self.download_button_dir):
            self.download_image("https://snapeda.s3.amazonaws.com/Kicadplugin/download+orange.png")
        if not os.path.exists(self.view_button_dir):
            self.download_image("https://snapeda.s3.amazonaws.com/Kicadplugin/viewonsnapeda+white.png")
        if not os.path.exists(self.search_button_image_dir):
            self.download_image("https://s19.directupload.net/images/200311/4i2efbui.png")
        if not os.path.exists(self.icon_bitmap_dir):
            self.download_ico("https://snapeda.s3.amazonaws.com/Kicadplugin/32x32.ico")

        with open(self.flip_table_dir, "r+") as f:
            table = f.read()
            if "(lib (name \"SnapEDA Library\")(type KiCad)" not in table:
                new_entry = ('  (lib (name "SnapEDA Library")(type KiCad)(uri "%r")(options "")(descr ""))' %
                             self.snapeda_library_abs_dir) + "\n)"
                new_entry = new_entry.replace("'", "")
                new_table = table[:-2] + new_entry
                f.seek(0)
                f.write(new_table)
                f.truncate()

        # Rewrite fp-lib-table
        new_entry = ('")(type KiCad)(uri "%r")(options "")(descr ""))' % self.snapeda_library_abs_dir)
        new_entry = new_entry.replace("'", "")
        lines_to_write = ''
        for line in open(self.flip_table_dir, 'r').readlines():
            line = re.sub(r'SnapEDA Library.+',(r'SnapEDA Library' + new_entry), line)
            lines_to_write += line

        with open(self.flip_table_dir, 'w') as filetowrite:
            filetowrite.write(lines_to_write)
        print('lines written')
        
        self.instruction_header_label.set("INSTALLATION COMPLETE")
        self.install_frame.config(cursor="hand2")
        self.instruction_label.set("Click screen to complete installation.\n Directing to login in screen in ")
        self.install_frame.bind("<Button-1>", self.continue_installation_callback)
        
        for i in range(5, 0, -1):
            tk.Label(self.install_frame, text=i, fg="white", bg="#ff761a", font=("Open Sans", "20", "bold")).grid(row=2, column=0, sticky="SEW")
            time.sleep(1)

        for widget in self.parent.grid_slaves():
            widget.destroy()
        LoginScreen(self.parent)

    def initialize_user_interface(self):
        self.is_installing = False
        self.setup_dirs()

        if self.is_installing:
            self.parent.title("SnapEDA v" + self.parent.version)
            self.parent.geometry("1150x828")
            self.parent.minsize(width=1150, height=828)
            snapeda_color = "#ff761a"
            self.install_frame = tk.Frame(self.parent, bg=snapeda_color)
            for i in range(6):
                self.install_frame.grid_rowconfigure(i, weight=1, uniform="foo")
            self.install_frame.grid_columnconfigure(0, weight=1)
            self.install_frame.grid(row=0, column=0, sticky="NEWS")
            self.instruction_label = tk.StringVar()
            self.instruction_label.set("Installation is starting.\nPlease wait for the installation to complete.")
            self.instruction_header_label = tk.StringVar()
            self.instruction_header_label.set("INSTALLING...")
            self.install_title_label = tk.Label(self.install_frame, textvariable=self.instruction_header_label, fg="white", bg=snapeda_color, font=("Open Sans", "18", "bold"))
            self.install_title_label.grid(row=1, column=0, sticky="SEW")
            self.install_instructions_label = tk.Label(self.install_frame, textvariable=self.instruction_label, fg="white", bg=snapeda_color, justify=tk.CENTER, font=("Open Sans", "13"))
            self.install_instructions_label.grid(row=2, column=0, sticky="NEW")
        
            install_thread = threading.Thread(target=self.installation_process)
            install_thread.start()
        else:
            LoginScreen(self.parent)

def boot_plugin():
    master = tk.Tk()
    master.geometry("458x721")
    master.minsize(width=458, height=721)
    master.version = version
    InstallScreen(master)
    tk.mainloop()


for_production = True
version = '0.0.2'

try:
    if sys.argv[1] == 'standalone':
        for_production = False
except:
    pass

if for_production:
    not_mac = platform.mac_ver()[0] == ""
    if not_mac:
        import pcbnew

        class SnapEDAPlugin(pcbnew.ActionPlugin):
            def defaults(self):
                self.name = "SnapEDA"
                self.category = "A descriptive category name"
                self.description = "A description of the plugin and what it does"
                self.show_toolbar_button = False  # Optional, defaults to False

            def Run(self):
                # The entry function of the plugin that is executed on user action
                plugin_thread = threading.Thread(target=boot_plugin)
                plugin_thread.setDaemon(True)
                plugin_thread.start()

    if not_mac:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        SnapEDAPlugin().register()  # Instantiate and register to Pcbnew
    else:
        master = tk.Tk()
        master.geometry("458x721")
        master.minsize(width=458, height=721)
        master.version = version
        InstallScreen(master)
        tk.mainloop()

else:
    master = tk.Tk()
    master.geometry("458x721")
    master.minsize(width=458, height=721)
    master.version = version
    InstallScreen(master)
    tk.mainloop()