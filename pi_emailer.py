import sys
import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
import pickle

MY_EMAIL = 'ppf.lightmeter@gmail.com'
MY_PSWD = 'PPF_Raspberry'

ENABLE_SUBJECT = 'Enable Email Updates'
DISABLE_SUBJECT = 'Disable Email Updates'
LIST_FILE = '/home/pi/Documents/Raspberry-Pi-Email-System/email_list.p'

ENABLED = 'ENABLED'
DISABLED = 'DISABLED'

BASE_MSG = 'Hello,\n\n This is an automated email from the Purdue Physical Facilies Light Meter.\n\n	The Light Meter can be found at the following IP Address:\n\n'


class pi_emailer():
	def __init__(self, email, pswd):
		self.email = email
		self.pswd = pswd
		if(os.path.isfile(LIST_FILE)):
			self.email_list = pickle.load(open(LIST_FILE,'rb'))
		else:
			self.email_list = dict()
		print self.email_list

	def read_emails(self):
		mail = imaplib.IMAP4_SSL('imap.gmail.com')
		mail.login(self.email,self.pswd)
		mail.list()
		mail.select('inbox')
	
		(retcode, messages) = mail.search(None,'(UNSEEN)')
		if retcode == 'OK':
			for id in messages[0].split():
				typ, data = mail.fetch(id,'(RFC822)')
				for response_part in data:
					if isinstance(response_part,tuple):
						original = email.message_from_string(response_part[1])
						if original['Subject'] == ENABLE_SUBJECT:
							address = original['From'].split('<')[1].split('>')[0]
							self.email_list[address] = ENABLED
						elif original['Subject'] == DISABLE_SUBJECT:
							address = original['From'].split('<')[1].split('>')[0]
							self.email_list[address] = DISABLED


	def send_updates(self, ip_address):
		s = smtplib.SMTP(host='smtp.gmail.com', port=587)
		s.ehlo()
		s.starttls()
		s.login(self.email,self.pswd)
		for key in self.email_list.keys():
			if(self.email_list[key] == ENABLED):
				self.send_email(s, key, ip_address)
		s.quit()



	def send_email(self, server, to_addr, ip_address):
		msg = MIMEText(BASE_MSG + ip_address)
		msg['Subject'] = 'Purdue Physical Facilities Exterior Lighting Meter IP Address'
		msg['From'] = self.email
		msg['To'] = to_addr
		
		server.sendmail(self.email,to_addr,msg.as_string())

	def save_list(self):
		pickle.dump(self.email_list, open(LIST_FILE,'wb'))



if __name__=='__main__':
	ip = sys.argv[1]
	emailer = pi_emailer(MY_EMAIL, MY_PSWD)
	emailer.read_emails()
	emailer.send_updates(ip)
	emailer.save_list()
