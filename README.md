This is a piece of code that find the 'golden nonce'. It is run on multiple AWS server to achieve parallelism for a faster runtime.

user input: N, the number of VM to run the code on
(or the number of hours the user want before computing the nonce value)
user input: D, the difficulty of nonce discovery
user input: T, timeout time before stopping the operation
user input: S, maximum expenditure limit before stopping the operation

all VM will be closed down once a golden once is found and report the nonce value back to the user.
user can terminate operation anny time and log file containing details from start to finish will be returned to the user.

the 'block' of data that we will be adding nonce to is 'COMSM0010cloud' with each character converted to binary via ASCII. The nonce added will be a 32 bit number in binary
