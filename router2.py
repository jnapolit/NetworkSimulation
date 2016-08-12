#R2
#Will recieve packets from R1 and then use longest prefix and a forwarding table
#to determine which ISP to then send the packets to

from socket import *
from time import*


#takes a binary number and pads it so that it
#is 8 bits (attaches proper leading zeros)
#RETURN- String
#PARAM- String
def padding(IP):
    if (8-len(IP)!=0):
        x = 8-len(IP)
        pad = ""
        for i in range(x):
            pad = pad+"0"
        IP = pad +IP
    return IP
    
#Takes a dotted IP address in decimal and then converts it to a
#32 bit IP address in binary with spaces in between each 8 bits
#RETURN- String
#PARAM- String
def convert(IP):
    
    #splits to get each of the 4 numbers in IP address
    IP1 = IP.split('.')[0]
    IP2 = IP.split('.')[1]
    IP3 = IP.split('.')[2]
    IP4 = IP.split('.')[3]

    #converts each of the 4 decimal numbers to binary 
    IP1B = str(bin(int(IP1)))[2:]
    IP2B = str(bin(int(IP2)))[2:]
    IP3B = str(bin(int(IP3)))[2:]
    IP4B = str(bin(int(IP4)))[2:]

    #adds the proper leading zeros so that each is 8 bits
    IP1B = padding(IP1B)
    IP2B = padding(IP2B)
    IP3B = padding(IP3B)
    IP4B = padding(IP4B)
    
    #concatenates them all into one IP address  
    IPAddress = IP1B +" "+ IP2B +" " + IP3B +" " + IP4B
    
    return IPAddress

#reads in the forwarding table from a file called 'router2_ftable.txt"
#and parses out the binary numbers with the stars into an array which 
#has a parallel array which contains which link the binary corresponds to.  
#RETURN- 2 Arrays
#PARAM- 
def forwardingTable():

    #initiate arrays and open file
    AddressArray = []
    LinkArray = []
    inFile = open("router2_ftable.txt", 'r', encoding = "utf-8")

    for line in inFile:
        
        forwardingNum = ""
        
        #find where the first * is in the line. Note this does not account for the
        #case when there are no stars in the line though
        fixedNumEndIndex = line.find('*')
        
        #find where the actual binary number begins (file hadd some line characters
        #prior to binary in line)
        fixedNumBeginIndex = min(line.find('0'), line.find('1'),line.find('*'))

        #parse out the binary part and if the line isn't empty and we have
        #an address then append it to the array
        forwardingNum = line[fixedNumBeginIndex:fixedNumEndIndex]
        if forwardingNum!="":
            AddressArray.append(forwardingNum)

        #after the binary had been added, look for the corresponding link that
        #addresses matching that binary should go to 
        linkNumSearch = line[fixedNumEndIndex:]
        for w in linkNumSearch:
            if w!='*' and w!=" " and w!='\n':
                LinkArray.append(w)

    return AddressArray, LinkArray


#Takes in IP and an array of binary addresses and checks to see which one of the
#address the IP matches with for the longest (returns index of link and need
#to index into the parralel link array to determine which link it is)
#RETURN- 1 String, 1 Array
#PARAM- -1 if it does not match with any addresses, integer index

def LongestPrefixMatcher(IP, AddressArr):
    
    numberLines = len(AddressArr) #number of lines in forwarding table
    scores = [] #array to put each score into after each iteration, then find min
                #and that line will be longest prefix matching

    #go through each number in the AddressArr
    for i in range(numberLines):
        score = 0
        forwardTab = AddressArr[i]
        length = len(forwardTab)
        #for each number in the address from forwarding table 
        for j in range(length):
            #if the number matches the number in the IP address increase score
            if forwardTab[j]==IP[j]:
                score = score +1
            #if it does not match then break out and whateve score is is final 
            else:
                break
        #keep score of each address in array
        scores.append(score)

    #find highest score
    LongestMatch = max(scores)

    #if the highest score is 0 then it matches with none
    if LongestMatch ==0:
        return -1
    #else find which address had the highest score
    else:
        return scores.index(LongestMatch)
    


def main():
    ISPAName = "localhost"
    ISPAPort = 11000
    ISPBName = "localhost"
    ISPBPort = 12000
    R2Port = 10000
    R2Socket = socket(AF_INET, SOCK_DGRAM)
    R2Socket.bind(('',R2Port))
    AddressArray, LinkArray = forwardingTable() #get forwarding table into array
    
    print ("R2 is read to receive")

    #continue to recieve until forever
    while 1:

        #receive message from R1
        message, R1address = R2Socket.recvfrom(2048)
        message = message.decode()
        IPAddress = message.split('\n')[0]
        text = message.split('\n')[1]
        print ("IP address: " + IPAddress + " Message: " + text)

        #take the IP address received in dot decimal form and convert to
        #binary non dot form
        binaryDotAddress = convert(IPAddress)

        #pass this formatted IP into the LongestPrefixMatcher to determine
        #which link it should go on 
        LinkIndex = LongestPrefixMatcher(binaryDotAddress, AddressArray)

        #If address did match with at least one
        if (LinkIndex != -1): 
            Link = LinkArray[LinkIndex]

        #otherwise set to 100 and then it will be dropped
        else:
            Link = '100'


        #if it's going to link 0 then send to ISPA  
        if (Link=='0'):
            R2Socket.sendto(message.encode(),(ISPAName,ISPAPort))
            #send message to ISPA

        #if its going to link 1 then send to ISPB   
        elif(Link=='1'):
            R2Socket.sendto(message.encode(),(ISPBName,ISPBPort))
            #send message to ISPB
        
        #else Link = 100 in which we should drop it since it does
        #not belong to either
        
            
           
   
main()


