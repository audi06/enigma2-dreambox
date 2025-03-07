#ifndef __LCDFB_H
#define __LCDFB_H

#include <lib/base/eerror.h>
#include <linux/fb.h>
#include <lib/gdi/lcd.h>
#include "gpixmap.h"

#ifndef LCD_DEV
# define LCD_DEV "/dev/fb1"
#endif

class eFbLCD: public eLCD
{
	int m_xRes, m_yRes, m_bpp;
	int m_brightness, m_gamma, m_alpha;
	int m_available;
	struct fb_var_screeninfo m_screeninfo;
	fb_cmap m_cmap;
	unsigned char m_ramp[256], m_rampalpha[256]; // RGB ramp 0..255
	uint16_t m_red[256], m_green[256], m_blue[256], m_trans[256];
	int m_phys_mem;
	int m_manual_blit;

	void calcRamp();
	int setMode(int xRes, int yRes, int bpp);
	void getMode();
	void enableManualBlit();
	void disableManualBlit();
			// low level gfx stuff
	int putCMAP();
	void save2png(unsigned char* output, int xRes, int yRes);
	void save2bmp(unsigned char* output, int xRes, int yRes);
public:
	eFbLCD(const char *fb=LCD_DEV);
	~eFbLCD();
	bool detected() { return m_available; }
	eSize size() { return eSize(m_xRes, m_yRes); }
	void setPalette(gUnmanagedSurface);
	int waitVSync();
	int setLCDContrast(int contrast) { return 0; };
	int setLCDBrightness(int brightness);
	void setInverted( unsigned char ) {};
	void setFlipped(bool) {};
	bool isOled() const { return 0; };
	void update();  // blit
	int lock();
	void unlock();
	int islocked() { return locked; }
	void setDump(bool);
	void dumpLCD(bool);
};

#endif
