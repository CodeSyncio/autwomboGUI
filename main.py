#---<imports>---
import os;import random;import threading;import time
import customtkinter
import webbrowser
from urllib.parse import urlparse, unquote
import requests;from io import BytesIO;import threading;from PIL import Image as PILIMAGE;from colorama import init,Fore;from selenium import webdriver;from selenium.webdriver.common.by import By;from selenium.webdriver.support import expected_conditions as EC;from selenium.webdriver.support.ui import WebDriverWait;from selenium.webdriver.common.action_chains import ActionChains;from selenium import webdriver;from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

customtkinter.set_appearance_mode("System") 
customtkinter.set_default_color_theme("dark-blue")  

#static values
APIKEY ="AIzaSyDCvp5MTJLUdtBYEKYWXJrlLzu1zuKM6Xw"

STYLE_IDS={"realistic":32,
           "expressionism":77,
           "figure":76,
           "hdr": 52,
           "spectral":63,
           "comic": 45,
           "soft touch":71,
           "splatter":74,
           "flora":68,
           "diorama":65,
           "abstract":67,
           "fantastical":61,
           "vector":60,
           "bad trip":57,
           "cartoonist":58,
           "meme": 44,
           "isometric":55,
           "retro-futurism":54,
           "analogue":53,
           "paint":50,
           "polygon":49,
           "gouache":48,
           "ink":38,
           "line-art": 47,
           "anime":46,
           "malevolent":40,
           "surreal":37,
           "unrealistic":42,
           "throwback": 35,
           "street art":41,
           "no style":3,
           "ghibli": 22,
           "melancholic": 28,
           "pandora":39,
           "daydream":36,
           "provenance": 17,
           "arcane":34,
           "toasty":31,
           "rose gold":18,
           "wuhtercuhler":16,
           "etching":14,
           "mystical": 11,
           "dark fantasy": 10,
           "psychic":9,
           "hd": 7,
           "vibrant": 6,
           "fantasy art":5,
           "steampunk":4,
           "festive":12,
           "synthwave": 1,
           "ukiyoe":2
           }

STYLES = sorted([i for i in STYLE_IDS])

def createToken():
    global APIKEY
    s = requests.Session()
    r = s.post("https://firebaseinstallations.googleapis.com/v1/projects/paint-prod/installations", headers={"Content-Type": "application/json", "x-goog-api-key": APIKEY}, json={
        "appId": "1:181681569359:web:277133b57fecf57af0f43a",
        "authVersion": "FIS_v2",
        "sdkVersion": "w:0.5.1",
    })
    r2 = s.post("https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={}".format(APIKEY))
    
    return r2.json() if r.status_code == 200 else r.status_code

TOKEN = createToken()['idToken']

def ToWebHook(data,path):
    if len(GUIHook.get()) !=0:
        fp = open(path,'rb')
        resp = requests.post(GUIHook.get(),files={"file":fp},data={"content":data})
        fp.close()
    else:
        pass
    

def downloadFile(url):
    return open(unquote(urlparse(url).path.split("/")[-1]), "wb").write(requests.get(url).content)
def checkstat(idparam):
    return requests.get(f"https://paint.api.wombo.ai/api/tasks/{idparam}", headers={"authorization": "bearer " + str(TOKEN)}).json()

def grab(text,style,fn,amount):
    
    import requests
    r1=requests.post("https://paint.api.wombo.ai/api/v2/tasks", json={"is_premium":False,"input_spec":{"prompt":text,"style":STYLE_IDS[style.lower()],"display_freq":10}},
            headers={"authorization": "bearer " + str(TOKEN),
                     "Content-Type": "text/plain;charset=UTF-8"}).json()
    time.sleep(2)
    while True:
        time.sleep(0.5)
        status = requests.get(f"https://paint.api.wombo.ai/api/tasks/{r1['id']}", headers={"authorization": "bearer " + str(TOKEN)}).json()
        if "completed" in status['state']:
            break
    
    time.sleep(10)
    r2 = requests.get(f"https://paint.api.wombo.ai/api/tasks/{r1['id']}", headers={"authorization": "bearer " + str(TOKEN)}).json()
    downloadurl=r2['result']['final']
    imagefile = requests.get(downloadurl)
    image_name = text.replace(" ", "_").lower()
    image_name = image_name + "-" + str(amount)
    with open(os.path.join(os.getcwd()+"\\"+fn+"\\"+image_name+".jpg"),'wb') as f:
        f.write(imagefile.content)
    print(Fore.GREEN+f"SUCCES | Completed image [{amount}] with ID [{r1['id']}]")
    
    if GUIHook.get() !="":
        ToWebHook(f"**input**: `{image_name}` | **style**: `{style}` | **iter** : `{str(amount)}`",f"{os.getcwd()}\\{fn}\\{image_name}.jpg")

