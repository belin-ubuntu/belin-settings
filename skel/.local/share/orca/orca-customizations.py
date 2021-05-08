try:
    import orca.input_event # watches for input that Orca recognizes
    import orca.keybindings # Handles binding keystrokes for Orca to use.
    import orca.orca # Imports the main screen reader
    import orca.settings
    import orca.speech # Handles Orca's speaking abilities
    import orca.braille # Displays information in Braille format
except IndexError:
    pass
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
import time
import os, sys
import configparser
import subprocess
from gi.repository import Gtk, Gdk
from urllib.request import urlopen, Request
import ssl
import importlib
if os.path.exists(os.getenv('HOME')+'/.gconf/apps/metacity'):
    os.system('rm -r '+os.getenv('HOME')+'/.gconf/apps/metacity')

def showwindows(script, inputEvent=None):
    import window_switch
    window_switch.windowcontextmenu().displaymenue()
    return True

def show_infocenter(script, inputEvent=None):
    os.system('python3 /usr/share/infocenter/infocenter.py &')
    return True

#Following function increasing master volume with 5 step, and spokening the new changed volume
honap=["január", "február", "március", "április", "május", "június", "július", "augusztus", "szeptember", "október", "november", "december"]
naptoldalek=["elsején", "másodikán", "harmadikán", "negyedikén", "ötödikén", "hatodikán", "hetedikén", "nyolcadikán", "kilencedikén", "tizedikén", "tizeneggyedikén", "tizenkettedikén", "tizenharmadikán", "tizennegyedikén", "tizenötödikén", "tizenhatodikán", "tizenhetedikén", "tizennyolcadikán", "tizenkilencedikén", "huszadikán", "huszoneggyedikén", "huszonkettedikén", "huszonharmadikán", "huszonnegyedikén", "huszonötödikén", "huszonhatodikán", "huszonhetedikén", "huszonnyolcadikán", "huszonkilencedikén", "harmincadikán", "harminceggyedikén"]
mute_volumes=['Master', 'Master Front', 'Headphone', 'Speaker', 'Front', 'Surround', 'Center', 'LFE', 'Side', 'PCM']
increaseordecrease_volumes=['Master', 'Master Front', 'Headphone', 'Speaker', 'Front', 'Surround', 'Center', 'LFE', 'Side', 'PCM']

def increasevolume(script, inputEvent=None):
    kilettmondva=False
    for hangeroszabalyzo in increaseordecrease_volumes:
        volume=subprocess.getoutput('amixer -D pulse get \''+hangeroszabalyzo+'\'|grep %|cut -d "[" -f2')
        volume=volume.replace("]", "")
        volume=volume.replace('%', '')
        try:
            vanetobbertek=-1
            vanetobbertek=volume.find(' ')
            if vanetobbertek!=-1:
                ertek=int(volume[0:vanetobbertek])
            else:
                ertek=int(volume)
            ertek=ertek+5
            if ertek>100:
                ertek=100
            #Following command increasing volume with 5 step
            subprocess.getoutput('amixer -D pulse sset \''+hangeroszabalyzo+'\' '+str(ertek)+'% unmute')
            #Final, spokening Orca the new increased volume value
            if not kilettmondva:
                orca.speech.speak(str(ertek)+'%')
                kilettmondva=True
        except ValueError:
            pass

#Following function decreasing master volume with 5 step, and spokening the new changed volume
def decreasevolume(script, inputEvent=None):
    kilettmondva=False
    for hangeroszabalyzo in increaseordecrease_volumes:
        volume=subprocess.getoutput('amixer -D pulse get \''+hangeroszabalyzo+'\'|grep %|cut -d "[" -f2')
        volume=volume.replace("]", "")
        volume=volume.replace('%', '')
        try:
            vanetobbertek=-1
            vanetobbertek=volume.find(' ')
            if vanetobbertek!=-1:
                ertek=int(volume[0:vanetobbertek])
            else:
                ertek=int(volume)
            ertek=ertek-5
            if ertek<0:
                ertek=0
            #Following command decreasing volume with 5 step
            subprocess.getoutput('amixer sset -D pulse \''+hangeroszabalyzo+'\' '+str(ertek)+'% unmute')
            #Final, spokening Orca the new decreased volume value
            if not kilettmondva:
                orca.speech.speak(str(ertek)+'%')
                kilettmondva=True
        except ValueError:
            pass

