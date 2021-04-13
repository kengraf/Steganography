# Python3 program to illustrate Iamge based stebanogrphy
# This code was written to support a Python security lab
# in UNH's 2021 GenCyber camp

# Read/Write images using OpenCV-Python.
# It is a library of Python bindings designed to solve computer vision problems. 
from PIL import Image
import numpy
import os

EOM = "<EOM>" # you can use any string as the end of message delimeter

def messageToBinary(message):
    if type(message) == str:
        return ''.join([ format(ord(i), "08b") for i in message ])
    elif type(message) == bytes or type(message) == numpy.ndarray:
        return [ format(i, "08b") for i in message ]
    elif type(message) == int or type(message) == numpy.uint8:
        return format(message, "08b")
    else:
        raise TypeError("Input type not supported")


# hide 'data' in 'image_name' 
# 'key' format is 'XY', X = is R,G, or B: Y is bit position 1 for LSB
def encode(image_name, secret_message, key):
    
    image = Image.open(image_name)

    #Check if the number of bytes to encode is less than the maximum bytes in the image
    n_bytes = image.height * image.width * 3 // 8
    if len(secret_message) > n_bytes:
        raise ValueError("Error encountered insufficient bytes, need bigger image or less data !!")

    secret_message += EOM 
    keyColor = key[0]
    keyBit = 8 - int(key[1])
    
    data_index = 0
    # convert input data to binary format using messageToBinary() fucntion
    binary_secret_msg = messageToBinary(secret_message)

    data_len = len(binary_secret_msg) #Find the length of data that needs to be hidden
    for x in range(0, image.width):
        for y in range(0, image.height):
            pixel = list(image.getpixel((x, y)))
            # Break out of the loop once all the data is encoded
            if data_index >= data_len:
                break
            
            # convert RGB values to binary format
            if( keyColor == 'R' or keyColor == 'r' ):
                r = messageToBinary(pixel[0])
                xx = r[:keyBit] + binary_secret_msg[data_index] + r[keyBit+1:];
                pixel[0] = int(xx, 2)
            if( keyColor == 'G' or keyColor == 'g' ):
                g = messageToBinary(pixel[1])
                xx = g[:keyBit] + binary_secret_msg[data_index] + r[keyBit+1:];
                pixel[1] = int(xx, 2)
            if( keyColor == 'B' or keyColor == 'b' ):
                b = messageToBinary(pixel[2])
                xx = b[:keyBit] + binary_secret_msg[data_index] + r[keyBit+1:];
                pixel[2] = int(xx, 2)
                
            data_index += 1
            image.putpixel((x,y), tuple(pixel))
            
    return image

def decode(image_name, key):

    image = Image.open(image_name)

    binary_data = ""
    keyColor = key[0]
    keyBit = 8 - int(key[1])
    
    for x in range(0, image.width):
        for y in range(0, image.height):
            pixel = list(image.getpixel((x, y)))
            if( keyColor == 'R' or keyColor == 'r' ):
                r = messageToBinary(pixel[0])
                binary_data += r[keyBit]
            if( keyColor == 'G' or keyColor == 'g' ):
                g = messageToBinary(pixel[1])
                binary_data += g[keyBit]
            if( keyColor == 'B' or keyColor == 'b' ):
                b = messageToBinary(pixel[2])
                binary_data += b[keyBit]

    # convert from bits to characters
    all_bytes = [ binary_data[i: i+8] for i in range(0, len(binary_data), 8) ]
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == EOM: #check if we have reached the end of message
            break

    # remove the delimeter and return the original hidden message
    return decoded_data[:-5] 

# write the encoded image data to filename
def write(filename, encoded_image ):
    return encoded_image.save(filename,'png')
    
    
# Try simple message on small image, changing the low red bit
def selfTest2(): 
    message = "Into the valley of death rode the 600 hundred"
    coverFilename = "Charge600.jpg"
    secretFilename = "secret.jpg"
    key = 'R1'
    
    secretData = encode( coverFilename, message, key )
    if( secretData == 0 ): return False
    
    success = write(secretFilename, secretData )
    if( success == False ):
        print("failed to write file: " + secretFilename )
        return False

    # Reverse the process
    dtext = decode( secretFilename, key )
    return dtext == message

def selfTest():
    types = ("png","jpeg","bmp")
    channel = ("R","G","B")
    testNum = 0
    secret = "test secret message"
    
    for t in types:
        img = Image.new("RGB", (100,100))
        fileT = "test."+t
        img.save(fileT, format=t)
        for o in types:
            fileO = "secret."+o
            key = channel[testNum%3] + str(testNum%8+1)
            i = encode(fileT, secret, key)
            write(fileO, i)
            pText = decode(fileO, key)
            result = ": Passed" if secret == pText else ": Failed"
            print("Test " + t + "->" + o + result )
            if secret != pText:
                return False
            os.remove(fileO)
        os.remove(fileT)
    return True
            
# Module test code
if __name__ == "__main__":
    print( "Tests passed" if selfTest2() else "Failed" )