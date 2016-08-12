#ISPA
#Receives packets from R2 and then counts which packets are going to which
#subnets

from socket import *
from math import*
from time import*


#takes an IP address and an Address and tells if that IP is less than
# or equal to the specified address by looking at one dot at a time.
#RETURN- Boolean
#PARAM- 2 Strings
def lessThanEq(IP,Add):  
  isLess = False

  #if the first number less or equal to first number and second to second and so on...
  if (int(IP.split(".")[0])<=int(Add.split('.')[0])):
    if (int(IP.split(".")[1])<=int(Add.split('.')[1])):
      if (int(IP.split(".")[2])<=int(Add.split('.')[2])):
        if (int(IP.split(".")[3]) <= int(Add.split('.')[3])):
          #then it is less than
          isLess = True
          
          
  return isLess


#takes an IP address and an Address and tells if that IP is greater than
# or equal to the specified address by looking at one dot at a time.
#RETURN- Boolean
#PARAM- 2 Strings    
def greaterThanEq(IP,Add):
  isGreater = False

  #if the first number is greater than or equal to first number and second to second and so on..
  if (int(IP.split(".")[0])>=int(Add.split('.')[0])):
    if (int(IP.split(".")[1])>=int(Add.split('.')[1])):
      if (int(IP.split(".")[2])>=int(Add.split('.')[2])):
        if (int(IP.split(".")[3])>=int(Add.split('.')[3])):
          isGreater = True
          
  return isGreater
  

#Takes IP address and an array of addresses and determines which subnet the address
#should go to 
#RETURN- integer index or -1 if does not belong in any subnet 
#PARAM- 1 String an 1 Array
def subnetMatch(IP, addressArr):
    isFound = False
    for address in addressArr:

      #check to see if IP address in subnet range
      if (greaterThanEq(IP,address.split(',')[0]) and lessThanEq(IP,address.split(',')[1])):
          index = addressArr.index(address)
          #once it finds subnet it belongs to it breaks out
          isFound = True
          break
    
    if (isFound == True):
        return index
    else:
        return -1
    

#Reads in forwarding table from ispa_ftable.txt and creates two arrarys
# 1 containing tuples  of each subnet's min and max (1 string with each seperated by comma)and another parallel array
# which corresponds to each number subnet the addresses correspond to
#RETURN- 2  Arrays
#PARAM- 
def fowardingTable():

     #open the file
    inFile = open("ispa_ftable.txt", 'r', encoding = "utf-8")
    subnetArray=[]
    addressArray = []

    
    for line in inFile:

      #parse out the IP and the subnet number
        line = line.strip("\ufeff")
        slashbegin = line.find("/")+1
        slashend = line.find(" ")
        slash = line[slashbegin:slashend]

      
        IP = line[:slashbegin-1]
        IP3 = IP.split(".")[0]
        IP2 = IP.split(".")[1]
        IP1 = IP.split(".")[2]
        IP0 = IP.split(".")[3]
        
        subnetindex = line.find("SUB")
        subnetsearch = line[subnetindex:]
        subnetNum = ""
        for w in subnetsearch:
          if w!=" " and w!="S" and w!="U" and w!="B" and w!="\n":
            subnetNum = subnetNum + w
        subnetArray.append(subnetNum)
        
       
        #convert slashed notation to decimal dot notation

        #determine how many 'free' bits you have to work with
        free = 32-int(slash)
        #special case that all 32 fixed
        if free ==0:
          group =-1

        #special case that 8, 16,or 24 numbers are fixed (multiple of 8)
        if free%8==0:
          group = free//8 -1
          
        #figure out which dot you will be adding to 
        else:
          group = free//8

        #if you are adding to group 0 then you are just chaning the first dot
        if (group ==0):
            maxNum = (2**free)-1
            maxDot0Range = int(IP0)+maxNum
            IPMax = IP3+"."+IP2+"."+IP1+"."+str(maxDot0Range)
            Range = IP +","+IPMax
            #comput max and min then put both into Array as one string seperated by comma
            addressArray.append(Range)
            
        #if you are adding to second group then you not only have to add
        #whatever remainder to the second group but also increase the
        #first group by 255
        elif (group ==1):
            maxNum = (2**(free-8))-1
            maxDot0Range = int(IP0)+255
            maxDot1Range = int(IP1)+ maxNum
            IPMax = IP3+"."+IP2+"."+str(maxDot1Range)+"."+str(maxDot0Range)
            Range = IP +","+IPMax
            addressArray.append(Range)

        #similar to group 2
        elif (group ==2):
            maxNum = (2**(free-16))-1
            maxDot0Range = int(IP0)+255
            maxDot1Range = int(IP1)+ 255
            maxDot2Range = int(IP2)+maxNum
            IPMax = IP3+"."+str(maxDot2Range)+"."+str(maxDot1Range)+"."+str(maxDot0Range)
            Range = IP +","+IPMax
            addressArray.append(Range)

        #similar to group 2
        elif (group==3):
            maxNum = (2**(free-24))-1
            maxDot0Range = int(IP0)+255
            maxDot1Range = int(IP1)+ 255
            maxDot2Range = int(IP2)+255
            maxDot3Range = int(IP3)+maxNum
            IPMax = str(maxDot3Range)+"."+str(maxDot2Range)+"."+str(maxDot1Range)+"."+str(maxDot0Range)                                
            Range = IP +","+IPMax
            addressArray.append(Range)
            
        #if all 32 bits fixed then no range  
        elif (group ==-1):
            Range = IP +","+IP
            addressArray.append(Range)

    return addressArray, subnetArray

def main():
    ISPAPort = 11000
    ISPASocket = socket(AF_INET, SOCK_DGRAM)
    ISPASocket.bind(('',ISPAPort))
    addressArray, subnetArray = fowardingTable() #In addressArray each element is a range of address for certain subnet
                                                  #SubnetArray is parallel array with addressArray and tells subnet number
                                                  #  which corresponds to those addresses
    #create array called counts with the number of entries equaling however many subnets there are
    counts=[]
    NumSubnets = len(subnetArray)
    for i in range(NumSubnets):
        counts.append(0)
        
    print ("ISPA is read to receive")

    #receive forever
    while 1:
      
      #receive from R2
        message, R2address = ISPASocket.recvfrom(2048)
        message = message.decode()
        IPAddress = message.split("\n")[0]
        message = message.split("\n")[1]

        #figure out which subnet the IP goes to 
        subnetNumIndex = subnetMatch(IPAddress,addressArray)
        
        if (subnetNumIndex!=-1):

            #print some blank space to look nice then increase count of
            #proper subnet
            print ("\n" * 30)
            counts[subnetNumIndex]=counts[subnetNumIndex]+1
            for i in range(NumSubnets):
                print("Subnet "+subnetArray[i]+": "+ str(counts[i])+"\n")
            
        #else address does not belong in any of ISP A's subnets

main()
