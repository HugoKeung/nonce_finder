import binascii
import hashlib
import boto3
import time
import sys
import os
import timeit

BUCKETNAME = '16187bucketmark'
QUEUENAME = '16187queue'
IAMPROFILE = '16187profile'
SCRIPTNAME = 'ec2.py'
EC2POLICYARN = 'arn:aws:iam::aws:policy/AmazonEC2FullAccess'
SQSPOLICYARN = 'arn:aws:iam::aws:policy/AmazonSQSFullAccess'
S3POLICYARN = 'arn:aws:iam::aws:policy/AmazonS3FullAccess'

#this function close all the running VMs
def shutdown():
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
    python3 {1} {2} {3} {4} {5} {6}
    echo '!!!!!!!!!!!! ran python script'
    '''.format('s3://{0}/{1}'.format(BUCKETNAME, SCRIPTNAME), SCRIPTNAME, start, end, leading_zero, queue, BUCKETNAME)
    ec2.create_instances(
        ImageId='ami-00068cd7555f543d5', 
        InstanceType='t2.micro',  
        MinCount=1, MaxCount=n, 
        UserData = userdata, 
        IamInstanceProfile = {
            'Name': IAMPROFILE
        }
    )
    return 0


def reportBack(url, message):
    print('reporting back to SQS')
    response = sqsclient.send_message(
        QueueUrl= url,
        MessageBody = message
    )

def receiveMessage(url):
    print('listening to SQS:  {0:.0f} seconds has passed'.format(timeit.default_timer()-t0))
    response = sqsclient.receive_message(
        QueueUrl = url,
        WaitTimeSeconds = 20,
        MaxNumberOfMessages = 10
    )
    
    if 'Messages' in response:
  
        for cnt, message in enumerate(response.get('Messages')):
            
            print(message.get('Body'))
            if (message.get('Body')[0]== '!'):
                nonceFound = 1
                #wait for few seconds before pull data
                getlog(1)
                quitprog()
    
            sqsclient.delete_message(
                QueueUrl=url,
                ReceiptHandle=message.get('ReceiptHandle')
            )

def getlog(done):

    #now get all s3 files that ar relevant and do maths in it
    totaltime = 0 
    totalnum = 0
    loglist=0
    list= []
    while len(list) != VmNum:
        try:
            list = s3client.list_objects(
                Bucket=BUCKETNAME,
                Prefix='result'
            )['Contents']
        except:
            pass
   
    for i in list:

        obj = s3.Object(BUCKETNAME, i['Key'])
        text = obj.get()['Body'].read().decode('utf-8')
        print(i['Key'])        
        print(float(text.split(':')[0]))
        totaltime = totaltime + float(text.split(':')[0])
        totalnum = totalnum + int(text.split(':')[1])

    print('!!!!!!!!!!!!!!!FINAL RESULT BELOW!!!!!!!!!!!!!!!!!!!')
    print('Total time for all VM used: '+str(totaltime) + ' Total number tested is: '+str(totalnum))


def quitprog():
    cleanup()
    print ('total time took (including spinning up VM): ' + str(timeit.default_timer()-t0))
    exit()

def cleanup():
 
    try:
        sqsclient.purge_queue(QueueUrl=queue.url)
    except:
        print('SQS purge queue error')
    try:
        list = s3client.list_objects(
            Bucket=BUCKETNAME,
            Prefix='result'
        )['Contents']
        for i in list:
            obj = s3.Object(BUCKETNAME, i['Key'])
            obj.delete()
    except:
        print('bucket is empty')
    shutdown()
def iamsetup():
    trust_replationship = '''{
        "Version": "2012-10-17",
        "Statement": [
            {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
            }
        ]
    }'''
    try:
        profile = iamclient.create_instance_profile(
            InstanceProfileName=IAMPROFILE
        )
    except:
        print('IAM profile already created')
    try:
        role = iamclient.create_role(
            RoleName='16187role',
            AssumeRolePolicyDocument=trust_replationship
        )
    except:
        print('IAM role already created')

    try:
        response = iamclient.add_role_to_instance_profile(
            InstanceProfileName='16187profile',
            RoleName='16187role',
        )
    except:
        print('Role already attached to profile')
    iamclient.attach_role_policy(
        RoleName= '16187role',
        PolicyArn=EC2POLICYARN
    )
    iamclient.attach_role_policy(
        RoleName= '16187role',
        PolicyArn=SQSPOLICYARN
    )
    iamclient.attach_role_policy(
        RoleName= '16187role',
        PolicyArn=S3POLICYARN
    )

#SECRET KEY TO BE PUT IN ENVIRONMENT AFTER TESTING
#Can put script. in S3 then use shell script to initiate the python script when setting up new instances
#if message matches then instantly terminate VM
#queue is also deleted to save resources

if __name__ == '__main__':
    nonceFound = 0
    if (len(sys.argv)!=4):
        print('Please follow the format: python3 client.py <VM Number> <Leading Zero> <Timeout>')
        print('Put 0 in <Timeout> if you prefer not to use that function')
        exit()
    t0 = timeit.default_timer()
    VmNum = int(sys.argv[1])
    leading_zero = int(sys.argv[2])
    timeout = int(sys.argv[3])
    NonceRange = 2147483647

    s3client = boto3.client('s3')
    s3 = boto3.resource('s3')
    ec2 = boto3.resource('ec2')
    sqs = boto3.resource('sqs')
    s3client = boto3.client('s3')
    sqsclient = boto3.client('sqs')
    iamclient = boto3.client('iam')
    iamsetup()
    #cleaning the environment first, setting everything to new state
    queue = sqs.create_queue(QueueName = QUEUENAME, Attributes={'VisibilityTimeout': '1'})
    try:
        s3client.create_bucket(
            ACL='private',
            Bucket = BUCKETNAME
        )
    except Exception as e:
        print(str(e))
###
###
###
###
#
    s3.Object(BUCKETNAME,SCRIPTNAME).put(Body=open(SCRIPTNAME,'rb'))
    cleanup()
    for i in range (0, VmNum):
        start = int(NonceRange/VmNum * i)
        end = int(NonceRange/VmNum * (i+1))
        launchVM(1,start,end, queue.url)
    try:
        while (nonceFound == 0):
            if timeout!=0:
                if timeit.default_timer()-t0 > timeout:
                    reportBack(queue.url, '!timeout')
                    timeout=0
            receiveMessage(queue.url)
    except KeyboardInterrupt:
        reportBack(queue.url, '!interrupted')    
        print('Interrupted by user')
        while (1):
            receiveMessage(queue.url)


