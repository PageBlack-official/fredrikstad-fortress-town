from PIL import Image, ImageDraw, ImageFont
import os
Image.MAX_IMAGE_PIXELS=None
T='soc/rapport/_tmp/'; U='soc/rapport/dekning-utsnitt/'
try: F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',26)
except Exception: F=ImageFont.load_default()
def merk(src,ut,punkter,tittel):
    im=Image.open(T+src).convert('RGB'); d=ImageDraw.Draw(im)
    for (x,y,txt) in punkter:
        d.ellipse((x-34,y-34,x+34,y+34),outline=(255,0,255),width=5)
        tw=d.textlength(txt,font=F)
        d.rectangle((x+38,y-18,x+38+tw+10,y+18),fill=(255,0,255)); d.text((x+43,y-16),txt,fill='white',font=F)
    d.rectangle((0,0,im.width,44),fill=(0,0,0)); d.text((10,8),tittel,fill='white',font=F)
    im=im.resize((1200,int(im.height*1200/im.width))); im.save(U+ut)
merk('u-torv.png','1-torvet.png',[(505,265,'statue'),(560,300,'markør 1'),(450,150,'ikon: info'),(830,110,'gatenavn'),(560,600,'teglmur (3)'),(1180,420,'gate, ingen fortau tegnet'),(900,560,'plen'),(1030,620,'gårdsrom (46)')],'1 Kongens torv / Kirkegaten (300 dpi, px 1900–3500 × 900–2000)')
merk('u-nord.png','2-nord.png',[(285,185,'båt (Byfergen)'),(320,400,'båt (Byfergen)'),(395,390,'ikon: ferje'),(900,200,'trekroner'),(430,510,'Færgeporten (34)'),(575,520,'markør 35'),(1100,330,'voll/allé')],'2 Nord: Smedjesgaten og elva (px 2300–3900 × 100–1200)')
merk('u-havn.png','3-havn.png',[(560,350,'Vindebroen (26)'),(330,195,'Voldporten (25)'),(950,300,'lys sti på bastion'),(900,750,'vollvei, grå'),(1000,150,'vollgrav/vann'),(830,400,'27 Voldportravelinet'),(100,720,'trær på voll (24)')],'3 Havn / Vindebroen (px 3400–5000 × 1300–2400)')
merk('u-sorvest.png','4-toihuset.png',[(1120,250,'plankegjerde, brunt'),(620,560,'parkmur, lys grå'),(190,310,'brygge med pullerter (14)'),(510,240,'ikon: WC'),(600,300,'ikon: museum (over)'),(1140,650,'Tøihuset (19)'),(800,450,'trær i parken'),(1300,420,'gårdsrom, grus')],'4 Tøihuset / Laboratoriegaten (px 400–2000 × 1200–2300)')
merk('u-isegran.png','5-isegran.png',[(480,580,'fortring (mur)'),(940,240,'båt / båtbyggeri'),(580,290,'hus, gul'),(490,215,'liten figur/lykt?'),(635,215,'liten figur/lykt?'),(1000,500,'vann, akvarell')],'5 Isegran (px 0–1600 × 200–1300)')
merk('u-sor.png','6-sor.png',[(440,930,'vollsti, grå stripe'),(700,350,'trerekke på voll'),(650,520,'21 Labratoriet'),(300,800,'vollgrav (17)'),(1000,900,'voll, grønn'),(1440,380,'markør 18')],'6 Sør: Prins Christians bastion (px 1200–2800 × 1900–3000)')
merk('u-nordost.png','7-nordost.png',[(1090,400,'sti over plen (30)'),(505,420,'mur/gjerde ved 36'),(700,650,'gate uten fortau'),(1050,900,'Artillerigården (29)'),(1280,370,'allé på voll'),(1500,200,'elv')],'7 Nordøst: Færgeportgaten (px 2600–4200 × 500–1600)')
print(os.listdir(U))
