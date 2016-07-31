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
    try:
        DETAILS['pyboard'] = mp.mpfexp.MpFileExplorer('ser:/dev/ttyUSB0') #devicefile
        DETAILS['connected'] = True
        DETAILS['pyboard'].enter_raw_repl()
    except:
        DETAILS['connected'] = False
    #todo wrap
    #if successful
    # do whatever
    #else return false
    #
    DETAILS['initialized'] = True

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
    return DETAILS['connected']
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
    execstring = (
        "import esp, os, sys, machine, network, ubinascii, json\r\n"
        "\r\n"
        "ret = {{}}\r\n"
        "\r\n"
        "ret['fw'] = sys.implementation.name + '_' + sys.platform\r\n"
        "ret['fw_family'] = sys.implementation.name\r\n"
        "ret['fw_platform'] = sys.platform\r\n"
        "ret['fwmajorrelease'] = sys.implementation.version[0]\r\n"
        "ret['fwrelease'] = '.'.join(map(str, sys.implementation.version))\r\n"
        "ret['fwrelease_info'] = sys.implementation.version\r\n"
        "\r\n"
        "if network.WLAN(network.STA_IF).active() or network.WLAN(network.AP_IF).active():\r\n"
        "    ret['ip4_interfaces'] = {{}}\r\n"
        "    ret['ipv4'] = {{}}\r\n"
        "\r\n"
        "if network.WLAN(network.STA_IF).active() and network.WLAN(network.STA_IF).ifconfig()[0] is not '0.0.0.0':\r\n"
        "    ret['ip4_interfaces']['sta'] = network.WLAN(network.STA_IF).ifconfig()[0]\r\n"
        "    ret['ipv4']['sta'] = network.WLAN(network.STA_IF).ifconfig()[0]\r\n"
        "\r\n"
        "if network.WLAN(network.AP_IF).active() and network.WLAN(network.AP_IF).ifconfig()[0] is not '0.0.0.0':\r\n"
        "    ret['ip4_interfaces']['ap'] = network.WLAN(network.AP_IF).ifconfig()[0]\r\n"
        "    ret['ipv4']['ap'] = network.WLAN(network.AP_IF).ifconfig()[0]\r\n"
        "\r\n"
        "ret['machine_id'] = ubinascii.hexlify(machine.unique_id()).decode('utf-8')\r\n"
        "ret['mem_total'] = esp.flash_size()\r\n"
        "ret['flash_id'] = esp.flash_id()\r\n"
        "ret['freq'] = machine.freq()\r\n"
        "\r\n"
        "has_hostname = False\r\n"
        "try:\r\n"
        "    with open('/etc/hostname', 'r') as f:\r\n"
        "        firstline = f.readline().strip()\r\n"
        "        has_hostname = True\r\n"
        "except:\r\n"
        "    pass\r\n"
        "\r\n"
        "try:\r\n"
        "    with open('/hostname', 'r') as f:\r\n"
        "        firstline = f.readline().strip()\r\n"
        "        has_hostname = True\r\n"
        "except:\r\n"
        "    pass\r\n"
        "\r\n"
        "if has_hostname:\r\n"
        "    ret['host'] = firstline\r\n"
        "    ret['nodename'] = firstline\r\n"
        "    ret['id'] = firstline\r\n"
        "    ret['fqdn'] = firstline\r\n"
        "\r\n"
        "ret['pythonversion'] = sys.version_info\r\n"
        "ret['serialnumber'] = ubinascii.hexlify(machine.unique_id()).decode('utf-8')\r\n"
        "ret['virtual'] = 'physical'\r\n"
        "ret['cpu_model'] = 'Xtensa lx106'\r\n"
        "\r\n"
        "ret['hwaddr_interfaces'] = {{}}\r\n"
        "addr = ubinascii.hexlify(network.WLAN(network.STA_IF).config('mac')).decode('utf-8')\r\n"
        "ret['hwaddr_interfaces']['sta'] = ':'.join(addr[i:i+2] for i in range(0,len(addr),2))\r\n"
        "addr = None\r\n"
        "\r\n"
        "addr = ubinascii.hexlify(network.WLAN(network.AP_IF).config('mac')).decode('utf-8')\r\n"
        "ret['hwaddr_interfaces']['ap'] = ':'.join(addr[i:i+2] for i in range(0,len(addr),2))\r\n"
        "\r\n"
        "print('{som}' + json.dumps(ret) + '{eom}')\r\n"
    ).format(som='\x1F', eom='\x1F')
    ret = DETAILS['pyboard'].exec_(execstring)
    ret2 = ret.split('\x1F')
    import json
    mydict = json.loads(ret2[1])
    GRAINS_CACHE.update(mydict)
    return GRAINS_CACHE
