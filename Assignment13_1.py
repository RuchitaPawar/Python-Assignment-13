import hashlib
import os
import smtplib
import sys
import time
import shutil
import urllib.request as urllib2
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule


def DeleteFile(dict1):
    DeletedFiles = "DeletedFilesLog_%s.log" % (time.time())
    results = list(filter(lambda x:len(x) > 1,dict1.values()))
    icnt =0
    f = open(DeletedFiles, "a")
    if len(results) > 0 :
        for result in results :
            for subresult in result :
                icnt +=1
                if icnt >=2:
                    print("Deleted file name:",subresult)
                    f.write(subresult)
                    f.close()
                    os.remove(subresult)
            icnt =0
        CreateDir(DeletedFiles)
    else:
        print("No duplicate files found")
   # periodically send the mail
    connected = isConnected()

    if connected:
        startTime = time.time()
        MailSender(DeletedFiles, sys.argv[2])
        endTime = time.time()

        print("Took %s seconds to evaluate." % (endTime - startTime))
    else:
        print("There is no internet connection")

    # creating directory for maintaining log file which contains information of deleted files
def CreateDir(DeletedFiles) :
    DirName = "Marvellous";

    absDirName = (os.path.join(sys.argv[1],DirName));
    try:
        if not (os.path.isdir(absDirName)):
            os.mkdir(os.path.join(sys.argv[1],DirName))
            shutil.copy(DeletedFiles,absDirName)
        else:
             shutil.copy(DeletedFiles, absDirName)
    except OSError:
        print("Creation of the directory %s failed" % os.path.join(sys.argv[1],DirName))
    else:
        print("Successfully created the directory %s "%os.path.join(sys.argv[1],DirName))

def hashfile(path,blocksize = 1024):
    afile = open(path,'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


def findDup(path):
    flag = os.path.isabs(path)
    if flag == False:
        path = os.path.abspath(path)

    exists = os.path.isdir(path)
    dups = {}
    if exists:
        for dirName, subDirs, fileList in os.walk(path):
           # print("Current folder is:", dirName)
            for fileName in fileList:
                path = os.path.join(dirName, fileName)
                file_hash = hashfile(path)

                if file_hash in dups:
                    dups[file_hash].append(path)
                else:
                    dups[file_hash] = [path]

            return dups;
    else:
        print("Invalid path")

# periodic mail scheduler
def isConnected():
    try:
        urllib2.urlopen('http://216.58.192.142', timeout=1)
        return True
    except urllib2.URLError as err:
        return False


def MailSender(filename, time):
    try:
        fromaddr = "ruchita1796@gmail.com"
        toaddr = "ruchitaspawar01@gmail.com"

        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr

        body = """  
          Hello %s,
            Please find the attached doucuments which contains Log of deleted filles.

            This is an auto generated mail

         Thanks & Regards,
            Ruchita Pawar
            """ % (toaddr)

        Subject = """
         Process Log generated at
         %s
        """ % (time)

        msg['Subject'] = Subject
        msg.attach(MIMEText(body, 'plain'))

        attachment = open(filename, "rb")

        p = MIMEBase('application', 'octet-stream')

        p.set_payload((attachment).read())

        encoders.encode_base64(p)

        p.add_header('Content Desposition', "attachment;filename =%s" % filename)

        msg.attach(p)

        s = smtplib.SMTP('smtp.gmail.com', 587)

        s.starttls()

        s.login(fromaddr, "---- password here ---")

        text = msg.as_string()

        s.sendmail(fromaddr, toaddr, text)

        s.quit()

        print("Log file successfully sentthrough mail")

    except Exception as E:
        print("Unable to send mail", E)


def main():

  # accept directory name from user and delete duplictae files from it.
    try:
        arr = {}
        arr = findDup(sys.argv[1])

        DeleteFile(arr)
        while True:
            schedule.run_pending()
            time.sleep(1)

    except ValueError:
        print("Error invalid datatype of input")

    except Exception:
        print("Error : Invalid input")


if __name__ == "__main__":
    main();
