# -*- coding: utf-8 -*-
import os
import time
import re
from Tools.HardwareInfo import HardwareInfo
from Components.SystemInfo import SystemInfo
from sys import maxsize, modules, version_info
from Tools.Directories import fileReadLine
from subprocess import PIPE, Popen

MODULE_NAME = __name__.split(".")[-1]


def getVersionString():
	return getImageVersionString()


def getImageVersionString():
	try:
		if os.path.isfile('/var/lib/opkg/status'):
			st = os.stat('/var/lib/opkg/status')
		tm = time.localtime(st.st_mtime)
		if tm.tm_year >= 2011:
			return time.strftime("%Y-%m-%d %H:%M:%S", tm)
	except:
		pass
	return _("unavailable")

# WW -placeholder for BC purposes, commented out for the moment in the Screen


def getFlashDateString():
	return _("unknown")


def getBuildDateString():
	try:
		if os.path.isfile('/etc/version'):
			version = open("/etc/version", "r").read()
			return "%s-%s-%s" % (version[:4], version[4:6], version[6:8])
	except:
		pass
	return _("unknown")


def getUpdateDateString():
	try:
		from glob import glob
		build = [x.split("-")[-2:-1][0][-8:] for x in open(glob("/var/lib/opkg/info/openpli-bootlogo.control")[0], "r") if x.startswith("Version:")][0]
		if build.isdigit():
			return "%s-%s-%s" % (build[:4], build[4:6], build[6:])
	except:
		pass
	return _("unknown")


def getEnigmaVersionString():
	import enigma
	enigma_version = enigma.getEnigmaVersionString()
	if '-(no branch)' in enigma_version:
		enigma_version = enigma_version[:-12]
	return enigma_version


def getGStreamerVersionString():
	try:
		from glob import glob
		gst = [x.split("Version: ") for x in open(glob("/var/lib/opkg/info/gstreamer[0-9].[0-9].control")[0], "r") if x.startswith("Version:")][0]
		return "%s" % gst[1].split("+")[0].replace("\n", "")
	except:
		return _("Not Installed")


def getffmpegVersionString():
	try:
		from glob import glob
		ffmpeg = [x.split("Version: ") for x in open(glob("/var/lib/opkg/info/ffmpeg.control")[0], "r") if x.startswith("Version:")][0]
		return "%s" % ffmpeg[1].split("+")[0].replace("\n", "")
	except:
		return _("Not Installed")


def getKernelVersionString():
	try:
		return open("/proc/version", "r").read().split(' ', 4)[2].split('-', 2)[0]
	except:
		return _("unknown")


def getHardwareTypeString():
	return HardwareInfo().get_device_string()


def getImageTypeString():
	try:
		image_type = open("/etc/issue").readlines()[-2].strip()[:-6]
		return image_type.capitalize().replace("develop", "Nightly Build")
	except:
		return _("undefined")