#

def check_firmware():
    execstring = ("import esp, ubinascii, ujson\r\n"
        "ret = {{}}\r\n"
        "ret['check_fw'] = esp.check_fw()\r\n"
        "print('{som}' + ujson.dumps(ret) + '{eom}')").format(x=x, som='\x1F', eom='\x1F')
    ret = DETAILS['pyboard'].exec_(execstring)
    return ret
#

def test():
    execstring = (
        "import esp, os, sys, machine, network, ubinascii, json\r\n"
        "\r\n"
        "ret = {{}}\r\n"
        "\r\n"
        "ret['fw'] = sys.implementation.name + '_' + sys.platform\r\n"
        "ret['fw_family'] = sys.implementation.name\r\n"
        "ret['fw_platform'] = sys.platform\r\n"
        "ret['fwmajorrelease'] = sys.implementation.version[0]\r\n"
        "ret['fwrelease'] = '.'.join(map(str, sys.implementation.version))\r\n"
        "ret['fwrelease_info'] = sys.implementation.version\r\n"
        "\r\n"
        "if network.WLAN(network.STA_IF).active() or network.WLAN(network.AP_IF).active():\r\n"
        "    ret['ip4_interfaces'] = {{}}\r\n"
        "    ret['ipv4'] = {{}}\r\n"
        "\r\n"
        "if network.WLAN(network.STA_IF).active() and network.WLAN(network.STA_IF).ifconfig()[0] is not '0.0.0.0':\r\n"
        "    ret['ip4_interfaces']['sta'] = network.WLAN(network.STA_IF).ifconfig()[0]\r\n"
        "    ret['ipv4']['sta'] = network.WLAN(network.STA_IF).ifconfig()[0]\r\n"
        "\r\n"
        "if network.WLAN(network.AP_IF).active() and network.WLAN(network.AP_IF).ifconfig()[0] is not '0.0.0.0':\r\n"
        "    ret['ip4_interfaces']['ap'] = network.WLAN(network.AP_IF).ifconfig()[0]\r\n"
        "    ret['ipv4']['ap'] = network.WLAN(network.AP_IF).ifconfig()[0]\r\n"
        "\r\n"
        "ret['machine_id'] = ubinascii.hexlify(machine.unique_id()).decode('utf-8')\r\n"
        "ret['mem_total'] = esp.flash_size()\r\n"
        "ret['flash_id'] = esp.flash_id()\r\n"
        "ret['freq'] = machine.freq()\r\n"
        "\r\n"
        "has_hostname = False\r\n"
        "try:\r\n"
        "    with open('/etc/hostname', 'r') as f:\r\n"
        "        firstline = f.readline().strip()\r\n"
        "        has_hostname = True\r\n"
        "except:\r\n"
        "    pass\r\n"
        "\r\n"
        "try:\r\n"
        "    with open('/hostname', 'r') as f:\r\n"
        "        firstline = f.readline().strip()\r\n"
        "        has_hostname = True\r\n"
        "except:\r\n"
        "    pass\r\n"
        "\r\n"
        "if has_hostname:\r\n"
        "    ret['host'] = firstline\r\n"
        "    ret['nodename'] = firstline\r\n"
        "    ret['id'] = firstline\r\n"
        "    ret['fqdn'] = firstline\r\n"
        "\r\n"
        "ret['pythonversion'] = sys.version_info\r\n"
        "ret['serialnumber'] = ubinascii.hexlify(machine.unique_id()).decode('utf-8')\r\n"
        "ret['virtual'] = 'physical'\r\n"
        "ret['cpu_model'] = 'Xtensa lx106'\r\n"
        "\r\n"
        "ret['hwaddr_interfaces'] = {{}}\r\n"
        "addr = ubinascii.hexlify(network.WLAN(network.STA_IF).config('mac')).decode('utf-8')\r\n"
        "ret['hwaddr_interfaces']['sta'] = ':'.join(addr[i:i+2] for i in range(0,len(addr),2))\r\n"
        "addr = None\r\n"
        "\r\n"
        "addr = ubinascii.hexlify(network.WLAN(network.AP_IF).config('mac')).decode('utf-8')\r\n"
        "ret['hwaddr_interfaces']['ap'] = ':'.join(addr[i:i+2] for i in range(0,len(addr),2))\r\n"
        "\r\n"
        "print('{som}' + json.dumps(ret) + '{eom}')\r\n"
    ).format(som='\x1F', eom='\x1F')
    ret = DETAILS['pyboard'].exec_(execstring)
    return ret

