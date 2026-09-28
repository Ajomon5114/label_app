import qrcode
import base64
from io import BytesIO

qr = qrcode.QRCode(version=1, box_size=10, border=0)
qr.add_data('Hello World')
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
buf = BytesIO()
img.save(buf, format="PNG")
b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

svg_data = f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
    <image x="10" y="10" width="100" height="100" href="data:image/png;base64,{b64}" />
</svg>"""

with open("test_qr.svg", "w") as f:
    f.write(svg_data)

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    drawing = svg2rlg("test_qr.svg")
    renderPM.drawToFile(drawing, "test_qr.png", fmt="PNG")
    print("Success with svglib!")
except Exception as e:
    print("Failed with svglib:", e)
