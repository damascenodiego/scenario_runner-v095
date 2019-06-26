import qrcode
import math
import os

from escposprinter import printer
from PIL import Image


def make_custom_qr(data):
    # Create qr code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    # Add data
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image()
    # Rezize it
    img = img.resize((200, 200))

    old_width, old_height = img.size
    canvas_width, canvas_height = (370, 200)
    # Center the image
    x1 = int(math.floor((canvas_width - old_width) / 2))
    y1 = int(math.floor((canvas_height - old_height) / 2))
    mode = img.mode
    new_background = (255)
    if len(mode) == 3:  # RGB
        new_background = (255, 255, 255)
    if len(mode) == 4:  # RGBA, CMYK
        new_background = (255, 255, 255, 255)

    newImage = Image.new(mode, (canvas_width, canvas_height), new_background)
    newImage.paste(img, (x1, y1, x1 + old_width, y1 + old_height))
    return newImage


def print_receipt(id, score):
    p = printer.Usb(0x0416, 0x5011)
    # p.open()
    p.set(align='center', size='normal')

    p.text('\n------------------------\n')
    p.text("Trusted Autonomous Vehicles\n"
           "presented by\n")
    uol_logo = os.getenv('ROOT_SCENARIO_RUNNER', "./") + "/utils/"+ "uol.jpg"
    p.image(uol_logo)

    p.text("\nYour driving score:\n\n")

    p.set(align='center', size='2x')
    p.text("{}\n\n".format(score))
    p.set(align='center', size='normal')

    # The data that you want to store
    an_url = 'driverleics.github.io/s?i={}'.format(id)

    p.text('See the complete scoreboard at\n\n'
           '{}\n\n'.format(an_url))

    p.text("Your ID:\n\n")
    p.set(align='center', size='2w')
    p.text("{}\n\n".format(id))
    p.set(align='center', size='normal')

    p.text('or using the QR-code below\n'.format(id))

    an_url = 'https://'+an_url
    img = make_custom_qr(an_url)
    # Save it
    img.save("qrcode.jpg")
    # Print it
    p.image("qrcode.jpg")

    p.text("\nThanks for\n"
           "visiting us and\n"
           "drive safe!\n")
    p.text('\n------------------------\n\n')
    # p.cut()
    # p.close()
