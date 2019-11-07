import binascii
import hashlib

#turn string to binary
def tobin(st):
    return ''.join('{:08b}'.format(b) for b in st.encode('ascii'))

#will be used after turning sstring to binary using tobin function
def tosha(st):
    return hashlib.sha256(st.encode('ascii')).hexdigest()

#adding nonce to ascii string, nonce is decimal number
def addnonce(st, i):
    return st+str(i)

#addnonce to multiple numbers
def addmultinonce(st, start, end):
    list = []
    for i in range (start, end):
        list.append(addnonce(st, i))
    return list

#whole operation to apply after the nonce is added. First string is turn to binary, then SHA is applied twice
def wholeoperation(st):
    return tosha(tosha(tobin(st)))


if __name__ == '__main__':
    print(wholeoperation('hello5'))
