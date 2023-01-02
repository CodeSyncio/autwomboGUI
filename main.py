#---<imports>---
import os;import random;import threading;import time
import customtkinter
import webbrowser
import requests;from io import BytesIO;import threading;from PIL import Image as PILIMAGE;from colorama import init,Fore;from selenium import webdriver;from selenium.webdriver.common.by import By;from selenium.webdriver.support import expected_conditions as EC;from selenium.webdriver.support.ui import WebDriverWait;from selenium.webdriver.common.action_chains import ActionChains;from selenium import webdriver;from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
#----------<CONFIG>----------#
FIREFOX_PATH = f"{os.getcwd()}\\dependencies\\firefox\\waterfox.exe"
GECKODRIVER_PATH = f"{os.getcwd()}\\dependencies\\gecko\\geckodriver.exe"
VERS = "v2.0.5"
customtkinter.set_appearance_mode("System") 
customtkinter.set_default_color_theme("dark-blue")  

#static values
XPATH_TEXT_FIELD = '//*[@id="blur-overlay"]/div/div/div[1]/div[1]/div[1]/div[1]/div[1]/input'
XPATH_IMG_STYLE = '//img[@class="Thumbnail__StyledThumbnail-sc-p7nt3c-0 hxvLKC"'
XPATH_IMG_STYLES_CONTAINER = '//div[@class="Thumbnail__StyledThumbnailContainer-sc-p7nt3c-1 gqZQZu"]'
XPATH_BTN_GENERATE = '//*[@id="blur-overlay"]/div/div/div/div[2]/button'
XPATH_RESULT_IMG = '//img[@class="ArtCard__CardImage-sc-67t09v-2 dOXnUm"]'
XPATH_BTN_GO_BACK = '//*[@id="blur-overlay"]/div/div/div[1]/div[1]/div/button'
CROP_COORDINATES = (81, 232, 999, 1756)
STYLES = ["Realistic","Bad Trip","Cartoonist","HDR","Meme", "Isometric","Analogue","Retro-Futurism",
            "Paint","Polygon","Gouache","Line-Art","Malevolent","Surreal","Throwback", "Street Art",
            "No Style", "Ghibli", "Melancholic", "Pandora", "Daydream", "Provenance", "Arcane", "Toasty",
            "Transitory", "Etching", "Mystical", "Dark Fantasy", "Psychic", "HD", "Vibrant", "Fantasy Art",
            "Steampunk", "Rose Gold", "Wuhtercuhler", "Psychedelic", "Synthwave", "Ukiyoe"]

def ToWebHook(data,path,uri):
    if len(GUIHook.get()) !=0:
        fp = open(path,'rb')
        resp = requests.post(uri,files={"file":fp},data={"content":data})
        fp.close()
    else:
        pass
    
def get_element_from_xpath( xpath, dr,timeout=30):
    return WebDriverWait(dr, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))

def crop_an_save_image( image_src, style, item,fn,startbench):
        image_name = item.replace(" ", "_").lower()
        nb_of_same_images = len([name for name in os.listdir(os.getcwd()+'\\'+fn) if name.split("-")[0] == image_name])
        image_name = image_name + "-" + str(nb_of_same_images) + ".png"
        image = PILIMAGE.open(BytesIO(requests.get(image_src).content))
        image = image.crop(CROP_COORDINATES)
        image.save(f"{fn}/{image_name}")
        end = time.perf_counter()
        gentime = round(end - startbench,3)
        ToWebHook(f"**input**: `{image_name}` | **style**: `{style}` | **iter** : `{str(nb_of_same_images)}` | **Generation time** : `{str(gentime)}`",f"{fn}/{image_name}",GUIHook.get())

def grab(text,style,fn):
    start =time.perf_counter()
    binary = FirefoxBinary(FIREFOX_PATH)
    driver = webdriver.Firefox(firefox_binary=binary, executable_path=GECKODRIVER_PATH,service_log_path=os.devnull)
    global throttled
    actions = ActionChains(driver)
    driver.get("https://app.wombo.art/")
    try:
        image_style = get_element_from_xpath(f'{XPATH_IMG_STYLE} and @alt="{style}"]',driver)
        coordinates = image_style.location_once_scrolled_into_view 
        driver.execute_script('window.scrollTo({}, {});'.format(coordinates['x'], coordinates['y']))
        actions.move_to_element(image_style).perform()

        image_style.click()
        time.sleep(1)
        input_text =get_element_from_xpath(XPATH_TEXT_FIELD,driver)
        input_text.clear()
        input_text.send_keys(text)
        time.sleep(1)
        generate_button = get_element_from_xpath(XPATH_BTN_GENERATE,driver)
        generate_button.click()
        
        try:
            result_image = get_element_from_xpath(XPATH_RESULT_IMG,driver ,80)
        except :
            driver.close()
            throttled = True
            
        image_src = result_image.get_attribute("src")
        crop_an_save_image(image_src, style, text,fn,start)
        throttled = False

        time.sleep(2)
        driver.close()
    except:
        throttled = True
    
def GetAIImages():
    global throttled
    throttled = False
    global mandethrottle
    global togglenotif
    display_text.set(f'>starting generation with settings:prompt = {GUIprompt.get()} | Amount = {str(GUIamount.get())} | style = {GUIstyle.get()} | Folder name = {GUIfoldername.get()}')
    time.sleep(3)
    init(autoreset=True)
    os.system('cls')
    print(Fore.LIGHTBLACK_EX+f"{', '.join(STYLES)}")
    style = GUIstyle.get()
    text = GUIprompt.get()
    am = int(GUIamount.get())
    fn = GUIfoldername.get()
    try:
        os.mkdir(os.getcwd()+'\\'+fn)
    except:
        pass
    for i in range(int(am)):
        if emergencystop == True:
            display_text.set('>child received termination instructions')
            break
        
        os.system('cls')
        display_text.set(f">Generating image [{i+1}]  ({str(round((i+1)/int(am)*100))}%)")
        threading.Thread(target=grab,args=((text),(style),(fn))).start()
        if int(am) <=10:
            time.sleep(random.randint(2,4))
        else:
            time.sleep(random.randint(7,10)) 
        if throttled == True:
            os.system(f'taskkill /im {os.path.split(FIREFOX_PATH)[1]} /f')
            for i in range (300):
                time.sleep(1)
                display_text.set(f'>Detected throttling, pausing {300-i} seconds... To bypass, enable a vpn and press the unthrottle button')
                if mandethrottle == True:
                    display_text.set(f'>overwriting throttle detection and resuming generation...')
                    time.sleep(3)
                    mandethrottle =False
                    break
            throttled = False 
    display_text.set('>Done generating images')
    time.sleep(5)
    display_text.set(f">styles:{', '.join(STYLES)}")
    
def hardterm():
    global emergencystop
    emergencystop = True
    os.system(f'taskkill /im {os.path.split(FIREFOX_PATH)[1]} /f')
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
    
    hardterminate=customtkinter.CTkButton(mf, text="hard term",width=10,command=starttermproc,fg_color='red',hover_color='DarkRed').grid(row=6,column=0,sticky='s')
    manualdethrottle=customtkinter.CTkButton(mf, text="unthrottle",width=10,command=dethrot,fg_color='orange',hover_color='DarkOrange').grid(row=7,column=0,sticky='n')
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
