from PIL import Image, ImageOps, ImageDraw, ImageFont
import random

# colours
black = (0, 0, 0)
white = (255, 255, 255)

# total size
x = 2450
y = 300

# ruler size
x_draw = 2200

large_marker_height = 75
large_marker_half_width = 2
large_marker_spacing = 200

medium_marker_height = 50
medium_marker_half_width = 1
medium_marker_spacing = 100

small_marker_height = 25
small_marker_half_width = 1
small_marker_spacing = 20

fidutial_1_x = 50
fidutial_1_y = 150
fidutial_2_x = x - 50
fidutial_2_y = 150
fidutial_r = 15

layer_name_x_offset = 0
layer_name_y_offset = -100

font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
font_size = 60
text_height_offset = 30

# load font
font = ImageFont.truetype(font_path, font_size)

def add_mark(pixels, x, y, marker_height, marker_half_width):
    # draw down rows
    for j in range(y):
        if j < marker_height or j > (y - marker_height):
            for i in range(x - marker_half_width, x + marker_half_width):
                pixels[i, j] = (255, 255, 255)

def draw_text(draw, x, y, text):
    # get size of text to draw
    (w, h) = font.getsize(text)
    
    # draw centred around x and y
    draw.text((x - w // 2, y - h // 2), text, font=font)

def encipher(img, x_buf, dot_size, seed):
    random.seed(seed)

    # original image pixels
    pixels_base = img.load()

    # new layer
    img_rand = Image.new("RGB", (img.size[0], img.size[1]))
    pixels_rand = img_rand.load()

    # generate random noise layer
    add_noise(img_rand, x_buf, dot_size)

    # create inverse layer
    img_rand_inv = img_rand.copy()
    pixels_rand_inv = img_rand_inv.load()

    # loop over pixels
    for i in range(x_buf, img_rand.size[0] - x_buf, dot_size):
        for j in range(0, img_rand.size[1], dot_size):
            # if pixel is white, don't invert
            if pixels_base[i, j] == white:
                for io in range(dot_size):
                    for jo in range(dot_size):
                        pixels_rand_inv[i+io, j+jo] = pixels_rand[i, j]
            else:        
                # compute inverse
                if pixels_rand[i, j] == white:
                    for io in range(dot_size):
                        for jo in range(dot_size):
                            pixels_rand_inv[i+io, j+jo] = black
                else:
                    for io in range(dot_size):
                        for jo in range(dot_size):
                            pixels_rand_inv[i+io, j+jo] = white
    
    return [img_rand, img_rand_inv]

def add_noise(image, x_buf, dot_size):
    pixels = image.load()

    for i in range(x_buf, image.size[0] - x_buf, dot_size):
        for j in range(0, image.size[1], dot_size):
            choice = random.choice([black, white])
            for io in range(dot_size):
                for jo in range(dot_size):
                    pixels[i+io, j+jo] = choice

def add_fiducials(img, fidutial_1_x, fidutial_1_y, fidutial_2_x, fidutial_2_y, fidutial_r):
    draw = ImageDraw.Draw(img)
    draw.ellipse((fidutial_1_x - fidutial_r, fidutial_1_y - fidutial_r, fidutial_1_x + fidutial_r, fidutial_1_y + fidutial_r), fill=(255, 255, 255))
    draw.ellipse((fidutial_2_x - fidutial_r, fidutial_2_y - fidutial_r, fidutial_2_x + fidutial_r, fidutial_2_y + fidutial_r), fill=(255, 255, 255))

def make_ruler_layers(dot_size):
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

    # add markings
    # x-axis
    for i in range(small_marker_spacing, x_draw + 1):
        if i % large_marker_spacing == 0:
            # add large mark
            add_mark(pixels, x_buf + i, img.size[1], large_marker_height, large_marker_half_width)

            draw_text(draw, x_buf + i, large_marker_height + text_height_offset, str(i // 200))

        elif i % medium_marker_spacing == 0:
            # add medium mark
            add_mark(pixels, x_buf + i, img.size[1], medium_marker_height, medium_marker_half_width)
        elif i % small_marker_spacing == 0:
            # add small mark
            add_mark(pixels, x_buf + i, img.size[1], small_marker_height, small_marker_half_width)

    # create ciphers
    layers = encipher(img, x_buf, dot_size, seed=25526)

    # add circles for alignment
    add_fiducials(layers[0], fidutial_1_x, fidutial_1_y, fidutial_2_x, fidutial_2_y, fidutial_r)
    add_fiducials(layers[1], fidutial_1_x, fidutial_1_y, fidutial_2_x, fidutial_2_y, fidutial_r)

    # add layer name
    draw_text(ImageDraw.Draw(layers[0]), fidutial_1_x + layer_name_x_offset, fidutial_1_y + layer_name_y_offset, "A")
    draw_text(ImageDraw.Draw(layers[1]), fidutial_1_x + layer_name_x_offset, fidutial_1_y + layer_name_y_offset, "B")

    #img.show()
    #layers[0].show()
    #layers[1].show()
    
    # add borders
    layers[0] = ImageOps.expand(layers[0], border=20, fill='black')
    layers[1] = ImageOps.expand(layers[1], border=20, fill='black')

    return layers

if __name__ == "__main__":
    layers_2 = make_ruler_layers(2)
    layers_3 = make_ruler_layers(3)
    layers_4 = make_ruler_layers(4)

    # save
    layers_2[0].save("layer_2_1.png")
    layers_2[1].save("layer_2_2.png")
    layers_3[0].save("layer_3_1.png")
    layers_3[1].save("layer_3_2.png")
    layers_4[0].save("layer_4_1.png")
    layers_4[1].save("layer_4_2.png")

    # create A4 sheet
    img_a4 = Image.new("RGBA", (2100, 2970), (0, 0, 0, 0))

    # paste
    img_a4.paste(layers_2[0].rotate(90, expand=1), (15, 360))
    img_a4.paste(layers_2[1].rotate(90, expand=1), (360, 360))
    img_a4.paste(layers_3[0].rotate(90, expand=1), (705, 360))
    img_a4.paste(layers_3[1].rotate(90, expand=1), (1050, 360))
    img_a4.paste(layers_4[0].rotate(90, expand=1), (1395, 360))
    img_a4.paste(layers_4[1].rotate(90, expand=1), (1740, 360))

    img_a4.save("a4.png")