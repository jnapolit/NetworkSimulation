#R1 router 
#Will randomly generate IP's within two certain ranges and send to R2 with a
#payload

from random import*
from time import*
from socket import*

R2Name = "localhost"
R2Port = 10000
R1Socket = socket(AF_INET, SOCK_DGRAM)
print("R1 about to send messages")

t = 0 #to keep track of time sent
x = 1/6  #to pace when packets are sent out
text = "This is the payload. Networks rocks." #fixed payload 

#repeat sending packets without stopping
while 1:
    
    #Sleep for 1/6 of a second and send packet with IP addresses ranging
    #from 130.0.128.0-130.0.191.255 with payload to R2

    sleep(x)

    #randomly generate IP
    dot3 = str(randint(128,191))
    dot4 = str(randint(0,255))

    #concatenate to make IP
    IPAddress = "130.0."+dot3+"."+dot4

    #Keep track of time
    t=t+(1/6)

    #log what happens and then send IP with payload to R2
    print("AT TIME: " + str(t) +" SENDING TO: " + IPAddress + " WITH PAYLOAD: " + text)
    message = IPAddress + '\n' + text
    R1Socket.sendto(message.encode(),(R2Name,R2Port))




    #Sleep for antoher 1/6 of a second and send two packets. One with IP addresses ranging
    #from 130.0.128.0-130.0.191.255 with payload and another with IP ranging
    #from 130.0.0.0 - 130.0.63.255 with payload to R2
    
    sleep(x)

    #randomly generate IP 
    dot3 = str(randint(128,191))
    dot4 = str(randint(0,255))

    #concatenate to make IP
    IPAddress = "130.0."+dot3+"."+dot4

    #keep track of time
    t=t+(1/6)

    #log what happens and then send IP with payload to R2
    print("AT TIME: " + str(t) +" SENDING TO: " + IPAddress + " WITH PAYLOAD: " + text)
    message = IPAddress + '\n' + text
    R1Socket.sendto(message.encode(),(R2Name,R2Port))

    #repea processes with other range and also send to R2
    dot3 = str(randint(0,63))
    dot4 = str(randint(0,255))
    IPAddress = "130.0."+dot3+"."+dot4
    print("AT TIME: " + str(t) +" SENDING TO: " + IPAddress + " WITH PAYLLOAD: " + text)
    message = IPAddress + '\n' + text
    R1Socket.sendto(message.encode(),(R2Name,R2Port))