#Following function toggle master volume mute on/off
def togglevolumemute(script, inputEvent=None):
    kilettmondva=False
    muted=True
    for volume in mute_volumes:
        #Following command gets master volume mute status
        mutestatus=subprocess.getoutput('amixer -D pulse get \''+volume+'\'|grep %|cut -d "[" -f3')
        mutestatus=mutestatus.replace(']\n', '')
        mutestatus=mutestatus.replace(']', '')
        if mutestatus.find('on')!=-1:
            muted=False
        if mutestatus.find('off')!=-1:
            muted=True
            break
    if not muted and not kilettmondva:
        orca.speech.speak('Némítás bekapcsolva.')
        orca.braille.displayMessage('Némítás bekapcsolva.', flashTime=orca.settings.brailleFlashTime)
        time.sleep(1.0)
        kilettmondva=True
    for volume in mute_volumes:
        #Following command toggle master volume mute on/off
        subprocess.getoutput('amixer sset -D pulse \''+volume+'\' toggle')
    if kilettmondva:
        return True
    muted=False
    for volume in mute_volumes:
        mutestatus=subprocess.getoutput('amixer get \''+volume+'\'|grep %|cut -d "[" -f4')
        mutestatus=mutestatus.replace(']', '')
        if mutestatus.find('on')!=-1:
            muted=False
        if mutestatus.find('off')!=-1:
            muted=True
    if not muted and not kilettmondva:
        orca.speech.speak('Némítás kikapcsolva.')
        orca.braille.displayMessage('Némítás kikapcsolva.', flashTime=orca.settings.brailleFlashTime)

def getVar(fileName, sectionName, sectionKey):
    config = configparser.ConfigParser()
    if os.path.exists(fileName) == True:
        try:
            config.read(fileName)
            return config.get(sectionName, sectionKey)
        except:
            return ""
    else:
        orca.speech.speak('Az RSS csatornákat tartalmazó konfigurációs állomány nem található a saját felhasználói mappájában.')
        sys.exit()
        return ""

def idojaraslekerese(kezdet):
    from xml.dom import minidom
    try:
        con=ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None, cadata=None)
        g=urlopen('https://www.metnet.hu/rss', context=con)
        orca.speech.speak('Kis türelmet, időjárás információk letöltése folyamatban.')
        xml=minidom.parse(g)
    except:
        orca.speech.speak("Az időjárásjelentést szolgáltató RSS csatorna jelenleg nem érhető el. Próbálja meg később.")

    cim=xml.getElementsByTagName("title")[0].childNodes[0].data
    cim1=xml.getElementsByTagName("title")[1].childNodes[0].data
    orca.speech.speak(cim)
    try:
        leiras=xml.getElementsByTagName("description")[0].childNodes[0].data
    except:
        leiras=''
    if (cim==cim1) or (leiras==cim) or (leiras==''):
        kelleltolas=1
    else:
        kelleltolas=0

    for i in range(kezdet,len(xml.getElementsByTagName("title"))):
        cim=xml.getElementsByTagName("title")[i].childNodes[0].data
        try:
            if kelleltolas==1:
                leiras=xml.getElementsByTagName("description")[i-1].childNodes[0].data
            else:
                leiras=xml.getElementsByTagName("description")[i].childNodes[0].data
        except:
            leiras='Nem áll rendelkezésre rövid leírás.'
        orca.speech.speak(cim)
        leiras=leiras.replace(' -', ' minusz')
        orca.speech.speak(leiras)

