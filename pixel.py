from PIL import Image, ImageDraw, ImageFont
import random

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

def encipher(img, n, seed):
    random.seed(seed)

    # copy image n times
    layers = [img.copy() for _ in range(n)]
    layer_pixels = [layer.load() for layer in layers]

    pixels = img.load()

    # colours
    black = (0, 0, 0)
    white = (255, 255, 255)

    def set_layer_colours(colours):
        for layer, colour in zip(layer_pixels, colours):
            layer[i, j] = colour

    # loop over pixels
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            # if pixel is white, all layers must be white
            if pixels[i, j] == white:
                set_layer_colours([white for _ in range(n)])
            else:
                # at least one layer must be black
                colours = [black] + [white] * (n - 1)

                # shuffle colours
                random.shuffle(colours)

                # set colours
                set_layer_colours(colours)
    
    return layers

if __name__ == "__main__":
    # total size
    x = 2050
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

    font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    font_size = 25
    text_height_offset = 15

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

    # create cyphertexts
    layers = encipher(img, 2, seed=25526)

    img.show()
    
    for layer in layers:
        layer.show()