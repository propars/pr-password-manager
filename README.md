
Propars Password Manager is a lite password manager application to keep track of all passwords and their usage periods.
- It generates random passwords in desired length.
- It alerts for the expired passwords via email.
- It prevents password re-use by archiving hash values of all passwords. Hash algorithm is SHA-256 and it uses django SECRET_KEY as salt.



__________________________

HOW TO RUN:

To be able to build and run the app via Makefile, just create a production_settings.py in prpassaman/prpassman directory and put 


**build:** `sudo make build`

**run:** `sudo make run`

(It runs in docker container, so it requires docker to run via make)

_________________________



WARNING: 
---
`SECRET_KEY` in repo is not safe. To run the app in production, please replace it with your own safe and secure `SECRET_KEY` in it (or use environment variables). 
