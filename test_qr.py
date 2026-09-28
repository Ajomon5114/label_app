import qrcode
values = {
    'product': 'Test Product',
    'batch': 'B123',
    'net_wt': '25.00 Kg',
    'gross_wt': '27.00 Kg'
}
qr_text = "\n".join([f"{k.replace('_', ' ').title()}: {v}" for k, v in values.items() if v])
qr = qrcode.QRCode(version=1, box_size=10, border=1)
qr.add_data(qr_text)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.save("test_qr.png")
print("QR text:")
print(repr(qr_text))
