from bitstring import BitArray
from PIL import Image
from tqdm import tqdm
import numpy as np

cimg = 'container.png'
simg  = 'secret.jpg'

def bytes_to_bits(file):
	bits = BitArray(file, endian='little').bin
	return bits

def bits_to_bytes(bits):
    bytestr = BitArray(bin=bits).tobytes()
    return bytestr

def get_file(path):
	with open(path, 'rb') as f:
		return f.read()

def get_container(path):
	img = np.array(Image.open(path))
	return np.unpackbits(img.flatten()), img.shape

#get container
container, shape = get_container(cimg)

#get secret
secret = bytes_to_bits(get_file(simg))
header = bin(len(secret))[2:].rjust(32, '0')

#write secret
container[7:32*8+len(secret)*8:8] = np.array([int(i) for i in tqdm(header+secret)])
Image.fromarray(np.packbits(container).reshape(shape)).save('secret_container.png', compress_level=9)

#read secret
extracted_header = int(''.join([str(i) for i in container[7:32*8:8]]),2)
extracted_secret = ''.join([str(i) for i in tqdm(container[7+32*8:32*8+extracted_header*8:8])])
print(extracted_secret==secret)
with open('extracted_secret.jpg', 'wb+') as f:
	f.write(bits_to_bytes(extracted_secret))

