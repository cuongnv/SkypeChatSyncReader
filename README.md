
# SkypeChatSyncReader
Based on source code from this link: https://pypi.python.org/pypi/skype-chatsync-reader
I was modified to fix bug and add new feature (Export feature: Export to HTML like skyperious HTML)

Source code was created by Konstantin Tretyakov

Algorithm and analysis you can read here: http://www.hackerfactor.com/blog/index.php?/archives/231-Skype-Logs.html#c1066

#10 kmn on 2010-10-06 06:47 (Reply)

After my previous post, i was able to get the hang of the \chatsync\(hex).dat files structure. However it will take some time to relate all the extracted variables, handles and id's. I should mention also, that it became obvious chatsync is not an "easy" and 100% effective method of acquiring chat-history, because SOME data IS actually encoded/encrypted, opposed to the plain simple structure of DBB files.

What I know so far ...

#HEADER - 32 bytes
5 bytes: 0x73; 0x43; 0x64; 0x72; 0x07 in ASCII terms "sCdB(bell)"
4 bytes: unsigned int, unix timestamp
4 or more bytes: unsigned int; total data size after header (filesize - 32)
N bytes padding

# Structure Level-1
Chatsync files contain 6 major ("big") blocks of data enumerated #1 - #6. Each of them has a standard header:

Block header - 16 bytes
4 bytes: unsigned int; block data size (in bytes)
4 bytes: unknown id
4 bytes: unsigned int; block number/descriptor (1,2,3,4,5 or 6)
4 bytes padding
Block contents (size specified in header)

# Structure Level-2
Each major block, according to it's descriptor (1-6) has different internal data structure!

Block_types#1,#2,#3 and #4
These blocks share common internal structure so i'll give the common description. The structure is what i've came to call collection of "variable clusters"(records). That is sequence of DBB variables in separate sub-blocks. Each "variable cluster" has the structure

byte 0x41 "A"
byte N 
--
--
DBB variables
--
--
( end of record )

NOTE: 
In addition to 0x00, 0x03, 0x04, there are two distinct data types i've found
0x01 - data is fixed size, with tructure: 0x01 - 7bit code - 8 bytes of data 
0x06 - which is also a mystery but has the structure:
var 1) 0x06 - 7 bit code - 0 
var 2) 0x06 - 7 bit code - !=0 - 7 bit format number

Each "variable cluster"(record) ends with eithter:
- end of block (last record)
- variable type 0x05, followed by a number (meaning unknown to me)
- a zero value for N (empty record)

Example:
65 - start of record
8 - max vars 0 (?)
5 - 0x05 end of record
0 - a number
---------------------
65 - start of record
6 - max vars
3 - 0x03; string
0 - code 0
116 + 
101 +
115 +
116 + 
0 = end of string "test#0"
0 - 0x00; int
1 - code 1
0 - value 0
0 - 0x00; int
3 - code 3
235 +
239 +
230 +
153 +
4 = intValue = 1127856107
5 - 0x05 end of record
1 - a number
---------------------
65 - start of record
0 - empty record !
---------------------
65 - start of record
2 - max var 2
5 - 0x05 end of record
0 - a number
....

Block_type#5...
... is just a collection of 16byte records, containng four 4-byte integer values, which represent message id (as insert into main.dbb or DBB), message handles (relating to block #6) and a field i have no clue about.
Data is aligned, so reading sequence of 32bit integers is straight-forward.

Block_type#6
Now here's where the fun starts. The "0x02/0x03/0x02", "0x03/0x03/0x01" header thing is just a game of chance. What is really stored is this:
A hybrid data structure, containing both aligned (header) and "variable cluster" parts. Here's the common structure:
HEADER - 20 bytes
4byte - integer; handle1
4byte - integer; handle2
4byte - integer; handle3
4byte - integer; handle4
- as to the meaning of these handles... they relate to the id's and handles specified in the other blocks, but i have yet to figure them out.
4bytes - unsigned int; total size of the following records
- if size is 2 bytes, this means following is "65 0" - empty record
DATA
Same rules apply as the structure of #3,#4,#5 blocks. The only difference is that the "end of block" is not end of the major block, but of the data block (started with HEADER).

The blocks containing actual chat messages contain a variable cluster containing a BLOB variable (0x04 data type). 
The size of this binary field is variable and the actual messages is contained INSIDE as a variable of type TEXT (0x03). That's why many have thought there's a 0x03 based "header" to look for.
I've found that these BLOBs contain IP addresses, ports, server information as well as the message itself. The offset at which standart DBB parsing might be attempted is 130 bytes, but this does not hold true in every case ! Also in case of group chats, the BLOBs do not contain the messages in plain text, there is no 0x03/0x02 etc. "header", hence small scale pattern attemps are bound for failure in general.
