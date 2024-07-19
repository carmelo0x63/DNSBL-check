# DNSBL-check
Python script to verify whether one or more IP addresses have been banned by one or more _blacklists_.<br/>
A Domain Name System blocklist, Domain Name System-based blackhole list, Domain Name System blacklist (DNSBL) or real-time blackhole list (RBL) is a service for operation of mail servers to perform a check via a Domain Name System (DNS) query whether a sending host's IP address is blacklisted for email spam. Most mail server software can be configured to check such lists, typically rejecting or flagging messages from such sites.<br/>
For a full history, see [Domain Name System blocklist](https://en.wikipedia.org/wiki/Domain_Name_System_blocklist) on Wikipedia. More information on [DNSBL.info](https://www.dnsbl.info/). An RFC also exists, [RFC5782](https://www.rfc-editor.org/rfc/rfc5782)<br/>

Initial code by: https://github.com/acidvegas/proxytools/. Some adjustments have been done.<br/>

### Requirements
- `aiodns`: simple way for doing asynchronous DNS resolutions using pycares
- `pycares`: interface to c-ares, C library performing DNS requests and name resolutions asynchronously

----

### Installation
```
git clone https://github.com/carmelo0x63/DNSBL-check.git
cd DNSBL-check
python3 -m venv .
source bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install --upgrade aiodns
./dnsbl.py
```

