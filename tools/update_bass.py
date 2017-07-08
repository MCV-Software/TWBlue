import urllib.request
import shutil
import zipfile
import os
def get_lib_url(lib):
    "Returns the standard URL for a library."
    finname="{}.zip".format(lib)
    return "http://us.un4seen.com/files/{}".format(finname)

def get_library(lib,url=None):
    "Download and extract a Bass library archive into a temporary directory."
    if not url:
        url=get_lib_url(lib)
    finname="{}.zip".format(lib)
    with urllib.request.urlopen(url) as fin, open(finname, "wb") as cam:
        shutil.copyfileobj(fin, cam)
    with zipfile.ZipFile("{}".format(finname),"r") as zipfin:
        zipfin.extractall("temp")
    os.remove(finname)

def prepare_libs():
    "Prepare library directory structure."
    #Move x64 directory out of temp.
    shutil.move(os.path.join("temp","x64"),os.path.join(os.getcwd(),"x64"))
    #Remove mp3-free directory
    shutil.rmtree("x64/mp3-free",ignore_errors=True)
    #Create x86 directory.
    if not os.path.exists("x86"):
        os.makedirs("x86")
    for file in os.listdir(os.fsencode("temp")):
        if b".dll" in file:
            shutil.move(os.path.join(b"temp",file),os.path.join(b"x86",file))
    # Cleanup
    shutil.rmtree("temp")
if __name__ == '__main__':
    libs=['bass', 'bassflac', 'bassmidi', 'bassmix', 'bassopus24', 'basswasapi', 'basswma', 'bassalac24']
    #Download the libraries
    for lib in libs:
        print("Fetching {}...".format(lib))
        get_library(lib)
    print("Finalizing...")
    prepare_libs()