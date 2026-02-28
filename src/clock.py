#!/usr/bin/python3

import locale
import logging
import signal
import sys
import time
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont
from systemd import journal

sys.path.insert(0, "/usr/lib/pi-clock")
from waveshare import EPD_13in3k

logger = logging.getLogger(__name__)
logger.addHandler(journal.JournalHandler(SYSLOG_IDENTIFIER="pi-clock"))
logger.propagate = False

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_PATH_JP = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


class Renderer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.font_time = ImageFont.truetype(FONT_PATH, 300)
        self.font_date = ImageFont.truetype(FONT_PATH, 60)
        self.font_date_jp = ImageFont.truetype(FONT_PATH_JP, 55)

    def render(self, dt: datetime, is_grayscale: bool) -> Image:
        img = Image.new("L", (self.width, self.height), 0xFF)  # white, grayscale
        draw = ImageDraw.Draw(img)
        if not is_grayscale:
            draw.fontmode = "1"  # Disable anti-aliasing
        locale.setlocale(locale.LC_ALL, "C")
        time_str = dt.strftime("%-I:%M")
        date_str = dt.strftime("%A, %B %-d")
        locale.setlocale(locale.LC_ALL, "ja_JP.UTF-8")
        date_str_jp = dt.strftime("%-Y年%-m月%-d日 (%A)")
        locale.setlocale(locale.LC_ALL, "C")
        cx = self.width // 2
        cy = self.height // 2

        # Center time in upper portion of display
        draw.text((cx, cy - 80), time_str, font=self.font_time, fill=0, anchor="mm")
        # Center English date
        draw.text((cx, cy + 120), date_str, font=self.font_date, fill=0, anchor="mm")
        # Center Japanese date below English date
        draw.text(
            (cx, cy + 195), date_str_jp, font=self.font_date_jp, fill=0, anchor="mm"
        )
        return img


class ShutdownRequested(Exception):
    pass


def main():
    logging.basicConfig(level=logging.INFO)

    try:
        logger.info("Initializing e-paper")

        def handle_sigterm(*_):
            logger.info("Received SIGTERM; shutting down")
            raise ShutdownRequested

        signal.signal(signal.SIGTERM, handle_sigterm)

        epd = EPD_13in3k.EPD()
        renderer = Renderer(epd.width, epd.height)

        logger.info("Entering timekeeping loop")
        while True:
            # Power up the hardware and update the display
            epd.init_4GRAY()
            now = datetime.now()
            img = renderer.render(now, is_grayscale=True)
            buf = epd.getbuffer_4Gray(img)
            epd.display_4Gray(buf)

            # Sleep until the next minute boundary--according to the
            # manual, the e-paper can be damaged by leaving it in a
            # high-voltage state for too long
            epd.send_command(0x10)  # DEEP_SLEEP
            epd.send_data(0x03)  # ... enabled
            nxt = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
            time.sleep((nxt - now).total_seconds())

    except ShutdownRequested:
        pass

    # For storage, the manual recommends clearing the display.
    epd.init()
    epd.Clear()
    epd.sleep()
    logger.info("E-paper is cleared; shutdown complete")


if __name__ == "__main__":
    main()
