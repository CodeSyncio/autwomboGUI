# ---<imports>---
import os
import threading
import time
import customtkinter
import webbrowser
from urllib.parse import urlparse, unquote
import requests
import threading
from colorama import init, Fore


class AutWombGUI:
    def __init__(self) -> None:

        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("dark-blue")

        # static values
        self.APIKEY = "AIzaSyDCvp5MTJLUdtBYEKYWXJrlLzu1zuKM6Xw"

        self.STYLE_IDS = {
            "realistic": 32,
            "expressionism": 77,
            "figure": 76,
            "hdr": 52,
            "spectral": 63,
            "comic": 45,
            "soft touch": 71,
            "splatter": 74,
            "flora": 68,
            "diorama": 65,
            "abstract": 67,
            "fantastical": 61,
            "vector": 60,
            "bad trip": 57,
            "cartoonist": 58,
            "meme": 44,
            "isometric": 55,
            "retro-futurism": 54,
            "analogue": 53,
            "paint": 50,
            "polygon": 49,
            "gouache": 48,
            "ink": 38,
            "line-art": 47,
            "anime": 46,
            "malevolent": 40,
            "surreal": 37,
            "unrealistic": 42,
            "throwback": 35,
            "street art": 41,
            "no style": 3,
            "ghibli": 22,
            "melancholic": 28,
            "pandora": 39,
            "daydream": 36,
            "provenance": 17,
            "arcane": 34,
            "toasty": 31,
            "rose gold": 18,
            "wuhtercuhler": 16,
            "etching": 14,
            "mystical": 11,
            "dark fantasy": 10,
            "psychic": 9,
            "hd": 7,
            "vibrant": 6,
            "fantasy art": 5,
            "steampunk": 4,
            "festive": 12,
            "synthwave": 1,
            "ukiyoe": 2}

        self.STYLES = sorted([i for i in self.STYLE_IDS])
        self.TOKEN = self.createToken()['idToken']
        self.emergencystop = False

    def createToken(self):

        s = requests.Session()
        r = s.post("https://firebaseinstallations.googleapis.com/v1/projects/paint-prod/installations", headers={"Content-Type": "application/json", "x-goog-api-key": self.APIKEY}, json={
            "appId": "1:181681569359:web:277133b57fecf57af0f43a",
            "authVersion": "FIS_v2",
            "sdkVersion": "w:0.5.1",
        })
        r2 = s.post(
            "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={}".format(self.APIKEY))

        return r2.json() if r.status_code == 200 else r.status_code

    def ToWebHook(self, data, path):
        if len(self.GUIHook.get()) != 0:
            fp = open(path, 'rb')
            resp = requests.post(self.GUIHook.get(), files={
                                 "file": fp}, data={"content": data})
            fp.close()
        else:
            pass

    def downloadFile(self, url):
        return open(unquote(urlparse(url).path.split("/")[-1]), "wb").write(requests.get(url).content)

    def checkstat(self, idparam):
        return requests.get(f"https://paint.api.wombo.ai/api/tasks/{idparam}", headers={"authorization": "bearer " + str(self.TOKEN)}).json()

    def grab(self, text, style, fn, amount):

        import requests
        r1 = requests.post("https://paint.api.wombo.ai/api/v2/tasks", json={"is_premium": False, "input_spec": {"prompt": text, "style": self.STYLE_IDS[style.lower()], "display_freq": 10}},
                           headers={"authorization": "bearer " + str(self.TOKEN),
                                    "Content-Type": "text/plain;charset=UTF-8"}).json()
        time.sleep(2)
        while True:
            time.sleep(0.5)
            status = requests.get(f"https://paint.api.wombo.ai/api/tasks/{r1['id']}", headers={
                                  "authorization": "bearer " + str(self.TOKEN)}).json()
            if "completed" in status['state']:
                break

        time.sleep(10)
        r2 = requests.get(f"https://paint.api.wombo.ai/api/tasks/{r1['id']}", headers={
                          "authorization": "bearer " + str(self.TOKEN)}).json()
        downloadurl = r2['result']['final']
        imagefile = requests.get(downloadurl)
        image_name = text.replace(" ", "_").lower()
        image_name = image_name + "-" + str(amount)
        with open(os.path.join(os.getcwd(), fn, image_name+".jpg"), 'wb') as f:
            f.write(imagefile.content)
        print(Fore.GREEN +
              f"SUCCES | Completed image [{amount}] with ID [{r1['id']}]")

        if self.GUIHook.get() != "":
            self.ToWebHook(
                f"**input**: `{image_name}` | **style**: `{style}` | **iter** : `{str(amount)}`", f"{os.getcwd()}\\{fn}\\{image_name}.jpg")

    def GetAIImages(self):

        global mandethrottle
        self.display_text.set(
            f'>starting generation with settings:prompt = {self.GUIprompt.get()} | Amount = {str(self.GUIamount.get())} | style = {self.GUIstyle.get()} | Folder name = {self.GUIfoldername.get()}')
        time.sleep(3)

        print(Fore.LIGHTBLACK_EX+f"{', '.join(self.STYLES)}")
        style = self.GUIstyle.get()
        text = self.GUIprompt.get()
        am = int(self.GUIamount.get())
        fn = self.GUIfoldername.get()
        try:
            os.mkdir(os.path.join(os.getcwd(), fn))
        except:
            pass
        for i in range(int(am)):
            if self.emergencystop == True:
                self.display_text.set(
                    '>child received termination instructions')
                break
            self.display_text.set(
                f">Generating image [{i+1}]  ({str(round((i+1)/int(am)*100))}%)")
            threading.Thread(target=self.grab, args=(
                (text), (style), (fn), (i))).start()

            print(Fore.CYAN+f"THREAD | New thread started for image [{i}]")

            if int(am) <= 10:
                pass
            else:
                time.sleep(0.5)
        time.sleep(5)
        self.display_text.set('>Done generating images')
        print(Fore.LIGHTGREEN_EX +
              f"SENT   | All requests sent for [{am}] images with prompt [{text}] and style [{style}]")
        time.sleep(5)

    def hardterm(self):

        self.emergencystop = True
        self.display_text.set('>hard termination done')

    def startproc(self):
        if len(self.GUIprompt.get()) != 0 and len(self.GUIamount.get()) != 0 and len(self.GUIfoldername.get()) != 0 and len(self.GUIfoldername.get()) != 0 and len(self.GUIstyle.get()) != 0:
            threading.Thread(target=self.GetAIImages, args=()).start()
        else:
            self.display_text.set(
                '>please fill in the PROMPT , AMOUNT , STYLE and FOLDER_NAME')

    def starttermproc(self):
        threading.Thread(target=self.hardterm, args=()).start()

    def openbrowser(self):
        webbrowser.open('https://github.com/CodeSyncio')

    def dethrot(self):
        global mandethrottle
        mandethrottle = True

    def main(self):
        init(autoreset=True)
        usrenv = os.getenv('username')
        mandethrottle = False
        throttled = False
        emergencystop = False
        mf = customtkinter.CTk()

        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("dark-blue")
        mf.title('AI image webscraper - CodeSyncio')
        customtkinter.CTkLabel(mf, text='Prompt:', anchor=customtkinter.W).grid(
            row=0, sticky='w', column=0)
        customtkinter.CTkLabel(mf, text='Iterations:', anchor=customtkinter.W).grid(
            row=1, sticky='w', column=0)
        customtkinter.CTkLabel(mf, text='Style:', anchor=customtkinter.W).grid(
            row=2, sticky='w', column=0)
        customtkinter.CTkLabel(mf, text='folder name:', anchor=customtkinter.W).grid(
            row=3, sticky='w', column=0)
        customtkinter.CTkLabel(mf, text='webhook (optional):', anchor=customtkinter.NW).grid(
            row=5, sticky='w', column=0)
        self.display_text = customtkinter.StringVar()
        self.display_text.set(f">")
        out = customtkinter.CTkLabel(mf, textvariable=self.display_text, width=420, height=200,
                                     anchor=customtkinter.NW, wraplength=200).grid(row=6, column=1, sticky='w')
        self.GUIprompt = customtkinter.CTkEntry(
            mf, width=400, placeholder_text="the eiffel tower landing on the moon...")
        self.GUIamount = customtkinter.CTkEntry(
            mf, width=60, placeholder_text="")
        self.GUIstyle = customtkinter.CTkComboBox(
            mf, width=200, values=self.STYLES)
        self.GUIHook = customtkinter.CTkEntry(
            mf, width=400, placeholder_text="https://discord.com/api/webhooks/...")
        self.GUIfoldername = customtkinter.CTkEntry(mf, width=200)
        self.GUIprompt.grid(row=0, column=1, sticky='w')
        self.GUIamount.grid(row=1, column=1, sticky='w')
        self.GUIstyle.grid(row=2, column=1, sticky='w')
        self.GUIfoldername.grid(row=3, column=1, sticky='w')
        self.GUIHook.grid(row=5, column=1, sticky='w')
        self.genbutton = customtkinter.CTkButton(
            mf, text="Generate", width=10, command=self.startproc, fg_color='gray', state='disabled', hover_color='DarkGreen')
        self.genbutton.grid(row=6, column=0, sticky='n')

        hardterminate = customtkinter.CTkButton(mf, text="terminate", width=10, command=self.starttermproc,
                                                fg_color='red', hover_color='DarkRed').grid(row=6, column=0, sticky='s')
        
        mysite = customtkinter.CTkButton(
            mf, text='My github', command=self.openbrowser, width=10).grid(row=8, column=0)
        self.GUIprompt.bind('<Leave>', self.checkstate)
        self.GUIamount.bind('<Leave>', self.checkstate)
        self.GUIstyle.bind('<Leave>', self.checkstate)
        self.GUIfoldername.bind('<Leave>', self.checkstate)
        self.GUIprompt.bind('<Enter>', self.checkstate)
        self.GUIamount.bind('<Enter>', self.checkstate)
        self.GUIstyle.bind('<Enter>', self.checkstate)
        self.GUIfoldername.bind('<Enter>', self.checkstate)

        mf.mainloop()

    def checkstate(self, event):

        if len(self.GUIamount.get()) != 0 and len(self.GUIprompt.get()) != 0 and len(self.GUIstyle.get()) != 0 and len(self.GUIfoldername.get()) != 0:
            self.genbutton.configure(state="normal")
            self.genbutton.configure(fg_color='green')
        else:
            self.genbutton.configure(state="disabled")
            self.genbutton.configure(fg_color='gray')


if __name__ == "__main__":
    app = AutWombGUI()
    app.main()
