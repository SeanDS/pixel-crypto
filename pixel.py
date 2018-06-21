from PIL import Image, ImageOps, ImageDraw, ImageFont
import random

# colours
black = (0, 0, 0)
white = (255, 255, 255)

def add_mark(pixels, x, y, marker_height, marker_half_width):
    # draw down rows
    for j in range(y):
        if j < marker_height or j > (y - marker_height):
            for i in range(x - marker_half_width, x + marker_half_width):
                pixels[i, j] = (255, 255, 255)

def draw_text(draw, x, y, text, font):
    # get size of text to draw
    (w, h) = font.getsize(text)
    
    # draw centred around x and y
    draw.text((x - w // 2, y - h // 2), text, font=font)

def encipher(img, x_buf, seed):
    random.seed(seed)

    # original image pixels
    pixels_base = img.load()

    # new layer
    img_rand = Image.new("RGB", (img.size[0], img.size[1]))
    pixels_rand = img_rand.load()

    # generate random noise layer
    add_noise(img_rand, x_buf)

    # create inverse layer
    img_rand_inv = img_rand.copy()
    pixels_rand_inv = img_rand_inv.load()

    # loop over pixels
    for i in range(x_buf, img_rand.size[0] - x_buf):
        for j in range(img_rand.size[1]):
            # if pixel is white, don't invert
            if pixels_base[i, j] == white:
               pixels_rand_inv[i, j] = pixels_rand[i, j]
            else:        
                # compute inverse
                if pixels_rand[i, j] == white:
                    pixels_rand_inv[i, j] = black
                else:
                    pixels_rand_inv[i, j] = white
    
    return [img_rand, img_rand_inv]

def add_noise(image, x_buf):
    pixels = image.load()

    for i in range(x_buf, image.size[0] - x_buf):
        for j in range(image.size[1]):
            # random pixel
            pixels[i, j] = random.choice([black, white])

if __name__ == "__main__":
    # total size
    x = 2250
    y = 300

    # ruler size
    x_draw = 2000

    large_marker_height = 75
    large_marker_half_width = 2
    large_marker_spacing = 100

    medium_marker_height = 50
    medium_marker_half_width = 1
    medium_marker_spacing = 50

    small_marker_height = 25
    small_marker_half_width = 1
    small_marker_spacing = 10

    fidutial_1_x = 50
    fidutial_1_y = 150
    fidutial_2_x = x - 50
    fidutial_2_y = 150
    fidutial_r = 15

    font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    font_size = 60
    text_height_offset = 30

    # black image
    # Coordinates: (columns, rows)
    # 200mm x 30mm, 10 pixels per mm
    img = Image.new("RGB", (x, y), "black")

    # image drawer
    draw = ImageDraw.Draw(img)

    # create the pixel map
    pixels = img.load()

    # x buffer
    x_buf = (x - x_draw) // 2

    # load font
    font = ImageFont.truetype(font_path, font_size)

    # add markings
    for i in range(small_marker_spacing, x_draw + 1):
        if i % large_marker_spacing == 0:
            # add large mark
            add_mark(pixels, x_buf + i, img.size[1], large_marker_height, large_marker_half_width)

            draw_text(draw, x_buf + i, large_marker_height + text_height_offset, str(i // 100), font)

        elif i % medium_marker_spacing == 0:
            # add medium mark
            add_mark(pixels, x_buf + i, img.size[1], medium_marker_height, medium_marker_half_width)
        elif i % small_marker_spacing == 0:
            # add small mark
            add_mark(pixels, x_buf + i, img.size[1], small_marker_height, small_marker_half_width)

    # create cyphers
    layers = encipher(img, x_buf, seed=25526)

    # add fidutials
    draw = ImageDraw.Draw(layers[0])
    draw.ellipse((fidutial_1_x - fidutial_r, fidutial_1_y - fidutial_r, fidutial_1_x + fidutial_r, fidutial_1_y + fidutial_r), fill=(255, 255, 255))
    draw.ellipse((fidutial_2_x - fidutial_r, fidutial_2_y - fidutial_r, fidutial_2_x + fidutial_r, fidutial_2_y + fidutial_r), fill=(255, 255, 255))
    draw = ImageDraw.Draw(layers[1])
    draw.ellipse((fidutial_1_x - fidutial_r, fidutial_1_y - fidutial_r, fidutial_1_x + fidutial_r, fidutial_1_y + fidutial_r), fill=(255, 255, 255))
    draw.ellipse((fidutial_2_x - fidutial_r, fidutial_2_y - fidutial_r, fidutial_2_x + fidutial_r, fidutial_2_y + fidutial_r), fill=(255, 255, 255))

    #img.show()
    #layers[0].show()
    #layers[1].show()
    
    # add borders
    layers[0] = ImageOps.expand(layers[0], border=20, fill='black')
    layers[1] = ImageOps.expand(layers[1], border=20, fill='black')

    # save
    layers[0].save("layer1.png")
    layers[1].save("layer2.png")

    # create A4 sheet
    img_a4 = Image.new("RGBA", (2100, 2970), (0, 0, 0, 0))

    # paste
    img_a4.paste(layers[0].rotate(90, expand=1), (15, 360))
    img_a4.paste(layers[1].rotate(90, expand=1), (360, 360))
    img_a4.paste(layers[0].rotate(90, expand=1), (705, 360))
    img_a4.paste(layers[1].rotate(90, expand=1), (1050, 360))
    img_a4.paste(layers[0].rotate(90, expand=1), (1395, 360))
    img_a4.paste(layers[1].rotate(90, expand=1), (1740, 360))

    img_a4.save("a4.png")