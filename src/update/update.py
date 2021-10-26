from logging import getLogger
logger = getLogger('update')

import contextlib
import io
import os
import platform
import requests
import tempfile
from wxUI import commonMessageDialogs
import widgetUtils
import webbrowser
try:
    import czipfile as zipfile
except ImportError:
    import zipfile

from platform_utils import paths

def perform_update(endpoint, current_version, app_name='', password=None, update_available_callback=None, progress_callback=None, update_complete_callback=None):
    requests_session = create_requests_session(app_name=app_name, version=current_version)
    available_update = find_update(endpoint, requests_session=requests_session)
    if not available_update:
        logger.debug("No update available")
        return False
    available_version = available_update['current_version']
    if available_version == current_version or platform.system()+platform.architecture()[0][:2] not in available_update['downloads']:
        logger.debug("No update for this architecture")
        return False
    available_description = available_update.get('description', None)
    available_date = available_update.get('date', None)
    update_url = available_update ['downloads'][platform.system()+platform.architecture()[0][:2]]
    logger.info("A new update is available. Version %s" % available_version)
    donation()
    if callable(update_available_callback) and not update_available_callback(version=available_version, description=available_description, date=available_date): #update_available_callback should return a falsy value to stop the process
        logger.info("User canceled update.")
        return
    base_path = tempfile.mkdtemp()
    download_path = os.path.join(base_path, 'update.zip')
    update_path = os.path.join(base_path, 'update')
    downloaded = download_update(update_url, download_path, requests_session=requests_session, progress_callback=progress_callback)
    extracted = extract_update(downloaded, update_path, password=password)
    bootstrap_path = move_bootstrap(extracted)
    execute_bootstrap(bootstrap_path, extracted)
    logger.info("Update prepared for installation.")
    if callable(update_complete_callback):
        update_complete_callback()

def create_requests_session(app_name=None, version=None):
    user_agent = ''
    session = requests.session()
    if app_name:
        user_agent = ' %s/%r' % (app_name, version)
    session.headers['User-Agent'] = session.headers['User-Agent'] + user_agent
    return session

def find_update(endpoint, requests_session):
    response = requests_session.get(endpoint)
    response.raise_for_status()
    content = response.json()
    return content

def download_update(update_url, update_destination, requests_session, progress_callback=None, chunk_size=io.DEFAULT_BUFFER_SIZE):
    total_downloaded = total_size = 0
    with io.open(update_destination, 'w+b') as outfile:
        download = requests_session.get(update_url, stream=True)
        total_size = int(download.headers.get('content-length', 0))
        logger.debug("Total update size: %d" % total_size)
        download.raise_for_status()
        for chunk in download.iter_content(chunk_size):
            outfile.write(chunk)
            total_downloaded += len(chunk)
            if callable(progress_callback):
                call_callback(progress_callback, total_downloaded, total_size)
    logger.debug("Update downloaded")
    return update_destination

def extract_update(update_archive, destination, password=None):
    """Given an update archive, extracts it. Returns the directory to which it has been extracted"""
    with contextlib.closing(zipfile.ZipFile(update_archive)) as archive:
        if password:
            archive.setpassword(password)
        archive.extractall(path=destination)
    logger.debug("Update extracted")
    return destination

def move_bootstrap(extracted_path):
    working_path = os.path.abspath(os.path.join(extracted_path, '..'))
    if platform.system() == 'Darwin':
        extracted_path = os.path.join(extracted_path, 'Contents', 'Resources')
    downloaded_bootstrap = os.path.join(extracted_path, bootstrap_name())
    new_bootstrap_path = os.path.join(working_path, bootstrap_name())
    os.rename(downloaded_bootstrap, new_bootstrap_path)
    return new_bootstrap_path

def execute_bootstrap(bootstrap_path, source_path):
    arguments = r'"%s" "%s" "%s" "%s"' % (os.getpid(), source_path, paths.app_path(), paths.get_executable())
    if platform.system() == 'Windows':
        import win32api
        win32api.ShellExecute(0, 'open', bootstrap_path, arguments, '', 5)
    else:  
        import subprocess
        make_executable(bootstrap_path)
        subprocess.Popen(['%s %s' % (bootstrap_path, arguments)], shell=True)
    logger.info("Bootstrap executed")

def bootstrap_name():
    if platform.system() == 'Windows': return 'bootstrap.exe'
    if platform.system() == 'Darwin': return 'bootstrap-mac.sh'
    return 'bootstrap-lin.sh'

def make_executable(path):
    import stat
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)

def call_callback(callback, *args, **kwargs):
    # try:
    callback(*args, **kwargs)
# except:
#  logger.exception("Failed calling callback %r with args %r and kwargs %r" % (callback, args, kwargs))

def donation():
    dlg = commonMessageDialogs.donation()
    if dlg == widgetUtils.YES:
        webbrowser.open_new_tab("http://twblue.es/?q=donate")