def GetAIImages():
    
    global mandethrottle
    display_text.set(f'>starting generation with settings:prompt = {GUIprompt.get()} | Amount = {str(GUIamount.get())} | style = {GUIstyle.get()} | Folder name = {GUIfoldername.get()}')
    time.sleep(3)
    
    print(Fore.LIGHTBLACK_EX+f"{', '.join(STYLES)}")
    style = GUIstyle.get()
    text = GUIprompt.get()
    am = int(GUIamount.get())
    fn = GUIfoldername.get()
    try:
        os.mkdir(os.path.join(os.getcwd()+'\\'+fn))
    except:
        pass
    for i in range(int(am)):
        if emergencystop == True:
            display_text.set('>child received termination instructions')
            break
        display_text.set(f">Generating image [{i+1}]  ({str(round((i+1)/int(am)*100))}%)")
        threading.Thread(target=grab,args=((text),(style),(fn),(i))).start()
        
        print(Fore.CYAN+f"THREAD | New thread started for image [{i}]")
                          
        if int(am) <=10:
            pass
        else:
            time.sleep(0.5)
    time.sleep(5)
    display_text.set('>Done generating images')
    print(Fore.LIGHTGREEN_EX+f"DONE  | Completed request for [{am}] images with prompt [{text}] and style [{style}]")
    time.sleep(5)
    
    
def hardterm():
    global emergencystop
    emergencystop = True
    display_text.set('>hard termination done')

def startproc():
    if len(GUIprompt.get()) != 0 and len(GUIamount.get())!=0 and len(GUIfoldername.get())!=0 and len(GUIfoldername.get())!=0 and len(GUIstyle.get())!=0:
        threading.Thread(target=GetAIImages,args=()).start()
    else:
        display_text.set('>please fill in the PROMPT , AMOUNT , STYLE and FOLDER_NAME')

def starttermproc():
    threading.Thread(target=hardterm,args=()).start()
    
def openbrowser():
    webbrowser.open('https://github.com/CodeSyncio')
    
def dethrot():
    global mandethrottle
    mandethrottle = True

if __name__ == "__main__":
    init(autoreset=True)
    usrenv = os.getenv('username')
    mandethrottle = False
    throttled = False
    emergencystop = False
    mf=customtkinter.CTk()
    
    customtkinter.set_appearance_mode("System") 
    customtkinter.set_default_color_theme("dark-blue")  
    mf.title('AI image webscraper - CodeSyncio')
    customtkinter.CTkLabel(mf, text='Prompt:',anchor=customtkinter.W).grid(row=0,sticky='w',column=0)
    customtkinter.CTkLabel(mf, text='Iterations:',anchor=customtkinter.W).grid(row=1,sticky='w',column=0)
    customtkinter.CTkLabel(mf, text='Style:',anchor=customtkinter.W).grid(row=2,sticky='w',column=0)
    customtkinter.CTkLabel(mf, text='folder name:',anchor=customtkinter.W).grid(row=3,sticky='w',column=0)
    customtkinter.CTkLabel(mf, text='webhook (optional):',anchor=customtkinter.NW).grid(row=5,sticky='w',column=0)
    display_text = customtkinter.StringVar()
    display_text.set(f">")
    out = customtkinter.CTkLabel(mf, textvariable=display_text,width=420,height=200,anchor=customtkinter.NW,wraplength=200).grid(row=6,column=1,sticky='w')
    GUIprompt = customtkinter.CTkEntry(mf,width=400,placeholder_text="the eiffel tower landing on the moon...")
    GUIamount = customtkinter.CTkEntry(mf,width=60,placeholder_text="")
    GUIstyle = customtkinter.CTkComboBox(mf,width=200,values=STYLES)
    GUIHook = customtkinter.CTkEntry(mf,width=400,placeholder_text="https://discord.com/api/webhooks/...")
    GUIfoldername = customtkinter.CTkEntry(mf,width=200)
    GUIprompt.grid(row=0, column=1,sticky='w')
    GUIamount.grid(row=1, column=1,sticky='w')
    GUIstyle.grid(row=2, column=1,sticky='w')
    GUIfoldername.grid(row=3, column=1,sticky='w')
    GUIHook.grid(row=5, column=1,sticky='w')
    genbutton=customtkinter.CTkButton(mf, text="Generate",width=10,command=startproc,fg_color='gray',state='disabled',hover_color='DarkGreen')
    genbutton.grid(row=6,column=0,sticky='n')
    
    hardterminate=customtkinter.CTkButton(mf, text="terminate",width=10,command=starttermproc,fg_color='red',hover_color='DarkRed').grid(row=6,column=0,sticky='s')
    #old piece of code
    # manualdethrottle=customtkinter.CTkButton(mf, text="unthrottle",width=10,command=dethrot,fg_color='orange',hover_color='DarkOrange').grid(row=7,column=0,sticky='n')
    mysite = customtkinter.CTkButton(mf,text='My github',command=openbrowser,width=10).grid(row=8,column=0)
    
    def checkstate(event):
        global genbutton
        if len(GUIamount.get()) !=0 and len(GUIprompt.get()) !=0 and len(GUIstyle.get()) !=0 and len(GUIfoldername.get()) !=0:
            genbutton.configure(state = "normal")
            genbutton.configure(fg_color='green')
        else:
            genbutton.configure(state = "disabled")
            genbutton.configure(fg_color='gray')
            
    GUIprompt.bind('<Leave>',checkstate)
    GUIamount.bind('<Leave>',checkstate)
    GUIstyle.bind('<Leave>',checkstate)
    GUIfoldername.bind('<Leave>',checkstate)
    GUIprompt.bind('<Enter>',checkstate)
    GUIamount.bind('<Enter>',checkstate)
    GUIstyle.bind('<Enter>',checkstate)
    GUIfoldername.bind('<Enter>',checkstate)
    
    mf.mainloop()
