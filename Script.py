#Written by Andre Boehm
print ("Starter rapport skript")
import smtplib, os, sys, time, spidev
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

#Variabler
fraepost = "From mail"
tilepost = "mail-1,mail-2"
datoogtid = time.strftime('%A %d.%B - %H:%M')
dato = time.strftime('%d.%B')
tid = time.strftime('%H:%M')
temp_channel  = 0

#CAM
os.system('fswebcam --no-banner /home/pi/campicture/picture.jpg')
filename = "picture.jpg"
attachment = open("/home/pi/campicture/picture.jpg", "rb")

#TEMP
# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
 
# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data
 
# Funksjon for konvertering av "data" til volt
def ConvertVolts(data,places):
  volts = (data * 3.3) / float(1023)
  volts = round(volts,places)
  return volts

# Funksjon for beregning av F basert pa volt 
def ConvertTempF(data,places):
  tempf = data*100
  tempf = round(tempf,places)
  return tempf

# Funksjon for konvertering av F til C  
def ConvertTempC(data,places):
  tempc = (data -32) * 5.0/9.0
  tempc = round(tempc,places)
  return tempc

# Funksjon for lese bildedato
bildedato = time.ctime(os.path.getmtime("/home/pi/campicture/picture.jpg"))

# Read the temperature sensor data
temp_level = ReadChannel(temp_channel)
temp_volts = ConvertVolts(temp_level,2)
tempf      = ConvertTempF(temp_volts,2)
tempc      = ConvertTempC(tempf,2)
#temp = ConvertTemp(temp_volts,2)
tempmail = ("{}C ({}V)".format(tempc,temp_volts))

##-------------------------variabler og funksjoner-------------------------##

def main():
    print

    #GMail settings
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        print 'Connection to Gmail succesessfully'
        print 'Connected to Gmail' + '\n'
        try:
            server.login("Logon Google account", "Password token")
        except smtplib.SMTPException:
            print
            print 'Authentication failed' + '\n'
            smtpserver.close()
            getpass.getpass('Press ENTER to continue...')
            sys.exit(1)

    except (socket.gaierror, socket.error, socket.herror, smtplib.SMTPException), e:
        print 'Connection to Gmail failed'
        print e
        getpass.getpass('Press ENTER to continue...')
        sys.exit(1)
    #Attachment settings
    msg = MIMEMultipart()

    msg['From'] = fraepost
    msg['To'] = tilepost
    msg['Subject'] = 'Subject - ' + datoogtid
 
    body = 'Mailen er generert: ' + dato + " - " + tid + '\n' + 'Temperatur: ' + tempmail + '\n' + 'Bildedato: ' + bildedato + '\n' + '\n' + 'Best Regards ... :)'

    msg.attach(MIMEText(body, 'plain'))
   
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
     
    msg.attach(part)

    try: 
        text = msg.as_string()
        server.sendmail(fraepost, tilepost.split(","), text)
    except smtplib.SMTPException:
        print 'Email could not be sent' + '\n'
        server.close()
        getpass.getpass('Press ENTER to continue...')
        sys.exit(1)

    print 'Email sent succesfully' + '\n'
    server.quit()
    sys.exit(1)

main()
print ("Slutt rapport skript")
