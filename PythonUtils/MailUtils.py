import smtplib


def sendEmail(fromAddr, toAddrList, ccAddrList, subject, message,
              login, password, smtpServer='smtp.gmail.com:587'):

    # Taken from http://rosettacode.org/wiki/Send_an_email#Python

    header = 'From: %s\n' % fromAddr
    header += 'To: %s\n' % ','.join(toAddrList)
    header += 'Cc: %s\n' % ','.join(ccAddrList)
    header += 'Subject: %s\n\n' % subject
    message = header + message

    server = smtplib.SMTP(smtpServer)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(fromAddr, toAddrList, message)
    server.quit()
    return problems
