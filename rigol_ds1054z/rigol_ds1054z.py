import pyvisa
import datetime
import time
import re
import csv
from math import floor, log10
import numpy as np
import datetime
import functools
from typing import Literal, List, Optional, Tuple

class Timer:
    def __init__(self):
        self._t = time.monotonic()
        
    @property
    def seconds(self):
        return time.monotonic() - self._t

    def __float__(self):
        return self.seconds


class rigol_ds1054z:
    MAX_READ = 250000
    # Constructor
    def __init__(self, resName=None, debug=False, verbose=False):
        resources = pyvisa.ResourceManager('@py')
        if resName is None:
            for resName in resources.list_resources():
                if resName.startswith(("TCPIP","USB")):
                    break
            else:
                raise RuntimeError("No instrument found on USB or LAN")
        # resources.list_resources() will show you the USB resource to pass in resName
        for i in range(1,4):
            try:
                self.inst = resources.open_resource(resName)
                break
            except Exception as e:
                time.sleep(2**i)
        else:
            raise e
        self.debug = debug
        self.verbose = verbose

    def wait(self, timeout=None) -> bool:
        """Waits for the device to indicate operation complete"""
        t = Timer()
        while timeout is None or t.seconds < timeout:
            try:
                result = self.inst.query_ascii_values('*OPC?', 'd')
            except:
                time.sleep(1)
                continue
            if result[0] == 1:
                return True
            time.sleep(0.5)
        return False
        

    def print_info(self):
        self.wait()
        self.inst.write('*IDN?')
        fullreading = self.inst.read_raw()
        readinglines = fullreading.splitlines()
        if self.verbose:
            print("Scope information: " + str(readinglines[0].decode()))
        # time.sleep(2)
    
    class measurement:
        def __init__(self, name='', description='', command='', unit='', return_type=''):
            self.name        = name
            self.description = description
            self.command     = command
            self.unit        = unit
            self.return_type = return_type
    #fmt: off
    max_voltage           = measurement(name='max_voltage',          command='VMAX', unit='Volts',         return_type='float', description='voltage value from the highest point of the waveform to the GND')
    min_voltage           = measurement(name='min_voltage',          command='VMIN', unit='Volts',         return_type='float', description='voltage value from the lowest point of the waveform to the GND')
    peak_to_peak_voltage  = measurement(name='peak_to_peak_voltage', command='VPP',  unit='Volts',         return_type='float', description='voltage value from the highest point to the lowest point of the waveform')
    top_voltage           = measurement(name='top_voltage',          command='VTOP', unit='Volts',         return_type='float', description='voltage value from the flat top of the waveform to the GND')
    base_voltage          = measurement(name='base_voltage',         command='VBAS', unit='Volts',         return_type='float', description='voltage value from the flat base of the waveform to the GND')
    top_to_base_voltage   = measurement(name='top_to_base_voltage',  command='VAMP', unit='Volts',         return_type='float', description='voltage value from the top of the waveform to the base of the waveform')
    average_voltage       = measurement(name='average_voltage',      command='VAVG', unit='Volts',         return_type='float', description='arithmetic average value on the whole waveform or on the gating area')
    rms_voltage           = measurement(name='rms_voltage',          command='VRMS', unit='Volts',         return_type='float', description='root mean square value on the whole waveform or the gating area')
    upper_voltage         = measurement(name='upper_voltage',        command='VUP',  unit='Volts',         return_type='float', description='actual voltage value corresponding to the threshold maximum value')
    mid_voltage           = measurement(name='mid_voltage',          command='VMID', unit='Volts',         return_type='float', description='actual voltage value corresponding to the threshold middle value')
    lower_voltage         = measurement(name='lower_voltage',        command='VLOW', unit='Volts',         return_type='float', description='actual voltage value corresponding to the threshold minimum value')
    overshoot_voltage     = measurement(name='overshoot_percent',    command='OVER', unit='%%',            return_type='float', description='ratio of the difference of the maximum value and top value of the waveform to the amplitude value')
    preshoot_voltage      = measurement(name='preshoot_percent',     command='PRES', unit='%%',            return_type='float', description='ratio of the difference of the minimum value and base value of the waveform to the amplitude value')
    variance_voltage      = measurement(name='variance_voltage',     command='VARI', unit='Volts',         return_type='float', description='average of the sum of the squares for the difference between the amplitude value of each waveform point and the waveform average value on the whole waveform or on the gating area')
    period_rms_voltage    = measurement(name='period_rms_voltage',   command='PVRMS',unit='Volts',         return_type='float', description='root mean square value within a period of the waveform')
    period_time           = measurement(name='period_time',          command='PER',  unit='Seconds',       return_type='float', description='time between the middle threshold points of two consecutive, like-polarity edges')
    frequency             = measurement(name='frequency',            command='FREQ', unit='Hz',            return_type='float', description='reciprocal of period')
    rise_time             = measurement(name='rise_time',            command='RTIM', unit='Seconds',       return_type='string',description='time for the signal amplitude to rise from the threshold lower limit to the threshold upper limit')
    fall_time             = measurement(name='fall_time',            command='FTIM', unit='Seconds',       return_type='string',description='time for the signal amplitude to fall from the threshold upper limit to the threshold lower limit')
    positive_width_time   = measurement(name='positive_width_time',  command='PWID', unit='Seconds',       return_type='float', description='time difference between the threshold middle value of a rising edge and the threshold middle value of the next falling edge of the pulse')
    negative_width_time   = measurement(name='negative_width_time',  command='NWID', unit='Seconds',       return_type='float', description='time difference between the threshold middle value of a falling edge and the threshold middle value of the next rising edge of the pulse')
    positive_duty_percent = measurement(name='positive_duty_ratio',  command='PDUT', unit='%%',            return_type='float', description='ratio of the positive pulse width to the period')
    negative_duty_percent = measurement(name='negative_duty_ratio',  command='NDUT', unit='%%',            return_type='float', description='ratio of the negative pulse width to the period')
    max_voltage_time      = measurement(name='max_voltage_time',     command='TVMAX',unit='Seconds',       return_type='float', description='time corresponding to the waveform maximum value')
    min_voltage_time      = measurement(name='min_voltage_time',     command='TVMIN',unit='Seconds',       return_type='float', description='time corresponding to the waveform minimum value')
    positive_pulse_number = measurement(name='positive_pulse_number',command='PPUL', unit='Occurances',    return_type='int',   description='number of positive pulses that rise from below the threshold lower limit to above the threshold upper limit')
    negative_pulse_number = measurement(name='negative_pulse_number',command='NPUL', unit='Occurances',    return_type='int',   description='number of negative pulses that fall from above the threshold upper limit to below the threshold lower limit')
    positive_edges_number = measurement(name='positive_edges_number',command='PEDG', unit='Occurances',    return_type='int',   description='number of rising edges that rise from below the threshold lower limit to above the threshold upper limit')
    negative_edges_number = measurement(name='negative_edges_number',command='NEDG', unit='Occurances',    return_type='int',   description='number of falling edges that fall from above the threshold upper limit to below the threshold lower limit')
    rising_delay_time     = measurement(name='rising_delay_time',    command='RDEL', unit='Seconds',       return_type='string',description='time difference between the falling edges of source 1 and source 2. Negative delay indicates that the selected falling edge of source 1 occurred after that of source 2')
    falling_delay_time    = measurement(name='falling_delay_time',   command='FDEL', unit='Seconds',       return_type='string',description='time difference between the falling edges of source 1 and source 2. Negative delay indicates that the selected falling edge of source 1 occurred after that of source 2')
    rising_phase_ratio    = measurement(name='rising_phase_ratio',   command='RPH',  unit='Degrees',       return_type='float', description='rising_delay_time / period_time x 360 degrees')
    falling_phase_ratio   = measurement(name='falling_phase_ratio',  command='FPH',  unit='Degrees',       return_type='float', description='falling_delay_time / period_time x 360 degrees')
    positive_slew_rate    = measurement(name='positive_slew_rate',   command='PSLEW',unit='Volts / Second',return_type='float', description='divide the difference of the upper value and lower value on the rising edge by the corresponding time')
    negative_slew_rate    = measurement(name='negative_slew_rate',   command='NSLEW',unit='Volts / Second',return_type='float', description='divide the difference of the lower value and upper value on the falling edge by the corresponding time')
    waveform_area         = measurement(name='waveform_area',        command='MAR',  unit='Volt Seconds',  return_type='float', description='algebraic sum of the area of the whole waveform within the screen. area of the waveform above the zero reference is positive and the area of the waveform below the zero reference is negative')
    first_period_area     = measurement(name='first_period_area',    command='MPAR', unit='Volt Seconds',  return_type='float', description='algebraic sum of the area of the first period of the waveform on the screen. area of the waveform above the zero reference is positive and the area of the waveform below the zero reference is negative')

    single_measurement_list = [max_voltage,         min_voltage,           peak_to_peak_voltage,  top_voltage,           base_voltage,          top_to_base_voltage,
                               average_voltage,     rms_voltage,           upper_voltage,         mid_voltage,           lower_voltage,         overshoot_voltage,
                               preshoot_voltage,    variance_voltage,      period_rms_voltage,    period_time,           frequency,             rise_time,
                               fall_time,           positive_width_time,   negative_width_time,   positive_duty_percent, negative_duty_percent, max_voltage_time,
                               min_voltage_time,    positive_pulse_number, negative_pulse_number, positive_edges_number, negative_edges_number, positive_slew_rate,
                               negative_slew_rate,  waveform_area,         first_period_area]

    double_measurement_list = [rising_phase_ratio, falling_phase_ratio, rising_delay_time, falling_delay_time]
	#fmt: on

    def powerise10(self, x):
        """ Returns x as a*10**b with 0 <= a < 10"""
        if x == 0: return 0,0
        Neg = x < 0
        if Neg: x = -x
        a = 1.0 * x / 10**(floor(log10(x)))
        b = int(floor(log10(x)))
        if Neg: a = -a
        return a,b
    
    def eng_notation(self, x):
        """Return a string representing x in an engineer friendly notation"""
        a,b = self.powerise10(x)
        if -3 < b < 3: return "%.4g" % x
        a = a * 10**(b % 3)
        b = b - b % 3
        return "%.4gE%s" % (a,b)

    def get_measurement(self, channel=1, meas_type=max_voltage):
        self.inst.write(':MEAS:ITEM? ' + meas_type.command + ',CHAN' + str(channel))
        fullreading = self.inst.read_raw()
        readinglines = fullreading.splitlines()
        if (meas_type.return_type == 'float'):
            reading = float(readinglines[0])
            if (meas_type.unit == '%%'):
                percentage_reading = reading*100
                print ("Channel " + str(channel) + " " + meas_type.name + " value is %0.2F " + meas_type.unit) % percentage_reading
            else:
                eng_reading = self.eng_notation(reading)
                print ("Channel " + str(channel) + " " + meas_type.name + " value is " + eng_reading + " " + meas_type.unit)
        elif (meas_type.return_type == 'int'):
            reading = int(float(readinglines[0]))
            print ("Channel " + str(channel) + " " + meas_type.name + " value is %d " + meas_type.unit) % reading
        else:
            reading = str(readinglines[0])
            print ("Channel " + str(channel) + " " + meas_type.name + " value is " + reading + " " + meas_type.unit)
        return reading
    
    # if no filename is provided, the timestamp will be the filename
    def write_screen_capture(self, filename=''):
        self.inst.write(':DISP:DATA? ON,OFF,PNG')
        raw_data = self.inst.read_raw()[11:] # strip off first 11 bytes
        # save image file
        if (filename == ''):
            filename = "rigol_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") +".png"
        fid = open(filename, 'wb')
        fid.write(raw_data)
        fid.close()
        print ("Wrote screen capture to filename " + '\"' + filename + '\"')
        time.sleep(5)
        
    def close(self):
        self.inst.close()
        print("Closed USB session to oscilloscope")
        
    def reset(self):
        self.wait()
        self.inst.write('*RST')
        time.sleep(5)
        self.wait()
        print("Reset oscilloscope")
    
    # probe should either be 10.0 or 1.0, per the setting on the physical probe
    def setup_channel(self, channel=1, on=True, offset_divs=0.0, volts_per_div=1.0, probe=10.0):
        if (on):
            #fmt: off
            self.inst.write(':CHAN' + str(channel) + ':DISP ' + 'ON')
            self.inst.write(':CHAN' + str(channel) + ':SCAL ' + str(volts_per_div))
            self.inst.write(':CHAN' + str(channel) + ':OFFS ' + str(offset_divs*volts_per_div))
            self.inst.write(':CHAN' + str(channel) + ':PROB ' + str(probe))
            print ("Turned on CH" + str(channel) + ", position is " + str(offset_divs) + " divisions from center, " + str(volts_per_div) + " volts/div, scope is " + str(probe) + "x")
            #fmt: on
        else:
            self.inst.write(':CHAN' + str(channel) + ':DISP OFF')
            print ("Turned off channel " + str(channel))
    
    def val_and_unit_to_real_val(self, val_with_unit='1s'):
        try:
            # Allow unitless strings and plain floats
            val = float(val_with_unit)
            return val
        except:
            pass
        number = float(re.search(r"([0-9\.]+)",val_with_unit).group(0))
        unit = re.search(r"([a-z]+)",val_with_unit.lower()).group(0).lower()
        if (unit == 's' or unit == 'v'):
            real_val_no_units = number
        elif (unit == 'ms' or unit == 'mv'):
            real_val_no_units = number * 0.001
        elif (unit == 'us' or unit == 'uv'):
            real_val_no_units = number * 0.000001
        elif (unit == 'ns' or unit == 'nv'):
            real_val_no_units = number * 0.000000001
        else:
            real_val_no_units = number
        return real_val_no_units

    def setup_timebase(self, time_per_div='1ms', delay='0ms') -> (float, float):
        time_per_div_real = self.val_and_unit_to_real_val(time_per_div)
        self.inst.write(':TIM:MAIN:SCAL ' + str(time_per_div_real))
        readback = self.get(':TIM:MAIN:SCAL?')
        print (f"Timebase was set to {readback} s per division")
        delay_real = self.val_and_unit_to_real_val(delay)
        self.inst.write(':TIM:MAIN:OFFS ' + str(delay_real))
        scale = self.inst.query_ascii_values(':TIM:MAIN:SCAL?')[0]
        offs = self.inst.query_ascii_values(':TIM:MAIN:OFFS?')[0]
        return scale, offs
    
    # remember to always use lowercase level units, the regex look for lowercase
    def setup_trigger(self, channel=1, slope_pos=1, level='100mv'):
        level_real = self.val_and_unit_to_real_val(level)
        self.inst.write(':TRIG:EDG:SOUR CHAN' + str(channel))
        if (slope_pos == 0):
            self.inst.write(':TRIG:EDG:SLOP NEG')
        else:
            self.inst.write(':TRIG:EDG:SLOP POS')
        self.inst.write(':TRIG:EDG:LEV ' + str(level_real))
        if (slope_pos == 1):
            print ("Triggering on CH" + str(channel) + " positive edge with level of " + level)
        else:
            print ("Triggering on CH" + str(channel) + " negative edge with level of " + level)
    
    # decode channel is either 1 or 2, only two decodes can be present at any time
    # use uppercase for encoding, valid choices are HEX, ASC, DEC, BIN, LINE
    # position_divs is the number of division (from bottom) to position the decode
    def setup_i2c_decode(self, decode_channel=1, on=1, sda_channel=1, scl_channel=2, encoding='HEX', position_divs=1.0):
        if (on == 0):
            self.inst.write(':DEC' + str(decode_channel) + ':CONF:LINE OFF')
        else:
            #fmt: off
            self.inst.write(':DEC' + str(decode_channel) + ':MODE IIC')
            self.inst.write(':DEC' + str(decode_channel) + ':DISP ON')
            self.inst.write(':DEC' + str(decode_channel) + ':FORM ' + encoding)
            self.inst.write(':DEC' + str(decode_channel) + ':POS ' + str(400-position_divs*50))
            self.inst.write(':DEC' + str(decode_channel) + ':THRE AUTO')
            self.inst.write(':DEC' + str(decode_channel) + ':CONF:LINE ON')
            self.inst.write(':DEC' + str(decode_channel) + ':IIC:CLK CHAN' + str(scl_channel))
            self.inst.write(':DEC' + str(decode_channel) + ':IIC:DATA CHAN' + str(sda_channel))
            self.inst.write(':DEC' + str(decode_channel) + ':IIC:ADDR RW')
            #fmt: on
    def sample_rate(self):
        return self.inst.query_ascii_values(":ACQ:SRAT?")[0]

    def status(self) -> Literal["TD", "WAIT", "RUN", "AUTO", "STOP"]:        
        """Status of scope

        Returns:
            str: _description_
        """
        return self.inst.query(":TRIG:STAT?").strip()


    def stop(self):
        self.wait()
        self.inst.write(':STOP')
        self.wait()


    def single_trigger(self):
        self.inst.write(':SING')
        return self.wait(3)

        # time.sleep(3)
        
    def force_trigger(self):
        self.inst.write(':TFOR')
        return self.wait(3)

        # time.sleep(3)
        
    def run_trigger(self):
        self.inst.write(':RUN')
        time.sleep(3)
        
    def autoscale(self):
        # DOESN"T DO ANYTHING
        self.wait(3)
        self.inst.write(':AUTO')
        return self.wait(3)
        # time.sleep(10)
        
    # For RIGOL 1054Z:
    # only allowed values are 12e3, 12e4, 12e5, 12e6, 24e6 for single channels
    # only allowed values are 6e3, 6e4, 6e5, 6e6, 12e6 for   dual channels
    # only allowed values are 3e3, 3e4, 3e5, 3e6, 6e6  for 3 or 4 channels
    # the int conversion is needed for scientific notation values
    def setup_mem_depth(self, memory_depth=12e6):
        """Set the scope to the requested depth
        
        If that fails, try a smaller number from a set chosen
        for the RIGOL series 1000 oscilloscopes
        
        Args:
            memory_depth (_type_, optional): _description_. Defaults to 12e6.

        Returns:
            _type_: _description_
        """
        if self.status() == 'STOP':
            raise RuntimeError("Can't set memory depth when stopped?")
        if str(memory_depth).upper() == 'AUTO':
            self.inst.write(':ACQ:MDEP AUTO')
            newdepth = self.inst.query(':ACQ:MDEP?').strip()
        else:
            rigol_depths = sorted(np.concatenate([digit  * 10**np.arange(3,7) for digit in (3,6,12)]))  + [24*10**6]
            reqdepth = int(memory_depth)
            ifallback = np.searchsorted(rigol_depths, reqdepth-1)
            for trydepth in [reqdepth] + rigol_depths[ifallback::-1]:
                self.inst.write(':ACQ:MDEP ' + str(int(trydepth)))
                newdepth = self.inst.query(':ACQ:MDEP?').strip()
                if newdepth == 'AUTO':
                    continue
                if int(newdepth) == trydepth:
                    break
            else:
                raise RuntimeError(f"Could not set depth to {memory_depth}")
        if self.verbose:
            print(f"Acquire memory depth set to {newdepth} samples ({memory_depth} requested)")
        return newdepth

    def get(self, datum:str):
        if "?" not in datum:
            datum = datum+"?"
        time.sleep(0.1)
        s = self.inst.query(datum).strip()
        time.sleep(0.1)
        for type_ in (float, int, str):
            try:
                return type_(s)
            except:
                pass
        else:
            raise RuntimeError(f"Trouble with {s}")
            

    def get_scales(self, istart=0, raw=True) -> Tuple[np.polynomial.Polynomial, np.polynomial.Polynomial]:
        """Conversions from oscilloscope to physical units

        Polynoimals to convert form raw mode 
        Rigol manual 2-221
        Args:
            istart (int, optional): Scope index . Defaults to 0.

        Returns:
            Tuple[np.polynomial.Polynomial, np.polynomial.Polynomial]: timepoly, voltpoly
        """
        if not raw:
            raise NotImplementedError("Only raw mode supported")

        scales = [self.get(f':WAV:{vname}?')
                  for vname in "XINCREMENT,XORIGIN,XREFERENCE,YINCREMENT,YORIGIN,YREFERENCE".split()]
        raise NotImplementedError("I don't yet have the conversion factors")


    def get_mem_depth(self):
        self.inst.write(':ACQ:MDEP?')
        fullreading = self.inst.read_raw()
        readinglines = fullreading.splitlines()
        if readinglines[0] == b'AUTO':
            mdepth = 6000
        else:
            mdepth = int(readinglines[0])
        return mdepth

    def read_raw_wave(self, channel=1, samprange=None, scale='uint8') -> np.ndarray:
        """Read the raw waveform

        Scale can be:
            'raw': uint8 in range 20-255 where 255 is lowest voltage
            'uint8': uint8 in range 0-235 where 0 is lowest voltage
            True: float scaled voltage
            
        samprange is indexed from 0
        
        Args:
            channel (int, optional): _description_. Defaults to 1.
            samprange ([ilow, ihigh], optional): range of samples. Defaults to all.
            scale (str, optional): _description_. Defaults to 'uint8'.
        Returns:
            NDArray: waveform, (index->time, value->voltage)
        Raises:
            NotImplementedError: _description_
        """        
        # Must be in stop state to read raw
        self.stop()
        self.inst.write(f':WAV:SOUR: CHAN{channel}')
        self.inst.write(':WAV:FORM BYTE')
        self.inst.write(':WAV:MODE MAX')
        
        self.wait()
        mdepth = self.get_mem_depth()
        if samprange is None:
            samprange = np.array([0,mdepth])
        else:
            samprange = np.asarray(samprange)
            if len(samprange) == 1:
                samprange = samprange * [0,1]
        segs = []
        for istart in range(samprange[0], samprange[1], self.MAX_READ):
            istop = min(mdepth, samprange[1], istart + self.MAX_READ)
            if istart >= istop:
                break
            # Oscilloscope indexes from 1 adn are inclusive
            self.inst.write(f':WAV:STAR {istart+1}')
            self.inst.write(f':WAV:STOP {istop}')
            seg = self.inst.query_binary_values(f':WAV:DATA?', 'B', container=np.array)
            if len(seg) == 0:
                break
            segs.append(seg)
        data = np.concatenate(segs)
        if scale == 'raw':
            pass
        elif scale == 'uint8':
            pass
            # data = 255 - data
        elif scale == True:
            raise NotImplementedError("Scaling not yet implmented")
        return data


    def write_waveform_data(self, channel=1, filename=''):
        self.inst.write(':WAV:SOUR: CHAN' + str(channel))
        time.sleep(1)
        self.inst.write(':WAV:MODE NORM')
        self.inst.write(':WAV:FORM ASC')
        mdepth = self.get_mem_depth()
        # This the read length is in characters, not data
        # num_reads = (mdepth // 15625) +1
        if (filename == ''):
            filename = "rigol_waveform_data_channel_" + str(channel) + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") +".csv"
        fid = open(filename, 'wt')
        print ("Started saving waveform data for channel " + str(channel) + " " + str(mdepth) + " samples to filename " + '\"' + filename + '\"')
        # for read_loop in range(0,num_reads):
        while True:
            self.inst.write(':WAV:DATA?')
            fullreading = self.inst.read_raw()
            try:
                readlen = int(fullreading[2:11])
                if readlen == 0:
                    break
            except:
                break
            values = [float(f.strip()) for f in fullreading[11:-1].decode().split(",")]
            readinglines = fullreading[11:-1].splitlines()
            reading = str(readinglines[0])
            reading = reading.replace(",", "\n")
            fid.write(reading)
        fid.close()

    def write_scope_settings_to_file(self, filename=''):
        self.inst.write(':SYST:SET?')
        raw_data = self.inst.read_raw()[11:] # strip off first 11 bytes
        
        if (filename == ''):
            filename = "rigol_settings_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") +".stp"
        fid = open(filename, 'wb')
        fid.write(raw_data)
        fid.close()
        print ("Wrote oscilloscope settings to filename " + '\"' + filename + '\"')
        time.sleep(5)
        
    def restore_scope_settings_from_file(self, filename=''):
        if (filename == ''):
            print ("ERROR: must specify filename\n")
        else:
            with open(filename, mode='rb') as file: # b is important -> binary
                fileContent = file.read()
                valList = list()
                #alter ending to append new CRLF
                fileContent = fileContent + chr(13) + chr(10)
                #convert to a list that write_binary_values can iterate
                for x in range(0,len(fileContent)-1):
                    valList.append(ord(fileContent[x]))
                self.inst.write_binary_values(':SYST:SET ', valList, datatype='B', is_big_endian=True) 
            print ("Wrote oscilloscope settings to scope")
            time.sleep(8)



"""
About reading waveform:
            # self.inst.write(f':WAV:DATA?')
            # fullreading = self.inst.read_raw()
            # The format of the TMC data description header is 
            # #NXXXXXXXXX; wherein, # is the denoter, N is 9 and 
            # the 9 data following it denote the number of bytes 
            # of the waveform data. 
            # There is also a '\n' appended
            # ndata = int(fullreading[2:11])
            # if ndata != len(fullreading) - 12:
            #     break   # Raise error?
            # segs.append(np.frombuffer(fullreading[11:-1], dtype=np.uint8))

"""