import binascii
import hashlib
import boto3
import sys
import time
import os

BLOCK = 'COMSM0010cloud'
LEADINGZERO = 2


#turn string to binary
def tobin(st):
    return ''.join('{:08b}'.format(b) for b in st.encode('ascii'))
    #print(st, ''.join(format(ord(x), 'b') for x in st.encode('ascii')))
    #return ''.join(format(ord(x, 'b') for x in st.encode('ascii')))

#will be used after turning sstring to binary using tobin function

def tosha(st):
    return hashlib.sha256(st.encode('ascii')).hexdigest()

#adding nonce to ascii string, nonce is decimal number
def addnonce(st, i):
    return st+str(i)

#First nonce is added, with nonce being 'i', then it is turned into binary and SHA256 is applied twice
def wholehashoperation(st, i):
    print(tosha(tosha(tobin(addnonce(st, i)))))
    return tosha(tosha(tobin(addnonce(st,i))))


#return 1 if goldennonce found, return 0 if not, with 'd' being the number of leading 0s needed
def goldennonce(st, d):
    n = '0'
    check = n.zfill(d)
    if st[:d] == check:
        return 1
    else: return 0

def reportBack(url, message):
    print('reporting back to SQS')
    response = sqsclient.send_message(
        QueueUrl= url,
        MessageBody = message
    )


#Can put script. in S3 then use shell script to initiate the python script when setting up new instances
#need to 1. send log to s3 after complete. 2. send message to SQS
#maybe create queue name which is random so there's no 60sec restriction


if __name__ == '__main__':
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    sqsclient = boto3.client('sqs')

    start = int(sys.argv[1])
    end = int(sys.argv[2])
    queueurl = sys.argv[3]
    #t0 = time.clock()
    t0 = time.process_time()
    for i in range (start, end):
        if goldennonce(wholehashoperation(BLOCK, i), LEADINGZERO) == 1:
            print('above is golden nonce, the nonce number is ', i)
            totalTime = time.process_time()-t0
            #totalTime = time.clock()-t0
            reportBack(queueurl, '!nonce number is '+ str(i) + 'time took is ' + str(totalTime))
            break
