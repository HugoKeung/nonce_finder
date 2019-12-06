**What is this?**

This is a piece of code that find the 'golden nonce'. The 'block' of data that we will be adding a nonce value to is 'COMSM0010cloud', with each characters encoded as ASCII and converted to binary at the end. This binary value will then be hashed through SHA256 for two times. If the number of leading '0' in the hashed value is equal to or higher than the difficulty user specified then the value is considered as a 'golden nonce'.
User can specify the number of AWS EC2 to run on to achieve parallelism for a faster runtime. Once the 'golden nonce' is found, the value will be printed out and any EC2 created for the task will be terminated. 

**Before running the script...**

Please ensure the following is installed before running the script
- Python3
- Boto3

AWS credentials also has to be set up on the local machine. This can be done through AWSCLI or setting it up directly through the credentials file under ~/.aws/credentials of your local machine.
For a more detailed information on how to set up your local aws credentials, please refer to the following link:
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration 

Due to restrictions of S3 naming in AWS, you may have to go into the python file named 'client.py' and change the string under 'BUCKETNAME' to something unique.

Please also make sure that the file 'ec2.py' is in the same directory you are running 'client.py'

To run the script type in the following command
python3 client.py <N> <D> <T>
with <N> being the number of VM to run the code on
with <D> being the difficulty. It is the number of leading zeros you want to find in the nonce value.
with <T> being the timeout (in seconds) before the programme shuts itself. The time starts counting when user run the script. Put in 0 if you prefer not to have a timeout.

User can also press Ctrl+C to interrupt the programme. Log will be pulled from the EC2 before exiting.

*Beware that since the EC2 usually take 60-120 seconds before fully started up, so any time under 60-120 seconds may mean that the EC2 will be shutdown right after it is started up and no meaningful computation will be made.



