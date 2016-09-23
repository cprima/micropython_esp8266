# -*- coding: utf-8 -*-
'''
This is a proxy minion that connects to a ESP8266 running micropython firmware.
'''
from __future__ import absolute_import

# Import python libs
import logging
import salt.utils.http

# Import 3rd-party libs
try:
    HAS_MPFSHELL = True
    # wraps pyboard with 
    import mp.mpfexp
except ImportError:
    HAS_MPFSHELL = False

__proxyenabled__ = ['micropython_esp8266']
__virtualname__ = 'micropython_esp8266'


GRAINS_CACHE = {}
DETAILS = {}


log = logging.getLogger(__file__)

#
def __virtual__():
#    '''
#    Only return if all the modules are available
#    '''
    if not HAS_MPFSHELL:
        return False, 'Missing dependency mpfshell https://github.com/wendlers/mpfshell'
    return __virtualname__

#def __virtual__():
#    '''
#    Only return if all the modules are available
#    '''
#    log.info('nxos proxy __virtual__() called...')
#
#    if __opts__.get('proxy_merge_grains_in_module', False) is False:
#        salt.utils.warn_until(
#            'Nitrogen',
#            'To use grains with the NXOS proxy minion, '
#            '`proxy_merge_grains_in_module: True` must be set in the '
#            'proxy minion config.'
#        )
#
#    return __virtualname__
#

def init(opts=None):
    '''
    Initialize the library and enter micropythons raw-REPL mode which takes bytes and doesn't echo back.
    '''
    #get option connection string
    DETAILS['conntype'] = opts['proxy'].get('conntype')
    # DETAILS['devicefile'] = opts['proxy'].get('devicefile')
    # DETAILS['port'] = opts['proxy'].get('port') #serial
    # DETAILS['baudrate'] = opts['proxy'].get('baudrate') #serial
    # DETAILS['ip'] = opts['proxy'].get('ip') #telnet, websocket
    # DETAILS['user'] = opts['proxy'].get('user') #telnet
    # DETAILS['password'] = opts['proxy'].get('password') #telnet, websocket
    #try to connect
    DETAILS['pyboard'] = mp.mpfexp.MpFileExplorer('ser:/dev/ttyUSB0') #devicefile
    DETAILS['pyboard'].enter_raw_repl()
    #if successful
    # do whatever
    #else return false
    #
    #DETAILS['initialized'] = True

#def init(opts=None):
#    '''
#    Required.
#    Can be used to initialize the server connection.
#    '''
#    if opts is None:
#        opts = __opts__
#    try:
#        DETAILS[_worker_name()] = SSHConnection(
#            host=opts['proxy']['host'],
#            username=opts['proxy']['username'],
#            password=opts['proxy']['password'],
#            key_accept=opts['proxy'].get('key_accept', False),
#            ssh_args=opts['proxy'].get('ssh_args', ''),
#            prompt='{0}.*#'.format(opts['proxy']['prompt_name']))
#        out, err = DETAILS[_worker_name()].sendline('terminal length 0')
#
#    except TerminalException as e:
#        log.error(e)
#        return False
#    DETAILS['initialized'] = True
#
#
def initialized():
    return True
#def initialized():
#    return DETAILS.get('initialized', False)
#
#
def ping():
    return True
#def ping():
#    '''
#    Required.
#    Ping the device on the other end of the connection
#    .. code-block: bash
#        salt '*' nxos.cmd ping
#    '''
#    if _worker_name() not in DETAILS:
#        init()
#    try:
#        return DETAILS[_worker_name()].conn.isalive()
#    except TerminalException as e:
#        log.error(e)
#        return False
#
#
def shutdown(opts):
    '''
    Required.
    Disconnect from the board.
    '''
    DETAILS['pyboard'].exit_raw_repl()
    return True
#def shutdown(opts):
#    '''
#    Required.
#    Disconnect
#    '''
#    pass
#    #DETAILS[_worker_name()].close_connection()





def grains():
    '''
    Get the grains from the proxy device.
    '''
    if not GRAINS_CACHE:
        return _grains() #maybe use connection settings here?
    return GRAINS_CACHE


def grains_refresh():
    '''
    Refresh the grains from the proxy device.
    '''
    GRAINS_CACHE = {}
    return grains()

#def _grains(host, protocol=None, port=None):
def _grains():
    '''
    Helper function to the grains from the proxied device.
    '''
    ret = {}
    ret['machine.freq'] = '79999'
    ret['machine.unique_id'] = '4711'
    ret['esp.flash_id'] = '0815'
    #todo write a ecex_-eable script to return a dictionary
    #ret['machine.freq'] = DETAILS['pyboard'].machine.freq()
    #ret['machine.unique_id'] = DETAILS['pyboard'].machine.unique_id()
    #ret['esp.flash_id'] = DETAILS['pyboard'].esp.flash_id()
    GRAINS_CACHE.update(ret)
    return GRAINS_CACHE
#

def check_firmware():
    ret = DETAILS['pyboard'].exec_(
        "import esp, ubinascii\r\n"
        "ret = {}\r\n"
        "ret['check_fw'] = esp.check_fw()\r\n"
        "print(ret)"
    )
    return ret
#
