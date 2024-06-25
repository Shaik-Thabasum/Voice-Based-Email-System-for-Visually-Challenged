import os
from playsound import playsound
import smtplib
import email
import imaplib
import speech_recognition as sr
from gtts import gTTS
from email.header import decode_header
# import webbrowser


# CONSTANTS

from CONSTANTS import EMAIL_ID, PASSWORD, LANGUAGE
# from CONSTANTS_dev import EMAIL_ID, PASSWORD, LANGUAGE


def SpeakText(command, langinp=LANGUAGE):
    """
    Text to Speech using GTTS
    Args:
        command (str): Text to speak
        langinp (str, optional): Output language. Defaults to "en".
    """
    if langinp == "": langinp = "en"
    tts = gTTS(text=command, lang=langinp)
    tts.save("~tempfile01.mp3")
    playsound("~tempfile01.mp3")
    print(command)
    os.remove("~tempfile01.mp3")


def speech_to_text():
    """
    Speech to text
    Returns:
        str: Returns transcripted text
    """
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source2:
            r.adjust_for_ambient_noise(source2, duration=0.2)
            audio2 = r.listen(source2)
            MyText = r.recognize_google(audio2)
            print("You said: "+MyText)
            return MyText

    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return None

    except sr.UnknownValueError:
        print("unknown error occured")
        return None


def sendMail(sendTo, msg):
    """
    To send a mail
    Args:
        sendTo (list): List of mail targets
        msg (str): Message
    """
    mail = smtplib.SMTP('smtp.gmail.com', 587)  # host and port
    # Hostname to send for this command defaults to the FQDN of the local host.
    mail.ehlo()
    mail.starttls()  # security connection
    mail.login(EMAIL_ID, PASSWORD)  # login part
    for person in sendTo:
        mail.sendmail(EMAIL_ID, person, msg)  # send part
        print("Mail sent successfully to " + person)
    mail.close()


def composeMail():
    """
    Compose and create a Mail
    Returns:
        None: None
    """
    SpeakText("Mention the gmail ID of the persons to whom you want to send a mail. Email IDs should be separated with the word, AND.")
    receivers = speech_to_text()
    receivers = receivers.replace("at the rate", "@")
    emails = receivers.split(" and ")
    index = 0
    for email in emails:
        emails[index] = email.replace(" ", "")
        index += 1

    SpeakText("The mail will be send to " +
              (' and '.join([str(elem) for elem in emails])) + ". Confirm by saying YES or NO.")
    confirmMailList = speech_to_text()

    if confirmMailList.lower() != "yes":
        SpeakText("Operation cancelled by the user")
        return None

    SpeakText("Say your message")
    msg = speech_to_text()

    SpeakText("You said  " + msg + ". Confirm by saying YES or NO.")
    confirmMailBody = speech_to_text()
    if confirmMailBody.lower() == "yes":
        SpeakText("Message sent")
        sendMail(emails, msg)
    else:
        SpeakText("Operation cancelled by the user")
        return None


def getMailBoxStatus():
    """
    Get mail counts of all folders in the mailbox
    """
    # host and port (ssl security)
    M = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    M.login(EMAIL_ID, PASSWORD)  # login

    for i in M.list()[1]:
        l = i.decode().split(' "/" ')
        if l[1] == '"[Gmail]"':
            continue

        stat, total = M.select(f'{l[1]}')
        l[1] = l[1][1:-1]
        messages = int(total[0])
        if l[1] == 'INBOX':
            SpeakText(l[1] + " has " + str(messages) + " messages.")
        else:
            SpeakText(l[1].split("/")[-1] + " has " + str(messages) + " messages.")

    M.close()
    M.logout()


def clean(text):
    """
    clean text for creating a folder
    """
    return "".join(c if c.isalnum() else "_" for c in text)


def getLatestMails():
    """
    Get latest mails from folders in mailbox (Defaults to 3 Inbox mails)
    """
    mailBoxTarget = "INBOX"
    SpeakText("C
