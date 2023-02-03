# tempcontrol
My side project to automate heating at our weekend house

## TL;DR

Part of the fun of a side project is to sharpen writing skills and
create a long story of how this all came about for those interested.
(OK, mostly just myself.) If you don't need the drama, I prepared a
[summary](#list-of-equipment-needed) of the hardware needs and wrote a
section on the [setup](#setup-and-configuration). 

## Introduction

My in-laws live close to our weekend house. We don't, at least by
local standards.  At some point I thought it was awkward to ask them
to turn on the heating at our weekend house every time before we
arrived in cold weather. They don't live *that* close.  When I
mentioned this to my father-in-law, he suggested me to exchange some
cash for a simple remote controlled relay at an appropriate ecommerce
site. Everything seemed so simple! But then... I started giving some
more thoughts to the plan and my journey into the Internet of Things
(IoT) started.

## Business requirements and basic parameters

Our weekend house has four radiators, each plugged into its own
outlet, so controlling them requires four simple remote controlled
relays instead of one. Heck, I can live with that. Remote controlling
anything requires some kind of a connection between you and the thing
you are controlling remotely. Here are the reasonable options I could
think of at the time:

    1. Fixed internet connection: there is only one provider
    available, and they are known to be expensive and
    unreliable. (Sounds familiar?) *Not good.*
    
    1. Cellular data connection, of which there are two options:
    
        1. Standard cellular data connection: my remote controller would
        probably have a hard time with dyndns. IP addresses
        only remain unchanged for the lifetime of the MPLS context in
        the mobile operator's backbone, of which I have zero
        control. So this option requires a server that the remote
        controller can connect to. Sounds a little bit more
        complicated than what I wanted to build. *Not good.* (Everyone
        makes bad decisions, don't they?)

        1. IoT SIM cards: data traffic is very limited. It might have
        been enough if I had had more experience and I had known
        exactly what I wanted to do and *how*. Some of these cards are
        only sold to businesses, others have more recurring costs than
        I am comfortable with. *Not good.*

    1. SMS: simple, reliable, cheap, and even my wife could control
    the system easily from anywhere without having to remember funky
    domain names and struggling with my poor web interface design. *Might work.*

So I concluded that I wanted to use the good old SMS service to
control four relays remotely. I silently stepped up one grade on the
ladder of complexity.

## Hardware choice

### Relays

There exists a wide variety of smart relays in online stores. Some
even look like normal power outlets. Remote control is usually
implemented via proprietary mobile apps, an internet connection, and
servers "in the cloud". Alas, these clouds often happen to reside in
data centers in China. Who takes issue with the fact that some server
in China receives regular updates about the temperature in one's own
weekend house and issues commands that control the operation of
electrical devices installed at said house? I do. (By the way, that's
another reason for ruling out an internet connection. And the idea of
implementing old-school SMS control was so thrilling that I just
couldn't resist it anyway.) But that means I need some sort of a
server that translates the SMS to some language that remote controlled
relays can understand.

### Controller

I heard that Arduino makes a great controller for simple projects such
as this one. I also heard that it's not exactly plug-and-play, and one
needs to solder resistances here and there occasionally to avoid
bricking devices. I always wanted to be able to do that, but I was
afraid to spend too much time on this before making any progress.

So I went for a Raspberry Pi (RPi). I had given RPi a try earlier and
I found it can do a wonderful job as a Minecraft server for my older
daughter and as an ad blocker for the subset of my family who are
willing to lose their ability to click on google ads next to search
results. I realize I am paying some extra here for my lack of
understanding of electrical circuitry.

### GSM connectivity

However, a RPi can't send SMS out of the box. First I looked at RPi
extensions (called hats in RPi lingo), and the only one available from
a local internet store was one with GSM/GPRS/LTE/GPS/GLONASS
capabilities costing as much as another RPi. That seemed way too much.

My second idea was to use a simple USB mobile data stick. It is
supposed to be a GSM modem after all. USB mobile data stick
manufacturers tend to release new models with *significant* changes in
capabilities *without* clearly indicating those changes. After reading
about other people's experiences and reconciling those with product
availability I ended up buying a DLink DWM-222 stick.

Apparently, not all DWM-222 sticks are created equal. [This excellent
page](https://wiki.dd-wrt.com/wiki/index.php/3G_/_3.5G) lists USB
sticks with ID's displayed by the `lsusb` command. Mine had
`2001:7e46`. It's disappointing that I need to use a Linux machine to
learn about what product I bought, isn't it? Anyway, my brand new
DWM-222's edge over older DWM-222 models is that it lost the GSM modem
functionality. As a result, it could only be mounted as some kind of a
fake Ethernet interface to the mobile data network, *even though* the
manufacturer's proprietary Windows software could make it send and
receive SMS messages. Back it went to the shop.

I kept browsing in search of a better RPi hat, allowing myself to
consider webshops abroad this time. Luckily, I found an excellent
[webshop](https://rlx.sk/en/) that had a SIM800C GSM/GPRS/Bluetooth
HAT for Raspberry Pi (by Waveshare) on stock for a fraction of the
price. I was on to something!

### Back to relays

The question that was still open was that of communication between the
RPi and the relays. I wanted to avoid having to deal with IoT
protocols to the extent possible and I found that
[Shelly](https://shelly.cloud) manufactures relays that can work off
the cloud, have built-in WiFi, support HTTP webhooks, and can handle
16A load.

### Thermometer

Finding a suitable thermometer was easy at this point: Shelly
manufactures those, too. I checked the fine print and I found that
their thermometer uses a battery, which I didn't like. Some more
investigation unveiled that a USB connector piece is also available as
an alternative power supply for the thermometer. I felt so clever! At
this point I had no idea that this thermometer was going to be the
most difficult piece in the game, because I stopped checking the fine
print after I resolved the battery gotcha.

### List of equipment needed

TBA: add summary of equipment needed.

## System architecture

TBA: figure

The system architecture evolved quite a bit as I made progress with
the implementation. First, I only wanted to have some sort of a web
service in charge of controlling the relays over local WiFi, and
receiving the temperature measurements over HTTP.

Everybody has a plan until they get punched in the face. My punch came
from the thermometer. Shelly H&T is designed to consume very little
energy. After powering on the device you only have a few minutes to
talk to it over its own WiFi to make the config changes that you
desire. After that, it will only turn on for a very short time once
every ten minutes (when ran from USB power, otherwise once every hour)
in order to take a new measurement and let interested peers know about
it. No matter how I tried to make it talk to my web service via HTTP,
the damned thing would remain silent. The debug logs that I could pull
from the Shelly H&T's UI didn't contain any useful information. I was
desperate to the point of [wiresharking](https://www.wireshark.org)
the hell out of it, but without any luck. At this point I felt that my
plan was coming down. This was the most difficult point in the
project.

In the absence of any better ideas, I started to play with random
settings, and for whatever reason I enabled using
[MQTT](https://mqtt.org) in the Shelly H&T config screen. That did the
trick: it started to talk to my web service via HTTP. I was overjoyed
and intrigued at the same time. Finally, I started to feel that the
whole plan is going to end up producing a working system.

I decided that I would read Shelly's developer docs about MQTT support
and I found some very interesting stuff. Everything I read made sense
and sounded simple, so I went ahead and installed
[Mosquitto](https://mosquitto.org/) and started getting my hands dirty
with MQTT. I realized quickly that MQTT allows me to build something
much more robust and far superior than my original web service design.

So I ended up adding an MQTT client to my architecture, which would be
in charge of talking to each device and actually controlling them.

When I was playing with random settings three paragraphs earlier, I
noticed that Shelly H&T's need an NTP server. After all, they need to
wake up in regular time intervals. In my test environment at home this
was not a problem, because the device had access to the Internet
through the RPi's WLAN. But that would not be the case in the
production environment.

RPi's are stuffed with functions, but a real time clock (or RTC in NTP
lingo) is not in their bag of tricks. So even if the RPi runs a NTP
server, it still needs a time source. The `fake-hwclock` service can
help, but over time significant drift may be accumulated if there is
no external time source to sync to.

GSM to the rescue! You may have noticed that cell phones can query the
local time from the GSM network. It is especially useful when you are
travelling across time zones. If the network can tell the time to a
cell phone, it sure can do the same to a GSM RPi hat. The only nuance
here is that the network won't bother you with this unless you ask for
it. That's not terribly difficult though: you just need to run the
appropriate `AT` commands.

Talking about `AT` commands, they are also needed for sending and
receiving SMS. The good people who implemented the [gammu
library](https://docs.gammu.org/) abstracted away this complexity.
Information exchange with a GSM modem is conversational by its nature,
and not event driven. Therefore, one needs to poll the modem
periodically to learn about new messages arrived since you two talked
most recently. Gammu has a solution for that, too. `gammu-smsd` is a
daemon process that performs the polling and can be asked to invoke
any unix command when a new message arrives. That should do the job.

### Components

After all these considerations, here are the logical components in the
architecture that I ended up needing to set up or implement:

    1. HTTP service, whose main reponsibilities are the following:

        1. Local user interface for control and diagnostics
        1. Temperature measurement registry
        1. SMS command interface

    1. Database backend to store the following:

        1. Temperature measurements
        1. System state changes

    1. MQTT server

    1. MQTT client to send control messages to relays

    1. NTP server to provide a reference time for Shelly H&T

    1. Some script to sync system time with GSM time

    1. SMS polling and sending service

### Messaging

The following interfaces are needed between the components in the system:

    1. HTTP REST API

    1. Database schema - not a real interface, but...

    1. MQTT messaging protocol between HTTP service and MQTT client

    1. SMS protocol

### Design for robustness

#### What could go wrong?

First, let me enumerate all the things that I could imagine to fail at
some point.

    1. The power grid. Well, that is a single point of failure. If there is no power there is no heating, so nothing to control anyway.

        1. What if the power comes back? The system should be set up so as to boot into operational state without manual assistance.
        
        1. What if the system fails to boot properly after a power outage? It would be important to at least retain the ability to run the system manually without having to uninstall the relays. Also, it would be great if the default state of the relays allowed the radiators to heat without any manual intervention.

        1. What if a partial power outage only affects one or more of the radiators (and the respective relays)? They should get some control message every now and then to make sure they operate as expected.

    1. The RPi. Yet another single point of failure. The RPi could freeze or it could do unexpected things. Unfortunately, there is not much we can do about it given the capabilities of the other components. But it would be useful if one could get the system to work without the controls in a simple way manually.

    1. The relays. Relays can probably fail in multiple ways, but given that they are wired into the circuit without redundancy, there is not much that we can do to address that.

    1. The thermometer. It's easy to notice if measurements have been missing for some time, but there is no way we could validate them and recognize a reasonable but false reading without some external reference. There should be some independent control to prevent overheating though.

    1. The radiators. It's also easy to notice if you are asking for some temperature but the system is unable to reach it.

    1. The user. The weakest point sometimes. What I want to avoid here is really to remain without the ability to control heating when I am physically present without my cell phone or any WiFi-enabled computer.

#### What can I do about it?

Whenever possible, I want the system to heal itself. I also want to
learn about any suspicious conditions so as to allow me to intervene
manually, if needed.

In the absence of redundancy, I decided to take the following steps to
improve robustness and safety.

    1. I set the default state after power-on in the Shelly relays to 'on'.

    1. When I send MQTT messages I mark them as 'last known good'/retained messages for the topic.

    1. I set the built-in thermostat of the radiators to 24C. This setting persists even after a power outage. (Lucky me. In case you are interested, fiddling with the control electronics of the radiators is beyond my capabilities. They don't have any external interface except for the power plug and a few manual buttons.)

    1. I added a periodic health check to the system that verifies if there are recent thermometer readings and if the temperature has stayed below the target for too long. It sends me a message if the systems fails the check.

    1. I added a manual mode to the system, where the RPi instructs the relays to switch on, and so the built-in thermometers of the radiators will control the heating just like in the good old times.

If there is power and the control system is unusable because of a failed RPi or thermometer, but the relays are still working, one can power off the RPi and the radiators in the fuse box, unplug the RPi, and then restore the power and have the system running as if there was no remote control.

## Setup and configuration

This section is intended for record keeping rather than explanation.

### Wiring

### RPi

#### Gammu

#### MQTT server

#### NTP server

#### Other services needed

### Shelly

#### Relays

#### Thermometer

### Python package installation

### Python package version upgrade

## Lessons learned

I realize that some of what follows sounds obvious, but I still wanted
to collect these thoughts.

    1. DIY-frindly off-the-cloud IoT products exist.

    1. Check all the fine print, even after you find the first gotcha.

    1. MQTT sounds like an intimidating acronym, but it is actually a very
    reasonable protocol. In fact, I can hardly imagine doing the job in a
    simpler way.

When working on this side project I had a lot of fun in the best sense
of the word. It proved to be challenging and lasted for long enough so
that it felt like a meaningful effort. It also solved a real problem.
I learned a lot about IoT and python, and enjoyed spending some late
hours trying to figure out how to make things work. Heck, I am proud
that it works, even though I am sure there are more efficient ways to
achieve the goals that I set in the beginning.