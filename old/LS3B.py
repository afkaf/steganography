from bitstring import BitArray
from PIL import Image
import numpy as np
from tqdm import tqdm

def bytes_to_bits(file):
    bits = BitArray(file, endian='little').bin
    nbits = len(bits)
    return bits, nbits

def bits_to_bytes(bits):
    bytestr = BitArray(bin=bits).tobytes()
    return bytestr

def edit_image(img, bits, nbits):
    #print(str(bin(nbits))[2:].rjust(33,'0'))
    bits = str(bin(nbits))[2:].rjust(33,'0') + bits
    nbits = len(bits)
    shape = img.shape
    img = img.flatten()
    for i in tqdm(range(0,nbits//3+2)):
        try:
            threebits = bits[i*3:i*3+3].ljust(3,'0')
            threebitsv = int(threebits,2)%8
        except:
            break
        dif = img[i]%8-threebitsv
        old = img[i].copy()
        new = img[i].copy()
        new = (new + ((8-dif) if dif > 0 else -(8-abs(dif)))) if abs(dif) > 4 else new - dif
        new = new if new <= 255 else new - 8
        new = new if new >= 0 else new + 8
        img[i] = new
        # if i > (nbits//3+1)-50:
        #     print(old, old%8, threebits, threebitsv, dif, new, threebitsv==new%8, abs(old-new))
    return Image.fromarray(img.reshape(shape))

def read_image(img):
    nbits = 0
    bitstr = ''
    img = np.array(img)
    img = img.flatten()
    for i in range(11):
        bitstr += bin(img[i] % 8)[2:].rjust(3,'0')
    size = int(bitstr,2)
    nbits = size//3+12
    bitstr = ''
    for i in tqdm(range(11,nbits)):
        try:
            bitstr += bin(img[i] % 8)[2:].rjust(3,'0')
        except: 
            break
    bitstr = bitstr[:size]
    return bitstr

write = input("Read or write: ")
if 'read' == write.lower():
    write = False
elif 'write' == write.lower():
    write = True

if write:
    secretPath = input('Input file to hide: ')
    containerPath = input('Input container image name: ')
    newname = input('What to name the new image (no extension): ')

    # open file to hide
    with open(secretPath, 'rb') as f:
        infile = f.read()

    # open container image
    im = np.array(Image.open(containerPath).convert(mode='RGB', palette=Image.ADAPTIVE, colors=256))

    # hidden file bits
    filebits, nbits = bytes_to_bits(infile)

    if im.shape[0]*im.shape[1]*im.shape[2]*3 > nbits+33:
        print('working...')
        new_im = edit_image(im, filebits, nbits)
        #new_im = new_im.convert(mode='RGB', palette=Image.ADAPTIVE, colors=256)
        print('Saving image...')
        new_im.save(f'{newname}.png', compress_level=9)
    else:
        print('File too big to store, try a larger image.')
else:
    containerPath = input('Input container image name: ')
    newname = input('What to name the payload: ')
    im = Image.open(containerPath)
    #im = im.convert(colors=256)
    print('working...')
    bitstr = read_image(im)
    bytestr = bits_to_bytes(bitstr)
    print('Saving payload...')
    with open(newname, 'wb+') as f:
        f.write(bytestr)