def otnaposelorejelzeslekerese(kellosszefoglalo):
    from xml.dom import minidom
    try:
        con=ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None, cadata=None)
        g=urlopen('https://www.metnet.hu/rss/2.php', context=con)
        orca.speech.speak("Kis türelmet, időjárás információk letöltése folyamatban.")
        xml=minidom.parse(g)
    except:
        orca.speech.speak("A Metnet öt napos előrejelzést szolgáltató RSS csatorna nem érhető el. Próbálja meg később.")
    cim=xml.getElementsByTagName("title")[0].childNodes[0].data
    cim1=xml.getElementsByTagName("title")[1].childNodes[0].data
    keszitesdatuma=xml.getElementsByTagName("title")[2].childNodes[0].data
    datum=keszitesdatuma[9:len(keszitesdatuma)-1].split(".")
    temp=keszitesdatuma.split(" ")
    ido=temp[2]
    ido=ido.split(":")
    honapszam=int(datum[1])
    napszam=int(datum[2][0:2])
    keszitesiuzenet="Az öt napos előrejelzés "
    keszitesiuzenet=keszitesiuzenet+datum[0]+". "+honap[honapszam-1]+" "+naptoldalek[napszam-1]+", "
    if ido[1]!="00":
        if ido[0][0]=="0":
                keszitesiuzenet=keszitesiuzenet+ido[0][1]+" óra "
        else:
                keszitesiuzenet=keszitesiuzenet+ido[0]+" óra "
        if ido[1][0]=="0":
            keszitesiuzenet=keszitesiuzenet+ido[1][1]+" perckor készült."
        else:
            keszitesiuzenet=keszitesiuzenet+ido[1]+" perckor készült."
    else:
        if ido[0][0]=="0":
            keszitesiuzenet=keszitesiuzenet+ido[0][1]+" órakor készült."
        else:
            keszitesiuzenet=keszitesiuzenet+ido[0]+" órakor készült."

    orca.speech.speak("Metnet ötnapos időjárás előrejelzés")
    orca.speech.speak(keszitesiuzenet)
    if (cim==cim1) or (leiras==cim) or (leiras==''):
        kelleltolas=1
    else:
        kelleltolas=0
    if kellosszefoglalo==1:
        for i in range(3,len(xml.getElementsByTagName("title"))):
            cim=xml.getElementsByTagName("title")[i].childNodes[0].data
            try:
                if kelleltolas==1:
                    leiras=xml.getElementsByTagName("description")[i-1].childNodes[0].data
                else:
                    leiras=xml.getElementsByTagName("description")[i].childNodes[0].data
            except:
                leiras='Nem áll rendelkezésre rövid leírás.'
            leiras=leiras.replace(' -', ' minusz')
        orca.speech.speak(leiras)
    i=0
    orca.speech.speak("Hőmérséklet adatok:")
    for i in range(0,5):
        datum=xml.getElementsByTagName("date")[i].childNodes[0].data
        orca.speech.speak(datum)
        minimum=xml.getElementsByTagName("minimum")[i].childNodes[0].data
        maximum=xml.getElementsByTagName("maximum")[i].childNodes[0].data
        reggel=xml.getElementsByTagName("morning")[i].childNodes[0].data
        delutan=xml.getElementsByTagName("afternoon")[i].childNodes[0].data
        wind=xml.getElementsByTagName("wind")[i].childNodes[0].data
        minimum=minimum.replace("-", "minusz")
        maximum=maximum.replace("-", "minusz")
        if wind!='':
                orca.speech.speak(wind+' szél.')
        ejszaka='Éjszaka '+minimum+' fok, napközben '+maximum+' fok.'
        orca.speech.speak(ejszaka)

def csatornalekeres(url, infocount):
    from xml.dom import minidom
    maganhangzok=['a', 'á', 'e', 'é', 'i', 'í', 'o', 'ó', 'u', 'ú', 'ö', 'ő', 'ü', 'ű', 'A', 'Á', 'E', 'É', 'I', 'Í', 'U', 'Ú', 'O', 'Ó', 'Ö', 'Ő', 'Ü', 'Ű', '[']
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        g=urlopen(req)
        orca.speech.speak('Az információk letöltése folyamatban, kérem várjon.')
        xml=minidom.parse(g)
    except:
        orca.speech.speak("Az ön által kért RSS csatorna információi jelenleg nem érhetők el. Próbálja meg később.")

    cim=xml.getElementsByTagName("title")[0].childNodes[0].data
    cim1=xml.getElementsByTagName("title")[1].childNodes[0].data
    try:
        leiras=xml.getElementsByTagName("description")[0].childNodes[0].data
    except:
        leiras=''
    if (cim==cim1) or (leiras==cim) or (leiras==''):
        kelleltolas=1
        kezdet=2
    else:
        kelleltolas=1
        kezdet=0
    cim=cim.replace('rss', '')
    cim=cim.replace('RSS', '')
    cim=cim.replace("[", "")
    cim=cim.replace("]", "")
    if cim[0]in maganhangzok:
        orca.speech.speak('Az '+cim+' RSS csatorna legfrissebb információi:')
    else:
        orca.speech.speak('A '+cim+' RSS csatorna legfrissebb információi:')
    if kezdet==0:
        hirkezdet=1
    else:
        hirkezdet=kezdet
    for i in range(hirkezdet,kezdet+int(infocount)):
        cim=xml.getElementsByTagName("title")[i].childNodes[0].data
        link=xml.getElementsByTagName("link")[i].childNodes[0].data
        try:
            if kelleltolas==1:
                leiras=xml.getElementsByTagName("description")[i-1].childNodes[0].data
            else:
                leiras=xml.getElementsByTagName("description")[i].childNodes[0].data
        except:
            leiras='Nem áll rendelkezésre rövid leírás.'
        orca.speech.speak(cim)
        orca.speech.speak(leiras)
    orca.speech.speak('Ha kíváncsi az RSS csatorna teljes tartalmára, nyomja le kétszer az előbb használt billentyűparancsot.')

