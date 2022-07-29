## Overview

The Domain Name System (DNS) is the Internet protocol and system that maps
human readable names to Internet protocol addresses; it is central to every
Internet activity, from web browsing to video streaming. Despite the central
role of the DNS to essentially all Internet communications, until recently it
has been unencrypted, which as introduced significant privacy risks and
vulnerabilities. In recent years, technology to encrypt DNS queries and
responses includes transmitting DNS queries and responses. This project is
studying the performance and privacy properties of existing encrypted DNS
protocols such as DoH and DoT, towards the ultimate goal of deploying
applications and systems that use these new protocols to improve user privacy
and provide users good performance.  The Internet is rapidly moving towards
encrypted DNS protocols, with encrypted DNS now either available or enabled by
default in many standard Internet browsers and Internet-connected embedded
devices.  Yet, there is relatively little knowledge or agreement about the
performance and privacy characteristics of such protocols.  This project builds
on the early work in this area to develop comprehensive techniques for
evaluating both the performance and privacy of new network applications,
systems, and architectures that rely on encrypted DNS protocols.  The research
will contribute to the larger body of knowledge on both DNS performance and
privacy, and the available performance and evaluation frameworks for evaluating
encrypted DNS protocols will be released to the community to allow others to
continue to build on these results.

The first theme of this project seeks to understand the performance
implications of existing encrypted DNS protocols and architectures, on DNS
lookup time, as well as on the performance of popular Internet applications
whose performance depends on the DNS, particularly for metrics such as web page
load time.  Understanding why (and when) encrypted DNS outperforms unencrypted
DNS---as well as when it does not---will ultimately shed light on how to best
architect DNS resolution to ensure both confidentiality and good performance.
The second theme of this project recognizes that encrypting DNS need not imply
centralization. Distributing a client's DNS queries across multiple recursive
resolvers may improve reliability, privacy, and even performance, although such
improvements will ultimately require the design of appropriate strategies for
distributing these queries. This theme explores the prospect of
re-decentralizing the DNS.  Third, the porject is coalescing various approaches
to DNS privacy---from DNS encryption to previous work on oblivious DNS
(ODNS)---into a coherent architectural framework. This theme explores how and
where DNS privacy extensions could be deployed (e.g., in a local DNS resolver,
in a web browser) to both preserve user privacy and preserve a seamless user
experience.

### Talks

- [IRTF MAPRG](talks/20220729-maprg/doh-measurements-2022.pdf)

### People

- [Ranya Sharma](https://www.ranyasharma.com/)
- [Nick Feamster](https://people.cs.uchicago.edu/~feamster/)
- [Austin Hounsel](https://github.com/ahounsel)

### Funding

This project is supported by National Science Foundation Award #2155128.
