# Reverse Engineering the KACO Blueplanet NX3 M2 HTTP Interface

I recently installed a new solar inverter from Kaco (Blueplanet NX3 M2 8.0 to be
specific). This is a pretty basic no-frills inverter which comes with a no-UI
Modbus/TCP interface on standard port 502. This is well documented.

In addition it comes with a Android and iOS app to do the initial set up and
provide some monitoring. The App also asks for a password to change the settings
after first set up (these are quite sensitive for the power grid).

I noticed that the app shows a bit more data (in particular the power for each
of the individual MPPT trackers) and wanted to integrate this in my reporting.


## Finding the HTTP port

There are probably a lot of ways to do this, but I was lazy and did a
```
nmap -sT -p1-65535 IP
```
against the inverter. This found port 502 (expected, modbus) and port 8484
open (exciting!).

Running `curl` against the IP gave me a disappointing `404 not found` error.

I tried a few urls (index.html, data.json, etc.) but to no avail.


## Finding the URLs

Next I downloaded the Android APK of the "KACO NX Setup" app, unzipped the
APK, decompiled the DEX files (using a tool called `jadx`):
```
git clone https://github.com/skylot/jadx.git
./gradlew dist
build/jadx/bin/jadx -d ../decompile/ ../classes.dex ../classes2.dex
```

Looking through the files, and strings, first thing to notice, that the main
app is called `com.aiswei.tool`.  In the `https` subdirectory there is an
`APIServiceV2.java` and `AcApi.java` which contains everything we need!

First target seems to be `getdev.cgi`:

```
curl http://IP:8484/getdev.cgi

{"psn":"scrubbed","key":"scrubbed","typ":5,"nam":"Wi-Fi Stick","mod":"B32078-10","muf":"KACO","brd":"KACO","hw":"M11","sw":"21618-006R","wsw":"ESP32-WROOM-32U","tim":"2022-11-11 13:19:34","pdk":"","ser":"","protocol":"V1.0","host":"cn-shanghai","port":1883,"status":-1}
```

This shows us a few interesting things

* It runs on an ESP32 module
* There seems to be MQTT support (host cn-shanghai, port 1883)

Unfortunately the other URLs didn't quite work but expected some parameters.

As I'm really lazy at reading code, I decided it would be more fun to
set up a fake inverter proxy.


## Fake inverter

I decided to use flask to build a fake inverter interface (see `fake_inverter.py`).

First step was to add a `/getdev.cgi` response. Running the KACO NX App on the phone, indeed found the
fake inverter (the "scanning" seems to just do a probe of port 8484 of all local devices on the network.
Next thing the app requests is

```
/wlanget.cgi?info=2
{"mode":"STATION","sid":"lasseredn","srh":-43,"ip":"192.168.2.218","gtw":"192.168.2.1","msk":"255.255.255.0"}

```

Mocking this out leads to 

```
/getdev.cgi?device=2
{"inv":[{"isn":"8.0NX312008413","add":3,"safety":70,"rate":8000,"msw":"V610-03043-04 ","ssw":"V610-60009-00 ","tsw":"V610-11009-01 ","pac":386,"etd":58,"eto":461,"err":0,"cmv":"V2.1.1AV2.00","mty":51,"psb_eb":1}],"num":1}
```

and ultimately

```
getdevdata.cgi?device=2&sn=8.0NX312001234

{"flg":1,"tim":"20221111140900","tmp":365,"fac":5001,"pac":381,"sac":381,"qac":0,"eto":461,"etd":58,"hto":58,"pf":100,"wan":0,"err":0,"vac":[2333,2350,2358],"iac":[7,8,7],"vpv":[3517,3600],"ipv":[50,57],"str":[]}
```

to get all the data we need:

* vpv 0.1V of voltage
* ipv 10mA steps of current
* fac is the frequency of the net in centi Hertz

etc.

## The Key

Remember I mentioned above, that you need key to access the Installer settings? I got
really curious what request would be send to the device when opening up the menu.

Interestingly enough - no request! The validation must be happening completely in the
App.

And indeed `AES.java` and `CipherUtil.java` do all the "magic". Which is kind of 
funny if it wouldn't be true:

* The algorithm takes the inverter serial number (ISN), ie. 8.0NX312001234
* It uses a fixed key (in AES.java) to encrypt it using the ECB Cipher
* It also provides an IV - which isn't even used by ECB
* Then it MD5 encodes the output - with a custom written bytes to char function no less
* Then it cuts 4 characters out of the string
* that's the "password", 16 bits of obfuscation

See `kaco_pass.py` for the python implementation. Just call the tool with the
serial number as an argument.


## Next steps

I'm going to write a module for the excellent Victron VenusOS to display the values
of the individual inverters.