def csatornahosszulekeres(url):
    from xml.dom import minidom
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        g=urlopen(req)
        xml=minidom.parse(g)
    except:
        orca.speech.speak("Az ön által kért RSS csatorna információi jelenleg nem érhetők el. Próbálja meg később.")

    cim=xml.getElementsByTagName("title")[0].childNodes[0].data
    f=open(os.getenv('HOME')+'/index.html',"w")
    f.write('<html>\n<head>\n<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=utf-8">\n<title>'+cim+'</title>\n</head>\n<body>')
    f.write('<h1>'+cim+'</h1>')
    orca.speech.speak('Kis türelmet, az információk letöltése folyamatban.')
    cim1=xml.getElementsByTagName("title")[1].childNodes[0].data
    try:
        leiras=xml.getElementsByTagName("description")[0].childNodes[0].data
    except:
        leiras=''
    if (cim==cim1) or (leiras==cim) or (leiras==''):
        kelleltolas=1
        kezdet=2
    else:
        kelleltolas=0
        kezdet=1
    for i in range(kezdet,len(xml.getElementsByTagName("title"))):
        cim=xml.getElementsByTagName("title")[i].childNodes[0].data
        link=xml.getElementsByTagName("link")[i].childNodes[0].data
        try:
            if kelleltolas==1:
                leiras=xml.getElementsByTagName("description")[i-1].childNodes[0].data
            else:
                leiras=xml.getElementsByTagName("description")[i].childNodes[0].data
        except:
            leiras='Nem áll rendelkezésre rövid leírás.'
        szoveg2=cim
        linktext=link
        f.write('<h2> <a href="'+linktext+'">'+szoveg2+'</a></h2>\n')
        f.write('<p>\n')
        szoveg2=leiras
        f.write(szoveg2+"</p>\n")
    orca.speech.speak('Betöltés, kis türelmet.')
    f.write('</body></html>')
    f.close()
    os.system('firefox '+os.getenv('HOME')+'/index.html &')

def csatorna1rovid(script, inputEvent=None):
    url=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'url1')
    infocount=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'infocount1')
    csatornalekeres(url, infocount)

def csatorna2rovid(script, inputEvent=None):
    url=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'url2')
    infocount=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'infocount2')
    csatornalekeres(url, infocount)

def csatorna3rovid(script, inputEvent=None):
    url=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'url3')
    infocount=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'infocount3')
    csatornalekeres(url, infocount)

def csatorna4rovid(script, inputEvent=None):
    url=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'url4')
    infocount=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'infocount4')
    csatornalekeres(url, infocount)

def csatorna5rovid(script, inputEvent=None):
    url=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'url5')
    infocount=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'infocount5')
    csatornalekeres(url, infocount)

def csatorna1hosszu(script, inputEvent=None):
    url=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'url1')
    csatornahosszulekeres(url)

def csatorna2hosszu(script, inputEvent=None):
    url=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'url2')
    csatornahosszulekeres(url)

def csatorna3hosszu(script, inputEvent=None):
    url=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'url3')
    csatornahosszulekeres(url)

def csatorna4hosszu(script, inputEvent=None):
    url=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'url4')
    csatornahosszulekeres(url)

def csatorna5hosszu(script, inputEvent=None):
    url=getVar(os.getenv('HOME')+'/rsscsatornak.cfg', 'rsscsatornak', 'url5')
    csatornahosszulekeres(url)

def idojarasrovid(script, inputEvent=None):
    kezdet=3
    idojaraslekerese(kezdet)

def idojarashosszu(script, inputEvent=None):
    kezdet=2
    idojaraslekerese(kezdet)

