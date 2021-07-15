Title: mDNS for Linux
Author: Mats Melander
Date: 2021-05-02
Modified: 2021-05-02
Tags: Linux, mDNS
Category: Technologies
Summary: Description of mDNS configuration for Linux Mint 20.1

Switching from Linux Mint 19 to Linux Mint 20.1 meant that pinging host on my local network stopped working.
I could still ping them using IP-addresses, but not their host names

```bash
mm@wolfrax:~/dev/pyPDP/asm$ ping rpi2.local
ping: rpi2.local: Name or service not known
mm@wolfrax:~/dev/pyPDP/asm$ ping 192.168.1.51
PING 192.168.1.51 (192.168.1.51) 56(84) bytes of data.
64 bytes from 192.168.1.51: icmp_seq=1 ttl=64 time=10.3 ms
```

How come? This made me search and read on the configuration for mDNS.
Until I found the right solution, I edited `/etc/hosts` with hard-coded
node name and IP-address (which is Ok, as I have configured static IP-addresses for these nodes).
These looks like so,

```bash
mm@wolfrax:~/dev/pyPDP/asm$ cat /etc/hosts
127.0.0.1	localhost
127.0.1.1	wolfrax

192.168.1.50	rpi1
192.168.1.51	rpi2
192.168.1.52	rpi3
192.168.1.53	rpi4
192.168.1.54	rpi5	

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
mm@wolfrax:~/dev/pyPDP/asm$ ping rpi2
PING rpi2 (192.168.1.51) 56(84) bytes of data.
64 bytes from rpi2 (192.168.1.51): icmp_seq=1 ttl=64 time=6.61 ms
```

#mDNS
[Multicast DNS](https://en.wikipedia.org/wiki/Multicast_DNS) (mDNS) resolve hostnames to IP-addresses for local networks.
By default mDNS resolve hostnames with top-domain `.local`. So, `rpi2.local` would resolve to IP-address `192.168.1.51`
in my network.

There seems to be several ways to do this in a Linux environment, 3 of them are:

1. [Avahi](https://en.wikipedia.org/wiki/Avahi_(software))
2. [NetworkManager](https://en.wikipedia.org/wiki/NetworkManager)
3. systemd-resolved, see [systemd](https://en.wikipedia.org/wiki/Systemd) and [systemd-resolved](https://wiki.archlinux.org/title/Systemd-resolved)

If not configured correctly, they might counteract each other. 
See [this article](https://wiki.archlinux.org/index.php/Systemd-resolved#mDNS) where disabling Avahi is suggested.

After some searching, I found [this thread](https://forums.linuxmint.com/viewtopic.php?p=1949048&sid=5bca7944423fb53de8a9dd8fb0c68ca5#p1949048)
where the problem I have where noted and resolved...somehwat.
The core of the thread is to enable multicastDNS by editing `/etc/systemd/resolved.conf` and editing the file so
```ini
MulticastDNS=yes
```
Then issue the following command (change interface to appropriate value) to set mdns for the interface
```bash
$ sudo systemd-resolve --set-mdns=yes --interface=wlp3s0
$ ping rpi2.local
PING rpi2.local (192.168.1.51) 56(84) bytes of data.
64 bytes from rpi2 (192.168.1.51): icmp_seq=1 ttl=64 time=5.26 ms
64 bytes from rpi2 (192.168.1.51): icmp_seq=2 ttl=64 time=5.34 ms
$ resolvectl
Global
       LLMNR setting: no                  
MulticastDNS setting: yes                 
  DNSOverTLS setting: no                  
      DNSSEC setting: no                  
    DNSSEC supported: no                  
          DNSSEC NTA: 10.in-addr.arpa     
                      16.172.in-addr.arpa 
                      168.192.in-addr.arpa
                      17.172.in-addr.arpa 
                      18.172.in-addr.arpa 
                      19.172.in-addr.arpa 
                      20.172.in-addr.arpa 
                      21.172.in-addr.arpa 
                      22.172.in-addr.arpa 
                      23.172.in-addr.arpa 
                      24.172.in-addr.arpa 
                      25.172.in-addr.arpa 
                      26.172.in-addr.arpa 
                      27.172.in-addr.arpa 
                      28.172.in-addr.arpa 
                      29.172.in-addr.arpa 
                      30.172.in-addr.arpa 
                      31.172.in-addr.arpa 
                      corp                
                      d.f.ip6.arpa        
                      home                
                      internal            
                      intranet            
                      lan                 
                      local               
                      private             
                      test                

Link 3 (wlp3s0)
      Current Scopes: DNS mDNS/IPv4 mDNS/IPv6
DefaultRoute setting: yes                    
       LLMNR setting: yes                    
MulticastDNS setting: yes             
```

Works! Until you switch the interface off, then on again. The mdns setting for the interface has been lost. :-(

But, it can be fixed! Here is how.

Create a file named for example `wifi.network` (it can be named anything, but the file extension *must* be `network`).
Store the file in `/etc/systemd/network`. The content of the file is
```ini
[Match]
Name=w*

[Network]
DHCP=yes
MulticastDNS=yes
LLMR=no
```

Note the wildcard on the Match-section. It could also be stated as `Name=wlp3s0`.
So, the logic is that mDNS needs to be enabled *both* in `resolved.conf` (globally) and per link in a new file with
extension `network` to become persistent.

Make systemd read the changes and check status using [networkctl](https://www.freedesktop.org/software/systemd/man/networkctl.html#)
```bash
$ networkctl reload
$ networkctl list
IDX LINK      TYPE     OPERATIONAL SETUP     
  1 lo        loopback carrier     unmanaged 
  2 enp0s31f6 ether    no-carrier  unmanaged 
  3 wlp3s0    wlan     routable    configured
```

Now, the system should find `rpi2.local` always.

Note that if `systemd.networkd` is not enabled/running, do this through
```bash
$ sudo systemctl enable systemd-networkd
$ sudo systemctl start systemd-networkd
```

# Using DNS stub file

Note below information from [archlinux](https://wiki.archlinux.org/title/Systemd-resolved#DNS):
> Using the systemd DNS stub file - the systemd DNS stub file `/run/systemd/resolve/stub-resolv.conf` contains the local 
stub 127.0.0.53 as the only DNS server and a list of search domains. This is the recommended mode of operation. 
The service users are advised to redirect the /etc/resolv.conf file to the local stub DNS resolver file 
`/run/systemd/resolve/stub-resolv.conf` managed by systemd-resolved. This propagates the systemd managed configuration 
to all the clients. This can be done by replacing /etc/resolv.conf with a symbolic link to the systemd stub:
>
```bash
$ sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
```

