import binascii
import hashlib
import boto3


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
    return 0

#launch number of VM specified by the user. To be implemented
def launchVM():
    print('launching VM')
    return 0

#SECRET KEY TO BE PUT IN ENVIRONMENT AFTER TESTING
if __name__ == '__main__':
    ec2 = boto3.resource('ec2', region_name='us-east-1', aws_accesskey_id='', aws_secret_access_key='')
    instance = ec2.create_instances(
     ImageId='ami-1e299d7e',
     MinCount=1,
     MaxCount=1,
     InstanceType='t2.micro')
    print(instance[0].id)
    print(instance)
#    for i in range (0, 3600):
 #       if goldennonce(wholehashoperation('COMSM0010cloud', i), 3) == 1:
  #          print('above is golden nonce, the nonce number is ', i)
   #         shutdown()