def otnaposelorejelzesrovid(script, inputEvent=None):
    kellosszefoglalo=0
    otnaposelorejelzeslekerese(kellosszefoglalo)

def otnaposelorejelzeshosszu(script, inputEvent=None):
    kellosszefoglalo=1
    otnaposelorejelzeslekerese(kellosszefoglalo)

def setClipboardText(text):
  cb = gtk.Clipboard()
  cb.set_text(text)
  cb.store()


myKeyBindings = orca.keybindings.KeyBindings()

#define the battery status function
def sayBattery(script, inputEvent=None):
  import subprocess
  message = subprocess.getoutput("acpi|grep \"%\"|cut -d \",\" -f2")
  ora=subprocess.getoutput("acpi |grep \",\" |cut -d \",\" -f3|cut -d \"r\" -f1|cut -d \":\" -f1")
  status=subprocess.getoutput("acpi|grep Battery|cut -d \",\" -f1")
  perc=subprocess.getoutput("acpi |grep \",\" |cut -d \",\" -f3|cut -d \"r\" -f1|cut -d \":\" -f2")
  if len(message) == 0 or message.startswith('No support for device type:'):
    uzenet = "Nem észlelhető telep."
  if status=="Battery 0: Charging":
    uzenet=message+" áll rendelkezésre (csatlakoztatva, töltődik)."
  if (status=="Battery 0: Full") or (status=="Battery 0: Unknown"):
    uzenet="Teljesen feltöltve ("+message+")."
  if status=="Battery 0: Discharging":
    if len(ora)==1 and len(perc)==1:
        uzenet="Akkumulátor töltöttség: "+message+"."    
    else:
        if ora[1]=="0" and ora[2]=="0" and perc!="" :
            if perc[0]=="0":
                uzenet=perc[1]+" perc van hátra ("+message+")."
            else:
                uzenet=perc+" perc van hátra ("+message+")."
        else:
            if perc[0]=="0" and perc[1]!="0":
                uzenet=ora[2]+" óra, "+perc[1]+" perc van hátra ("+message+")."
            else:
                if perc[1]=="0":
                    uzenet=ora[2]+" óra van hátra ("+message+")."
                else:
                    uzenet=ora[2]+" óra, "+perc+" perc van hátra ("+message+")."
  orca.speech.speak(uzenet)
  orca.braille.displayMessage(uzenet, flashTime=orca.settings.brailleFlashTime)
  return True

def presentclipboardtext(script, inputEvent=None):
  """ Presents the clipboard text. """
  #Get the clipboard
  cb = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
  #assign the clipboard contents to a variable.
  cbText = cb.wait_for_text()
  if isinstance(cbText, str) != True:
      message = "Nincs szöveg a vágólapon."
  else:
      verbosity = orca.settings.speechVerbosityLevel
      #If the verbosity setting is verbose, need spokening a notification message, and real clipboard text.
      #If the verbosity setting is brief, only need sending clipboard text.
      if verbosity == orca.settings.VERBOSITY_LEVEL_VERBOSE:
          message = "A vágólapon levő szöveg: %s" %(cbText)
      else:
          message=cbText
  #Speak and braille the info
  orca.speech.speak(message)
  orca.braille.displayMessage(message, flashTime=orca.settings.brailleFlashTime)  
  return True

def nevnapkimondas(script, inputEvent=None):
  import subprocess
  import os
  nevnap=subprocess.getoutput("birthday -W 0|grep \".\"|cut -d \".\" -f1")
  orca.speech.speak("Ma "+nevnap+" névnapja van.")
  orca.braille.displayMessage("Ma "+nevnap+" névnapja van.", flashTime=orca.settings.brailleFlashTime)
  return True

for hangeroszabalyzo in mute_volumes:
    hangero=0
    subprocess.getoutput('amixer set '+hangeroszabalyzo+' on')
    volume=subprocess.getoutput('amixer get \''+hangeroszabalyzo+'\'|grep %|cut -d "[" -f2')
    volume=volume.replace("]", "")
    volume=volume.replace('%', '')
    vanetobbertek=-1
    try:
        vanetobbertek=volume.find(' ')
        if vanetobbertek!=-1:
            hangero=int(volume[0:vanetobbertek])
        else:
            hangero=int(volume)
        if hangero==0:
            subprocess.getoutput('amixer set '+hangeroszabalyzo+' 90%')
    except:
        pass
    hangero=0
    subprocess.getoutput('amixer set -D pulse '+hangeroszabalyzo+' on')
    volume=subprocess.getoutput('amixer get -D pulse \''+hangeroszabalyzo+'\'|grep %|cut -d "[" -f2')
    volume=volume.replace("]", "")
    volume=volume.replace('%', '')
    vanetobbertek=-1
    try:
        vanetobbertek=volume.find(' ')
        if vanetobbertek!=-1:
            hangero=int(volume[0:vanetobbertek])
        else:
            hangero=int(volume)
        if hangero==0:
            subprocess.getoutput('amixer set -D pulse '+hangeroszabalyzo+' 90%')
    except:
        pass
