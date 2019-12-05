import binascii
import hashlib
import boto3
import sys
import time
import os
import threading
import _thread
import timeit
import urllib.request

BLOCK = 'COMSM0010cloud'

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
    #print(tosha(tosha(tobin(addnonce(st, i)))))
    return tosha(tosha(tobin(addnonce(st,i))))


#return 1 if goldennonce found, return 0 if not, with 'd' being the number of leading 0s needed
def goldennonce(st, d):
    n = '0'
    check = n.zfill(d)
    if st[:d] == check:
        return 1
    else: return 0

def reportBack(url, message):
   # print('!!reporting back to SQS')
    #it is only calling this function when either nonce is found or all numbers allocated are tested
  #  sendlog()
    response = sqsclient.send_message(
        QueueUrl= url,
        MessageBody = message
    )
    

def receiveMessage(url):
    #print('listening to SQS')
    response = sqsclient.receive_message(
        QueueUrl = url,
        WaitTimeSeconds = 5
    )
    #send log every 20 secodns for 'backup' just in case if the client terminate the ec2 before they can send log
   # sendlog()
    #print(response.get('Messages')[0].get('Body'))
    if 'Messages' in response:
        for message in response.get('Messages'):
            
            print(message.get('Body'))
            if (message.get('Body')[0]== '!'):
                done=1
                print(message.get('Body'))
                sendlog()
                os.exit(1)
def receiveMessageInThread(url):
    global done
    while (done==0):
        receiveMessage(url)

def sendlog():
    log = open('!{0}.txt'.format(start), 'w')
    timenow = timeit.default_timer()-t0
    log.write(str(timenow)+':'+str(numTested)+':'+str(nonceFound))
    reportBack(queueurl,'sending log from{0}'.format(start))
    log.close()
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).upload_file('!{0}.txt'.format(start), 'result/!{0}.txt'.format(start))
    print('log uploaded')
    logsent=1

#Can put script. in S3 then use shell script to initiate the python script when setting up new instances
#need to 1. send log to s3 after complete. 2. send message to SQS
#maybe create queue name which is random so there's no 60sec restriction

#TODO receive message sync
#TODO threading cause wrong number for number tester variable
if __name__ == '__main__':
    print('starting script')

    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    sqsclient = boto3.client('sqs')
    ec2 = boto3.resource('ec2')
    
    numTested = 0
    totalTime = 0
    nonceFound = 0
    done=0
  

    start = int(sys.argv[1])
    end = int(sys.argv[2])
    leading_zero = int(sys.argv[3])
    queueurl = sys.argv[4]
    bucket = sys.argv[5]
    response = urllib.request.urlopen("http://169.254.169.254/latest/meta-data/instance-id")
    instance_id = response.read().decode('utf-8')

    startmessage = 'script is starting for number {0} to {1}'.format(start, end)
    reportBack(queueurl, startmessage)
    receiveMessage(queueurl)
    t0 = timeit.default_timer()
    try:
        threading.Thread(target = receiveMessageInThread, args=(queueurl,)).start()
    except:
        print ('unable to start thread, calculation will not stop till the end')

    for i in range (start, end):
        numTested = numTested + 1
        
        if goldennonce(wholehashoperation(BLOCK, i), leading_zero) == 1:
            print('!!!!!!!!!above is golden nonce, the nonce number is ', i)
            totalTime = timeit.default_timer()-t0
            nonceFound = 1
            done=1
            reportBack(queueurl, '!nonce number is '+ str(i) + ' Time took is ' + str(totalTime))
            sendlog()
    print('no nonce')  
    reportBack(queueurl, 'No nonce found within range {0} and {1}'.format(start, end))
    sendlog()


