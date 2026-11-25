from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

root=Path(__file__).resolve().parents[1]
out=root/'presentation'/'GraphGuard_Final_Presentation.pdf'
canvas=Canvas(str(out), pagesize=(1280,720))
for image_path in sorted((root/'.build'/'slides').glob('slide-*.png'), key=lambda p:int(p.stem.split('-')[1])):
    image=Image.open(image_path)
    canvas.drawImage(ImageReader(image),0,0,width=1280,height=720)
    canvas.showPage()
canvas.save()