subprocess.getoutput('setxkbmap hu')
subprocess.getoutput('killall speech-dispatcher')
switchwindowHandler = orca.input_event.InputEventHandler(
    showwindows,
    "Megjeleníti egy helyi menüben az elérhető képernyőelemeket és ablakokat.")

infocenterHandler = orca.input_event.InputEventHandler(
    show_infocenter,
    "Az Információs Központ megjelenítése.")

myKeyBindings.add(orca.keybindings.KeyBinding(
    "F10",
    1 << orca.keybindings.MODIFIER_ORCA,
    1 << orca.keybindings.MODIFIER_ORCA,
    switchwindowHandler))

myKeyBindings.add(orca.keybindings.KeyBinding(
    "i",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    infocenterHandler))

sayBatteryHandler = orca.input_event.InputEventHandler(
    sayBattery,
    "Kimondja és kiírja a braille kijelzőre az akkumulátor státuszát.") # Shows the function of the key press in learn mode

myKeyBindings.add(orca.keybindings.KeyBinding(
    "a",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    sayBatteryHandler)) # Sets Orca-a as the battery status key

presentclipboardhandler = orca.input_event.InputEventHandler(
    presentclipboardtext,
    "Kimondja és megjeleníti a braille kijelzőn a vágólapon található szöveget.")

myKeyBindings.add(orca.keybindings.KeyBinding(
    "r",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    presentclipboardhandler))

nevnapHandler = orca.input_event.InputEventHandler(
    nevnapkimondas,
    "Kimondja és kiírja a braille kijelzőre a mai névnapot.") # Shows the function of the key press in learn mode

myKeyBindings.add(orca.keybindings.KeyBinding(
    "n",
    orca.keybindings.ORCA_MODIFIER_MASK,
    orca.keybindings.ORCA_MODIFIER_MASK,
    nevnapHandler)) # Sets Orca-a as the battery status key

increasevolumeHandler = orca.input_event.InputEventHandler(
    increasevolume,
    "Növeli a fő hangerőt, majd kimondja az új értéket.") # Shows the function of the key press in learn mode

myKeyBindings.add(orca.keybindings.KeyBinding(
    "Page_Up",
    orca.keybindings.ORCA_MODIFIER_MASK,
    orca.keybindings.ORCA_MODIFIER_MASK,
    increasevolumeHandler))

decreasevolumeHandler = orca.input_event.InputEventHandler(
    decreasevolume,
    "Csökkenti a fő hangerőt, majd kimondja az új értéket.") # Shows the function of the key press in learn mode

myKeyBindings.add(orca.keybindings.KeyBinding(
    "Page_Down",
    orca.keybindings.ORCA_MODIFIER_MASK,
    orca.keybindings.ORCA_MODIFIER_MASK,
    decreasevolumeHandler))

mutevolumeHandler = orca.input_event.InputEventHandler(
    togglevolumemute,
    "Átváltja a fő hangerő némítását.") # Shows the function of the key press in learn mode

myKeyBindings.add(orca.keybindings.KeyBinding(
    "End",
    orca.keybindings.ORCA_MODIFIER_MASK,
    orca.keybindings.ORCA_MODIFIER_MASK,
    mutevolumeHandler))

csatorna1rovidHandler = orca.input_event.InputEventHandler(
    csatorna1rovid,
    "Kimondja az 1. beállított RSS csatorna legfrissebb információit.")

csatorna2rovidHandler = orca.input_event.InputEventHandler(
    csatorna2rovid,
    "Kimondja a 2. beállított RSS csatorna legfrissebb információit.")

csatorna3rovidHandler = orca.input_event.InputEventHandler(
    csatorna3rovid,
    "Kimondja a 3. beállított RSS csatorna legfrissebb információit.")

