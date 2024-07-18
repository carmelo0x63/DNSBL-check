# DNSBL-check
Python script to verify whether one or more IP addresses have been blacklisted.

### Requirements
- aiodns: simple way for doing asynchronous DNS resolutions using pycares
- pycares: interface to c-ares, C library performing DNS requests and name resolutions asynchronously

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

