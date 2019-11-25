import binascii
import hashlib
import boto3
import time
import sys
import os

SQSURL = 'https://sqs.us-east-1.amazonaws.com/971030030830/16187queue'
IAMARN = 'arn:aws:iam::971030030830:instance-profile/ec2s3sqs'
IAMNAME = 'ec2s3sqs'
S3SCRIPT = 's3://16187tester/ec2.py'
SCRIPTNAME = 'ec2.py'

#turn string to binary
def tobin(st):
    return ''.join('{:08b}'.format(b) for b in st.encode('ascii'))

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

#this function close all the VMs, detail of the function to be implemented
def shutdown():
    print('shut down')
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    for instance in instances:
        #print(instance.id, instance.instance_type)
        instance.terminate()
    return 0

#launch number of VM specified by the user. To be implemented
def launchVM(n, start, end, queue):
    print('launching VM')
    #is all t2.micro by default
    userdata = '''
    #!/bin/bash
    echo '!!!!!!!!!!!!!!!!!! pulling form S3'
    aws s3 cp {0} .
    sudo yum install python3 -y
    yes | pip3 install --user boto3
    echo '!!!!!!!!!!finish loading boto3'
    python3 {1} {2} {3} {4}
    echo '!!!!!!!!!!!! ran python script'
    '''.format(S3SCRIPT, SCRIPTNAME, start, end, queue)
    ec2.create_instances(
        ImageId='ami-00068cd7555f543d5', 
        InstanceType='t2.micro',  
        MinCount=1, MaxCount=n, 
        UserData = userdata, 
        IamInstanceProfile = {
            'Arn': IAMARN
        }
    )
    return 0


def reportBack():
    print('reporting back to SQS')
    response = sqsclient.send_message(
        QueueUrl= SQSURL,
        MessageBody = 'this is the message body'
    )

def receiveMessage(url):
    print('listening to queue')
    response = sqsclient.receive_message(
        QueueUrl = url,
        WaitTimeSeconds = 20
    )

    #nonceFound = 1
    
    #print(response.get('Messages')[0].get('Body'))
    if 'Messages' in response:
        if (response.get('Messages')[0].get('Body')[0]== '!'):
            print(response.get('Messages')[0].get('Body'))
            nonceFound = 1
            #wait for few seconds before pull data
            time.sleep(5)
            sqsclient.purge_queue(QueueUrl=queue.url)
            getlog()

            shutdown()
            quitprog()

def getlog():
    s3client = boto3.client('s3')
    s3 = boto3.resource('s3')
    totaltime = 0 
    totalnum = 0
    #now get all s3 files that ar relevant and do maths in it
    list = s3client.list_objects(
        Bucket='16187tester',
        Prefix='result'
    )['Contents']
 #   print(list)
    for i in list:
        obj = s3.Object('16187tester', i['Key'])
        text = obj.get()['Body'].read().decode('utf-8')
        totaltime = totaltime + float(text.split(':')[0])
        totalnum = totalnum + int(text.split(':')[1])
        obj.delete()

    print('Total VM time took is: '+str(totaltime) + 'Total number tested is: '+str(totalnum))
    #remove everything after finish getting log

def quitprog():
    print ('total time took (including spinning up VM): ' + str(time.process_time()-t0))
    exit()


#SECRET KEY TO BE PUT IN ENVIRONMENT AFTER TESTING
#Can put script. in S3 then use shell script to initiate the python script when setting up new instances
#if message matches then instantly terminate VM
#queue is also deleted to save resources

if __name__ == '__main__':
    nonceFound = 0
    if (len(sys.argv)!=2):
        print('wrong arg')
        exit()
    t0 = time.process_time()
    ec2 = boto3.resource('ec2')
    sqs = boto3.resource('sqs')
    s3client = boto3.client('s3')
    sqsclient = boto3.client('sqs')
    VmNum = int(sys.argv[1])
    NonceRange = 2147483647
    #NonceRange = 4000

    queue = sqs.create_queue(QueueName = '16187queue')
    
    for i in range (0, VmNum):
        start = int(NonceRange/VmNum * i)
        end = int(NonceRange/VmNum * (i+1))
        launchVM(1,start,end, queue.url)
    while (nonceFound == 0):
        receiveMessage(queue.url)

