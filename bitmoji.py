import tkinter as tk
from tkinter import ttk
import json
import subprocess
from PIL import ImageTk, Image
import zipfile
import io
import os
import sys

PER_LINE = int(sys.argv[1])
LINES = int(sys.argv[2])
TMPFILE = sys.argv[5]
SHOWID = str(10214655)

class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling"""

    def vscrollbar_set(self, first, last):
        self.vscrollbar.set(first, last)
        if first != "0.0" and last == "1.0":
            self.master.frame_bottom_preload()

    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=self.vscrollbar_set)  # yscrollcommand=vscrollbar.set

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior():
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', lambda e: _configure_interior())

        def _configure_canvas():
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', lambda e: _configure_canvas())

        self.interior.bind('<Enter>', lambda e: self._bound_to_mousewheel())
        self.interior.bind('<Leave>', lambda e: self._unbound_to_mousewheel())
        self.canv = canvas
        self.vscrollbar = vscrollbar

    def _bound_to_mousewheel(self):
        self.canv.bind_all("<Button-4>", lambda e: self._on_mousewheel_up())
        self.canv.bind_all("<Button-5>", lambda e: self._on_mousewheel_down())

    def _unbound_to_mousewheel(self):
        self.canv.unbind_all("<Button-4>")
        self.canv.unbind_all("<Button-5>")

    def _on_mousewheel_down(self):
        self.canv.yview_scroll(1, "units")

    def _on_mousewheel_up(self):
        self.canv.yview_scroll(-1, "units")

class SampleApp(tk.Tk):
    @staticmethod
    def strip_smiles(tweet):
        char_list = [tweet[j] for j in range(len(tweet)) if ord(tweet[j]) in range(65536)]
        tweet = ''
        for j in char_list:
            tweet = tweet + j
        return tweet

    def frame_bottom_preload(self):
        for i in range(4):
            frames_len = len(self.frames)
            if len(self.stickers) > frames_len * PER_LINE:
                self.add_line(self.stickers[frames_len * PER_LINE: (frames_len + 1) * PER_LINE])
        pass

    def sticker_select(self, sticker):
        if sticker[0:4] == "res.":
            try:
                f = open("nowres.txt", 'w')
                f.write(sticker)
                f.close()
            except OSError:
                pass
            
            self.zip = zipfile.ZipFile(sticker, "r")
            self.stickers_init()
            self.sv.set("")
        
        else:
            with open(TMPFILE, 'wb') as f:
                f.write(self.zip.read("webp/" + sticker + ".webp"))
                f.close()
                print(TMPFILE) # use in wrapper script
                # subprocess.call(["./select", tmp_file])
                
            self.destroy()

    def sticker_click(self, sticker):
        self.sel_frame = tk.Frame(self)
        self.sel_frame.configure(bg='white')
        self.sel_frame['highlightthickness'] = 5
        self.sel_frame['highlightcolor'] = "#78538b"
        
        maxw = self.winfo_width() - 150
        
        if sticker[0:4] == "res.":
            pzip = zipfile.ZipFile(sticker, "r")
            img = Image.open(io.BytesIO(pzip.read("webp/" +  SHOWID + ".webp")))
            sticker = SHOWID
        else:
            img = Image.open(io.BytesIO(self.zip.read("webp/" + sticker + ".webp")))
            
        self.sel_frame_img = ImageTk.PhotoImage(img)
        ttk.Label(self.sel_frame, image=self.sel_frame_img).pack(padx=142, pady=(20, 0))
        ttk.Label(self.sel_frame).pack(pady=5)

        txt_frame = tk.Frame(self.sel_frame)
        txt_frame.pack(pady=(0, 20)) 
        txt_frame.configure(bg='white')

        if "alt_text" in self.imoji[sticker]:
            l_text = self.imoji[sticker]["alt_text"]
            if "descriptive_alt_text" in self.imoji[sticker]:
                l_text = self.imoji[sticker]["descriptive_alt_text"]
            l_text = self.strip_smiles(l_text)

            t_frame = tk.Frame(txt_frame)
            t_frame.pack(fill=tk.X, expand=tk.TRUE, padx=20)
            t_frame.configure(bg='white')
            ttk.Label(t_frame, text="Desc: ", font='Helvetica 16 bold').pack(side=tk.LEFT, padx=5)
            ttk.Label(t_frame, text=l_text, wraplength=maxw, font='Helvetica 14 italic').pack(side=tk.LEFT, padx=5,
                                                                                             fill=tk.X, expand=tk.TRUE)

        if len(self.imoji[sticker]["tags"]) > 0:
            l_text = ""
            for i in self.imoji[sticker]["tags"]:
                t = self.strip_smiles(i)
                if t != "":
                    l_text += ", " + t
            l_text = l_text[2:]

            t_frame = tk.Frame(txt_frame)
            t_frame.pack(fill=tk.X, expand=tk.TRUE, padx=20)
            t_frame.configure(bg='white')
            ttk.Label(t_frame, text="Tags: ", font='Helvetica 16 bold').pack(side=tk.LEFT, padx=5)
            ttk.Label(t_frame, text=l_text, wraplength=maxw, font='Helvetica 14 italic').pack(side=tk.LEFT, padx=5,
                                                                                             fill=tk.X, expand=tk.TRUE)

        if len(self.imoji[sticker]["categories"]) > 0:
            l_text = ""
            for i in self.imoji[sticker]["categories"]:
                l_text += ", #" + i[4:]
            l_text = l_text[2:]

            t_frame = tk.Frame(txt_frame)
            t_frame.pack(fill=tk.X, expand=tk.TRUE, padx=20)
            t_frame.configure(bg='white')
            ttk.Label(t_frame, text="Cats: ", font='Helvetica 16 bold').pack(side=tk.LEFT, padx=5)
            ttk.Label(t_frame, text=l_text, wraplength=maxw, font='Helvetica 14 italic').pack(side=tk.LEFT, padx=5,
                                                                                             fill=tk.X, expand=tk.TRUE)
                                                                                             
        self.sel_frame.update()
        h = self.sel_frame.winfo_reqheight()
        h = (self.winfo_height() - h) // 2 - 5
        w = self.sel_frame.winfo_reqwidth()
        w = (self.winfo_width() - w) // 2 - 5
        self.sel_frame.place(x=w, y=h )

    def sticker_relize(self):
        self.sel_frame.destroy()

    def txt_change(self, sv):
        txt = sv.get()
        if len(txt) >= 2:
            txt = txt.replace("#", "_")
            stickers = []
            for t in self.imoji:
                i = self.imoji[t]
                flag = False
                for j in i['tags']:
                    if txt in " " + j + " ":
                        flag = True
                        break

                if not flag and "categories" in i:
                    for j in i['categories']:
                        if txt.replace(" ", "_") in "_" + j[4:] + "_":
                            flag = True
                            break

                if not flag and "alt_text" in i:
                    if txt in " " + i["alt_text"] + " ":
                        flag = True

                if not flag and "descriptive_alt_text" in i:
                    if txt in " " + i["descriptive_alt_text"] + " ":
                        flag = True

                if flag:
                    stickers.append(i['comic_id'])

            self.set_stickers(stickers)
        else:
            self.set_stickers(self.all_stickers)

        self.sel['text'] = "<all>"

    def add_line(self, stickers):
        t_frame = tk.Frame(self.frame.interior)
        t_frame.configure(bg="white")

        for i in range(PER_LINE):
            if i == len(stickers):
                stickers.append("0")

            if stickers[i][0:4] == "res.":
                try:
                    pzip = zipfile.ZipFile(stickers[i], "r")
                    t_image = tk.PhotoImage(data=pzip.read("128/" + SHOWID + ".png"))
                except KeyError:
                    t_image = self.empty
                    stickers[i] = "0"
                    
            elif stickers[i] == "0":
                t_image = self.empty
            else:
                try:
                    t_image = tk.PhotoImage(data=self.zip.read("128/" + stickers[i] + ".png"))
                except KeyError:
                    t_image = self.empty
                    stickers[i] = "0"

            self.imgs.append(t_image)

            t_label = ttk.Label(t_frame, image=t_image)
            
            if stickers[i] != "0":
                t_label.bind("<Button-1>", lambda e, st=stickers[i]: self.sticker_select(st))
                t_label.bind("<Button-3>", lambda e, st=stickers[i]: self.sticker_click(st))
                t_label.bind("<ButtonRelease-3>", lambda e: self.sticker_relize())
            t_label.pack(side=tk.LEFT, padx=15, pady=15)

        t_frame.pack()
        self.frames.append(t_frame)

    def set_stickers(self, stickers):
        self.stickers = stickers
        self.imgs = []

        for i in self.frames:
            i.destroy()
        self.frames = []

        for i in range(LINES + 1 - (len(stickers) <= LINES * PER_LINE)):
            self.add_line(stickers[i * PER_LINE: (i + 1) * PER_LINE])

        self.frame.canv.xview_moveto(0)
        self.frame.canv.yview_moveto(0)

    # def dragwin(self, event):
    #    self.geometry(f'+{event.x_root}+{event.y_root}')

    def select_item(self):
        self.sv.set("")

        value = (self.listbox.get(self.listbox.curselection()))
        self.sel['text'] = value

        stickers = []
        
        if value == "<all>" or value == "<profiles>":
            if value == "<all>":
                stickers = self.all_stickers
            else:
                for f in os.listdir('.'):
                    if f[0:4] == "res.":
                        stickers.append(f)
        else:
            if value[0:1] == '#':
                for t in self.imoji:
                    i = self.imoji[t]
                    if '#mt_' + value[1:] in i['categories']:
                        stickers.append(i['comic_id'])
            else:
                for t in self.imoji:
                    i = self.imoji[t]
                    if '#' + value in i['supertags']:
                        stickers.append(i['comic_id'])
        self.set_stickers(stickers)

        self.listbox.select_clear(0, self.listbox.size())
        self.listbox_frame.place_forget()

    def sel_click(self):
        
        if self.listbox_frame is None:
            self.listbox_frame = tk.Frame(self)
            self.listbox_frame.configure(bg='white', borderwidth=5, highlightthickness=5)

            listbox_items = []
            listbox_items.append('<all>')
            listbox_items.append('<profiles>')
            listbox_items.extend(map(lambda x: x[1:], self.supertags))
            listbox_items.extend(map(lambda x: '#' + x[4:], self.categories))

            self.listbox = tk.Listbox(self.listbox_frame, width=27, height=9, font=('times', 13),
                                      borderwidth=0, highlightthickness=0)
            self.listbox.configure()

            self.listbox.bind('<<ListboxSelect>>', lambda e: self.select_item())
            self.listbox.pack(side="left", fill="y", padx=4)

            self.scrollbar = tk.Scrollbar(self.listbox_frame, orient="vertical")
            self.scrollbar.config(command=self.listbox.yview)
            self.scrollbar.pack(side="right", fill="y")
            self.listbox.config(yscrollcommand=self.scrollbar.set)

            for item in listbox_items:
                self.listbox.insert(tk.END, item)

        self.focus_flag = False
        self.listbox.focus_set()
        self.listbox_frame.place(x=10, y=10)

    def txt_key_callback(self, event):
        if event.char == '\x1B':
            if self.sv.get() == "":
                self.destroy()
            else:
                self.sv.set("")

    def txt_lost_focus(self):
        self.txt.focus_force()
        
    def stickers_init(self):
        js = json.loads(self.zip.read("templates").decode('utf-8'))

        self.imoji = {}
        self.all_stickers = []
        self.categories = []
        self.supertags = []
        
        for i in js['imoji']:
            self.imoji[i['comic_id']] = i
            self.all_stickers.append(i['comic_id'])

        for i in self.imoji:
            for t in self.imoji[i]['supertags']:
                if t not in self.supertags:
                    self.supertags.append(t)

        for i in self.imoji:
            for t in self.imoji[i]['categories']:
                if t not in self.categories:
                    self.categories.append(t)
                    
        self.supertags.sort()
        self.categories.sort()
        

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.imoji = {}
        self.all_stickers = []
        self.categories = []
        self.supertags = []
        
        style = ttk.Style()
        self.scrollbar = None
        self.listbox = None
        self.listbox_frame = None
        self.sel_frame = None
        self.sel_frame_img = None
        self.focus_flag = True

        self.stickers = []
        self.imgs = []
        self.frames = []

        self.title('Bitmoji')
        self.wm_attributes('-type', 'dock')
        # self.update_idletasks()
        
        width = 40 + PER_LINE*(128 + 15*2) # self.winfo_width()
        height = 76 + LINES*(128 + 15*2) # self.winfo_height()
        
        # x = (self.winfo_screenwidth() // 2) - (width // 2)
        # y = (self.winfo_screenheight() // 2) - (height // 2)
        # self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        # self.bind('<B1-Motion>', self.dragwin)
        
        self.geometry('{}x{}+{}+{}'.format(width, height, int(sys.argv[3]), int(sys.argv[4])))

        self.frame = VerticalScrolledFrame(self)
        self.frame.pack(fill=tk.BOTH, expand=tk.TRUE, padx=0, pady=0, side=tk.BOTTOM)

        frame = tk.Frame(self)
        frame.pack(pady=10, fill=tk.X)
        frame.configure(bg='white')

        self.sel = tk.Label(frame, text="<all>", width=34, relief="raised")
        self.sel.configure(bg='white', borderwidth=0, highlightthickness=5)
        self.sel.pack(side=tk.LEFT, padx=10, pady=0, ipady=4)
        self.sel.bind("<Button-1>", lambda e: self.sel_click())

        self.sv = tk.StringVar()
        self.sv.trace("w", lambda name, index, mode, sv1=self.sv: self.txt_change(sv1))
        self.txt = ttk.Entry(frame, textvariable=self.sv, style='pad.TEntry')
        self.txt.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=2)
        ttk.Style().configure('pad.TEntry', padding='5 2 2 2', borderwidth=5, bordertcolor="#ddd")
        self.configure(bg='white')
        self.txt.focus_force()
        # self.txt.focus_set()

        self.txt.bind("<FocusOut>", lambda e: self.txt_lost_focus())
        self.txt.bind('<Key>', self.txt_key_callback)

        # self.X = tk.Label(frame, text="X", relief="raised", bg='white', borderwidth=0, highlightthickness=5)
        # self.X.pack(padx=10, pady=0, side=tk.LEFT, ipady=4, ipadx=10)
        # self.X.bind("<Button-1>", lambda e: self.destroy())

        self.frame.configure(bg="white")
        self.frame.canv.configure(bg="white")
        self.frame.interior.configure(bg="white")
        self.frame.vscrollbar.configure(bg="white")

        style.configure("TLabel", background="white")
        style.configure("TButton", background="white")
        self.configure(bg="white")

        self['highlightthickness'] = 5
        self['highlightcolor'] = "#78538b"
        
        ######
        
        resname = "res.zip"
        try:
            f = open("nowres.txt", 'r')
            resname = f.read()
            f.close()
        except OSError:
            resname = "res.zip"

        self.zip = zipfile.ZipFile(resname, "r")
        self.empty = ImageTk.PhotoImage(Image.new('RGB', (128, 128), (255, 255, 255)))
        self.stickers_init()
        self.set_stickers(self.all_stickers)



app = SampleApp()
app.mainloop()
