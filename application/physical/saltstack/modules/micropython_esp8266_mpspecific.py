# -*- coding: utf-8 -*-
'''
Provide the module for the MicroPython-specific libraries of a proxy-minion.
'''

from __future__ import absolute_import

# Import python libs
import logging
import salt.utils

log = logging.getLogger(__name__)

__proxyenabled__ = ['micropython_esp8266']
__virtualname__ = 'micropython_esp8266_mpspecific'


def __virtual__():
    '''
    Only work on systems that are a proxy minion
    '''
    log.debug('micropython_esp8266_mpspecific proxy __virtual__() called...')
    try:
        if salt.utils.is_proxy() and __opts__['proxy']['proxytype'] == 'micropython_esp8266':
            return __virtualname__
    except KeyError:
        return (False, 'The micropython_esp8266_mpspecific execution module failed to load.  Check the proxy key in pillar.')

    return (False, 'The micropython_esp8266_mpspecific execution module failed to load: only works on a micropython_esp8266 proxy minion.')
#

def copy_file(src=None, dst=None):
    return True

#
def check_firmware():
    ret = __proxy__['micropython_esp8266.check_firmware']()
    ret2 = ret.split('\x1F')
    import json
    return json.loads(ret2[1])

#
def test():
    ret = __proxy__['micropython_esp8266.test']()
    ret2 = ret.split('\x1F')
    import json
    return json.loads(ret2[1])

# candidates for grains
#sys.implementation
#sys.path
#sys.platform
#sys.version
#sys.version_info
#machine.freq()
#machine.unique_id()
#esp.flash_id()
#wlan.isconnected()
#network.phy_mode() #MODE_11B|MODE_11G|MODE_11N
#self.sysname = self.eval("os.uname()[0]").decode('utf-8') #from mpfexp.py

# slightly volatile candidates
#wlan.ifconfig() # When called with no arguments, this method returns a 4-tuple [(ip, subnet, gateway, dns)]
#wlan.active([is_active]) # up|down
#wlan.status() #STAT_IDLE|STAT_CONNECTING|STAT_WRONG_PASSWORD|STAT_NO_AP_FOUND|STAT_CONNECT_FAIL|STAT_GOT_IP


#wlan.connect(ssid, password)
#wlan.disconnect()
#wlan.scan()
#wlan.config('param')
#wlan.config(param=value, ...)
#rtc.now()
#wdt.feed()
#micropython.alloc_emergency_exception_buf(size)
#pyb.millis()
#pyb.micros()
#pyb.hard_reset()
#pyb.sync()
#pyb.main(filename)
#i2c.scan()
#rtc.datetime([datetimetuple])
#esp.sleep_type([sleep_type])
#esp.flash_read(byte_offset, length_or_buffer)
#esp.flash_write(byte_offset, bytes)
#esp.flash_erase(sector_no)
