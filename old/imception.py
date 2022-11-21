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
	bits = str(bin(nbits))[2:].rjust(32,'0') + bits
	nbits = len(bits)
	shape = img.shape
	img = img.flatten()
	for i in tqdm(range(nbits)):
		if not ((bits[i] == '0' and img[i] % 2 == 0) or (bits[i] == '1' and img[i] % 2 == 1)):
			if img[i] < 255:
				img[i] = img[i]+1
			else: 
				img[i] = img[i]-1
	return Image.fromarray(img.reshape(shape))

def read_image(img):
	nbits = 0
	bitstr = ''
	img = np.array(img)
	shape = img.shape
	img = img.flatten()
	for i in range(32):
		bitstr += str(img[i] % 2)
	nbits = int(bitstr,2)+32
	bitstr = ''
	for i in tqdm(range(32,nbits)):
		bitstr += str(img[i] % 2)
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
	im = np.array(Image.open(containerPath))

	# hidden file bits
	filebits, nbits = bytes_to_bits(infile)

	if im.shape[0]*im.shape[1]*im.shape[2] > nbits+32:
		print('working...')
		new_im = edit_image(im, filebits, nbits)
		new_im = new_im.convert(mode='RGB', palette=Image.ADAPTIVE, colors=256)
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

# bitcombos = ['000','001','010','011','100','101','110','111']

# bitstr = '10101111011011011010010111111110001001011111010011'

# for i in range(0,len(bitstr),3):
# 	int1 = randint(0,255)
# 	str1 = int1%8
# 	str2 = int(bitstr[i:i+3].ljust(3, '0'),2)
# 	dif = str1-str2
# 	new = (int1 + ((8-dif) if dif > 0 else -(8-abs(dif)))) if abs(dif) > 4 else int1 - dif
# 	new = new if new <= 255 else new - 8
# 	newv = new%8
# 	print(f"{int1} {str1} {str2} {dif} {new} {newv} {str2==newv} {abs(int1-new)}")
# dic = {i:[] for i in range(8)}
# for i in range(0,255):
# 	dic[i%8].append(i)
# #print(dic)

# a = 119 
# b = 7 
# c = 2

# print((a+(8-(b-c))%8))
