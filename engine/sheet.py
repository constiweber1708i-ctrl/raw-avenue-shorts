import sys, glob
from PIL import Image, ImageDraw
files=sorted(glob.glob(sys.argv[1])); cols=int(sys.argv[3]) if len(sys.argv)>3 else 5
tw,th=324,576; rows=(len(files)+cols-1)//cols
S=Image.new("RGB",(cols*tw,rows*(th+30)),"white"); d=ImageDraw.Draw(S)
for i,f in enumerate(files):
    im=Image.open(f).resize((tw,th)); x,y=(i%cols)*tw,(i//cols)*(th+30)
    S.paste(im,(x,y+30)); d.text((x+5,y+8),f.split("_")[-1],fill="black")
S.save(sys.argv[2])