def getCPUInfoString():
	try:
		cpu_count = 0
		cpu_speed = 0
		processor = ""
		for line in open("/proc/cpuinfo").readlines():
			line = [x.strip() for x in line.strip().split(":")]
			if not processor and line[0] in ("system type", "model name", "Processor"):
				processor = line[1].split()[0]
			elif not cpu_speed and line[0] == "cpu MHz":
				cpu_speed = "%1.0f" % float(line[1])
			elif line[0] == "processor":
				cpu_count += 1

		if processor.startswith("ARM") and os.path.isfile("/proc/stb/info/chipset"):
			processor = "%s (%s)" % (open("/proc/stb/info/chipset").readline().strip().upper(), processor)

		if not cpu_speed:
			try:
				cpu_speed = int(open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq").read()) / 1000
			except:
				try:
					import binascii
					cpu_speed = int(int(binascii.hexlify(open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb').read()), 16) / 100000000) * 100
				except:
					cpu_speed = "-"

		temperature = None
		freq = _("MHz")
		if os.path.isfile('/proc/stb/fp/temp_sensor_avs'):
			temperature = open("/proc/stb/fp/temp_sensor_avs").readline().replace('\n', '')
		elif os.path.isfile('/proc/stb/power/avs'):
			temperature = open("/proc/stb/power/avs").readline().replace('\n', '')
		elif os.path.isfile('/proc/stb/fp/temp_sensor'):
			temperature = open("/proc/stb/fp/temp_sensor").readline().replace('\n', '')
		elif os.path.isfile("/sys/devices/virtual/thermal/thermal_zone0/temp"):
			try:
				temperature = int(open("/sys/devices/virtual/thermal/thermal_zone0/temp").read().strip()) / 1000
			except:
				pass
		elif os.path.isfile("/proc/hisi/msp/pm_cpu"):
			try:
				temperature = re.search('temperature = (\d+) degree', open("/proc/hisi/msp/pm_cpu").read()).group(1)
			except:
				pass
		if temperature:
			return "%s %s %s (%s) %s\xb0C" % (processor, cpu_speed, freq, ngettext("%d core", "%d cores", cpu_count) % cpu_count, temperature)
		return "%s %s %s (%s)" % (processor, cpu_speed, freq, ngettext("%d core", "%d cores", cpu_count) % cpu_count)
	except:
		return _("undefined")


def getChipSetString():
	if HardwareInfo().get_device_name() in ('dm7080', 'dm820'):
		return "7435"
	elif HardwareInfo().get_device_name() in ('dm520', 'dm525'):
		return "73625"
	elif HardwareInfo().get_device_name() in ('dm900', 'dm920', 'et13000', 'sf5008'):
		return "7252S"
	elif HardwareInfo().get_device_name() in ('hd51', 'vs1500', 'h7'):
		return "7251S"
	elif HardwareInfo().get_device_name() in ('alien5',):
		return "S905D"
	else:
		chipset = fileReadLine("/proc/stb/info/chipset", source=MODULE_NAME)
		if chipset is None:
			return _("Undefined")
		return str(chipset.lower().replace('\n', '').replace('bcm', '').replace('brcm', '').replace('sti', ''))

def getDVBAPI():
	if SystemInfo["OLDE2API"]:
		return _("Old") 
	else:
		return _("New")


def getDriverInstalledDate():
	try:
		from glob import glob
		try:
			if HardwareInfo().get_device_name() =="dm8000":
				driver = [x.split("-")[-2:-1][0][-9:] for x in open(glob("/var/lib/opkg/info/*-dvb-modules-*.control")[0], "r") if x.startswith("Version:")][0]
			else:
				driver = [x.split("-")[-2:-1][0][-8:] for x in open(glob("/var/lib/opkg/info/*-dvb-modules-*.control")[0], "r") if x.startswith("Version:")][0]
			return "%s-%s-%s" % (driver[:4], driver[4:6], driver[6:])
		except:
			try:
				driver = [x.split("Version:") for x in open(glob("/var/lib/opkg/info/*-dvb-proxy-*.control")[0], "r") if x.startswith("Version:")][0]
				return "%s" % driver[1].replace("\n", "")
			except:
				driver = [x.split("Version:") for x in open(glob("/var/lib/opkg/info/*-platform-util-*.control")[0], "r") if x.startswith("Version:")][0]
				return "%s" % driver[1].replace("\n", "")
	except:
		return _("unknown")


def getPythonVersionString():
	return "%s.%s.%s" % (version_info.major, version_info.minor, version_info.micro)


def GetIPsFromNetworkInterfaces():
	import socket
	import fcntl
	import struct
	import array
	is_64bits = maxsize > 2**32
	struct_size = 40 if is_64bits else 32
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	max_possible = 8 # initial value
	while True:
		_bytes = max_possible * struct_size
		names = array.array('B')
		for i in range(0, _bytes):
			names.append(0)
		outbytes = struct.unpack('iL', fcntl.ioctl(
			s.fileno(),
			0x8912,  # SIOCGIFCONF
			struct.pack('iL', _bytes, names.buffer_info()[0])
		))[0]
		if outbytes == _bytes:
			max_possible *= 2
		else:
			break
	namestr = names.tobytes()
	ifaces = []
	for i in range(0, outbytes, struct_size):
		iface_name = bytes.decode(namestr[i:i + 16]).split('\0', 1)[0]
		if iface_name != 'lo':
			iface_addr = socket.inet_ntoa(namestr[i + 20:i + 24])
			ifaces.append((iface_name, iface_addr))
	return ifaces


def getBoxUptime():
	try:
		time = ''
		f = open("/proc/uptime", "r")
		secs = int(f.readline().split('.')[0])
		f.close()
		if secs > 86400:
			days = secs / 86400
			secs = secs % 86400
			time = ngettext("%d day", "%d days", days) % days + " "
		h = secs / 3600
		m = (secs % 3600) / 60
		time += ngettext("%d hour", "%d hours", h) % h + " "
		time += ngettext("%d minute", "%d minutes", m) % m
		return "%s" % time
	except:
		return '-'


def getOpenSSLVersion():
	process = Popen(("/usr/bin/openssl", "version"), stdout=PIPE, stderr=PIPE, universal_newlines=True)
	stdout, stderr = process.communicate()
	if process.returncode == 0:
		data = stdout.strip().split()
		if len(data) > 1 and data[0] == "OpenSSL":
			return data[1]
	print("[About] Get OpenSSL version failed.")
	return _("Unknown")


# For modules that do "from About import about"
about = modules[__name__]
