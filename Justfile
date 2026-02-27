version := "0.1.0"
pi_host := "pi4"

deb_color := if env('TERM', 'dumb') == 'dumb' {
  'DPKG_COLORS=never'
} else {
  'DPKG_COLORS=always'
}

fmt:
	black src/clock.py

deb:
    mkdir -p package/usr/lib/pi-clock
    cp -r src/clock.py src/waveshare package/usr/lib/pi-clock/
    chmod +x src/waveshare package/usr/lib/pi-clock/clock.py
    {{deb_color}} dpkg-deb --build package pi-clock_{{version}}_all.deb

clean:
    rm -rf package/usr/lib/pi-clock pi-clock_*.deb

# Build deb, copy to Pi, reinstall, restart service
deploy: deb
    scp pi-clock_{{version}}_all.deb {{pi_host}}:/tmp/
    ssh {{pi_host}} "sudo dpkg -i /tmp/pi-clock_{{version}}_all.deb"

start:
    ssh {{pi_host}} "sudo systemctl start pi-clock"

stop:
    ssh {{pi_host}} "sudo systemctl stop pi-clock"

setup:
    echo "On the pi: sudo raspi-config nonint do_spi 0"
