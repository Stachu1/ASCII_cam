import sys, os, time, cv2, numpy as np, threading, json
from PIL import Image, ImageDraw





def convert_to_ascii(img, settings):      #? Converts PIL image to ascii characters list
    if os.path.isfile("img.png"):
        img = Image.open(os.path.join(os.getcwd(), "img.png"))
        
    #* resize the image
    width, height = settings["window"]["size"]["x"], settings["window"]["size"]["y"]
    img_width = settings["image"]["size"]["x"]
    img_height = settings["image"]["size"]["y"]
    img = img.resize((img_width, int(img_height)))


    #* get pixels values
    pixels = img.convert("L").getdata()
    pixels_rgb = img.convert("RGB").getdata()
    

    #* get ascii array
    ascii_array = settings["image"]["ascii_array"]
    
    new_pixels = []
    for pixel in pixels:
        new_pixels.append(ascii_array[int(pixel / (255 / len(ascii_array))) - 1])
    new_pixels = ''.join(new_pixels)

    # split string of chars into multiple strings of length equal to new width and create a list
    ascii = [new_pixels[index:index + img_width] for index in range(0, len(new_pixels), img_width)]
    
    # ascii_image_to_print = "\n".join(ascii)
    #* print(ascii_image_to_print)
    return ascii, width, height, img_width, img_height, pixels_rgb
    


def generate_img(ascii_image, width, height, img_width, img_height, pixels_rgb, settings):       #? Generates PIL image out of ascii characters list
    if settings["image"]["color"]["one"] == "True":
        img = Image.new(mode="RGB", size=(img_width*6, int(img_height)*10), color=tuple(settings["image"]["color"]["background"]))
        d = ImageDraw.Draw(img)
        for row in range(len(ascii_image)):
            d.text(xy=(0,10*row), text=ascii_image[row], fill=(int(255*settings["image"]["color"]["filter"]["red"]), int(255*settings["image"]["color"]["filter"]["green"]), int(255*settings["image"]["color"]["filter"]["blue"])), fontsize=1)
        img = img.resize((width, height))
        return img
    
    else:
        img = Image.new(mode="RGB", size=(img_width*6, int(img_height)*10), color=tuple(settings["image"]["color"]["background"]))
        d = ImageDraw.Draw(img)
        for row in range(len(ascii_image)):
            ascii_image[row] = list(ascii_image[row])
        for row in range(len(ascii_image)):
            for pixel in range(len(ascii_image[row])):
                d.text(xy=(6*pixel,10*row), text=ascii_image[row][pixel], fill=(pixels_rgb[row*img_width+pixel][2]*settings["image"]["color"]["filter"]["blue"], pixels_rgb[row*img_width+pixel][1]*settings["image"]["color"]["filter"]["green"], pixels_rgb[row*img_width+pixel][0]*settings["image"]["color"]["filter"]["red"]), fontsize=1)
        img = img.resize((width, height))
        return img


def main_cam_thread(settings):
    vid = cv2.VideoCapture(0)
    c = 0
    while(True):
        ret, frame = vid.read()
        # cv2.imshow('frame', frame)
        if settings["image"]["flip_x"] == "True":
            frame = cv2.flip(frame, 0)
        if settings["image"]["flip_y"] == "True":
            frame = cv2.flip(frame, 1)
        if settings["image"]["color"]["invert"] == "True":
            frame = cv2.bitwise_not(frame)
            
        if c < 60:
            c = c + 1
        else:
            c = 0
            with open(os.path.join(os.getcwd(), "settings.json")) as f:
                settings = json.load(f)
                f.close()
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        
        ascii, width, height, img_width, img_height, pixels_rgb = convert_to_ascii(img, settings)
        
        ascii_image = generate_img(ascii, width, height, img_width, img_height, pixels_rgb, settings)
        open_cv_image = np.array(ascii_image) 
        cv2.imshow(settings["window"]["name"], open_cv_image)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    vid.release()
    #! Destroy all the windows
    cv2.destroyAllWindows()
    return False




with open(os.path.join(os.getcwd(), "settings.json")) as f:     #? Start!
    settings = json.load(f)
    f.close()



name = "Ascii cam"
cam_thread = threading.Thread(target=main_cam_thread, args=(settings,))
cam_thread.run()