csatorna4rovidHandler = orca.input_event.InputEventHandler(
    csatorna4rovid,
    "Kimondja a 4. beállított RSS csatorna legfrissebb információit.")

csatorna5rovidHandler = orca.input_event.InputEventHandler(
    csatorna5rovid,
    "Kimondja az 5. beállított RSS csatorna legfrissebb információit.")

csatorna1hosszuHandler = orca.input_event.InputEventHandler(
    csatorna1hosszu,
    "Megjeleníti a Firefox webböngészőben az 1. beállított RSS csatorna elérhető információit.")

csatorna2hosszuHandler = orca.input_event.InputEventHandler(
    csatorna2hosszu,
    "Megjeleníti a Firefox webböngészőben a 2. beállított RSS csatorna elérhető információit.")

csatorna3hosszuHandler = orca.input_event.InputEventHandler(
    csatorna3hosszu,
    "Megjeleníti a Firefox webböngészőben a 3. beállított RSS csatorna elérhető információit.")

csatorna4hosszuHandler = orca.input_event.InputEventHandler(
    csatorna4hosszu,
    "Megjeleníti a Firefox webböngészőben a 4. beállított RSS csatorna elérhető információit.")

csatorna5hosszuHandler = orca.input_event.InputEventHandler(
    csatorna5hosszu,
    "Megjeleníti a Firefox webböngészőben az 5. beállított RSS csatorna elérhető információit.")

idojarasrovidHandler = orca.input_event.InputEventHandler(
    idojarasrovid,
    "Kimondja a metnet RSS csatornán elérhető rövidített előrejelzést")

idojarashosszuHandler = orca.input_event.InputEventHandler(
    idojarashosszu,
    "Kimondja a metnet RSS csatornán elérhető teljes előrejelzést")

otnaposelorejelzesrovidHandler = orca.input_event.InputEventHandler(
    otnaposelorejelzesrovid,
    "Kimondja a metnet RSS csatornán elérhető öt napos előrejelzés hőmérséklet adatait.")

otnaposelorejelzeshosszuHandler = orca.input_event.InputEventHandler(
    otnaposelorejelzeshosszu,
    "az összefoglalóval együtt kimondja a metnet RSS csatornán elérhető öt napos előrejelzést.")

myKeyBindings.add(orca.keybindings.KeyBinding(
    "1",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    csatorna1rovidHandler))

myKeyBindings.add(orca.keybindings.KeyBinding(
    "2",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    csatorna2rovidHandler))

myKeyBindings.add(orca.keybindings.KeyBinding(

   "3",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    csatorna3rovidHandler))

myKeyBindings.add(orca.keybindings.KeyBinding(
    "4",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    csatorna4rovidHandler))

myKeyBindings.add(orca.keybindings.KeyBinding(
    "5",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    csatorna5rovidHandler))

myKeyBindings.add(orca.keybindings.KeyBinding(
    "1",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    csatorna1hosszuHandler,2))

myKeyBindings.add(orca.keybindings.KeyBinding(
    "2",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    csatorna2hosszuHandler,2))

myKeyBindings.add(orca.keybindings.KeyBinding(
    "3",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    csatorna3hosszuHandler,2))

myKeyBindings.add(orca.keybindings.KeyBinding(
    "4",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    csatorna4hosszuHandler,2))

myKeyBindings.add(orca.keybindings.KeyBinding(
    "5",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    csatorna5hosszuHandler,2))

myKeyBindings.add(orca.keybindings.KeyBinding(
    "w",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    otnaposelorejelzesrovidHandler, 1))

myKeyBindings.add(orca.keybindings.KeyBinding(
    "w",
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    orca.keybindings.ORCA_SHIFT_MODIFIER_MASK,
    otnaposelorejelzeshosszuHandler, 2))

myKeyBindings.add(orca.keybindings.KeyBinding(
    "w",
    orca.keybindings.ORCA_MODIFIER_MASK,
    orca.keybindings.ORCA_MODIFIER_MASK,
    idojarasrovidHandler))

myKeyBindings.add(orca.keybindings.KeyBinding(
    "w",
    orca.keybindings.ORCA_MODIFIER_MASK,
    orca.keybindings.ORCA_MODIFIER_MASK,
    idojarashosszuHandler,2))

orca.settings.keyBindingsMap["default"] = myKeyBindings

