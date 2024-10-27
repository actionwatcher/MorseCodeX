## Summary

MorseCodeX is somewhat similar to RufzXP, originally developed for Mac users. Implemented in Python, it works on Windows and Linux as well. The app allows practice in a realistic environment for both calls and contest exchange messages. The data source may be selected from SCP (supercheck partial), text files, or call history files. The format of the file is determined automatically. The application supports English and Cyrillic character data sources.

## Design Philosophy

MorseCodeX is designed with a clear focus on enhancing on-the-air contest skills through a divide-and-conquer methodology. While the ultimate goal aligns with similar apps like MorseRunner and RufzXP, MorseCodeX sets itself apart by allowing users to practice key components of their contesting skill set independently, making preparation more efficient and targeted toward specific contests.

During a contest, operators rely on a variety of distinct skill elements, such as:
- Call receiving
- Exchange receiving
- Handling weak signals
- Managing QRM (interference)

Call receiving is a fundamental skill applicable across all contests. However, its challenges can vary significantly depending on factors such as station setup, geographic location, and the specific contest. For example, an operator in California running 100 watts during the ARRL Sweepstakes might rarely face pileups, while someone operating from a rare state or superstation will likely encounter more intense pressure. MorseCodeX acknowledges these differences, helping users develop appropriate expectations and practice accordingly.

Exchange receiving, on the other hand, is highly contest-specific. Different contests introduce variations in sending patterns, such as whether a station sends "TU", "QSL", or nothing at all before transmitting an exchange, or how serial numbers are presented (as letters or numbers). To prepare for these nuances, MorseCodeX enables focused training on specific contest exchange formats, offering users a valuable preparation opportunity before the event.

Additionally, the ability to operate in noisy environments or when experiencing QRM is a vital, yet distinct, skill. MorseCodeX allows operators to hone these skills separately, ensuring that their speed and accuracy remain stable under real-world conditions. Through this approach, the app equips users to maintain high performance even in challenging circumstances, while supporting continuous improvement.


## Source Code Installation (prefered)

Python 3.9 + required (it can be used with lower version of Python but coloring of the result screens will be incorrect due to a bug in tkinter)
Following packages (channel::package) with all the dependencies need to be installed:
- conda-forge::python-sounddevice (numpy will be installed as dependency)
- only for macs: tkmacosx (that needs to be installed through pip3: pip3 install tkmacosx)

## Binary Installation MacOS

- download and unarchive MorseCodeX.zip for Windows or for Macs
- verify sha
- drag MorseCodeX app into your /Applications folder on Macs or your preferred location for Windows
- Run MorseCodeX and approve security requests for it

## Data Source Files

Training files are supercheck partials or call history files from N1MM+ logger website thus the training will be on callsignes or exchange messages. However the same way one can form any text file. For example the most common 100 words or anything one desires. Another example can be exchanges for specific contests, letters, numbers, mix and groups. 

Several message source files are povided for your convinuence.

SCPs for call practice (detailed description https://www.supercheckpartial.com):
- MASTER.SCP World contest
- MASTERSS.SCP - US and US territories and Canada
- MASTERDX.SCP - Everything but not US and VE
- MASTERUSVE.SCP - US and Canada

Words: (general practice)
- letters.txt
- numbers.txt
- common100.txt - most common 100 enblish words

Call history: (for exchange practice)
- NAQPCW.txt - North America QSO party 
- states_provinces.txt (US states and Canada provinces)
- ca_counties.txt - California counties (for California QSO Party practice)
- cqp.txt - California counties + US states and Canada provinces (for California QSO Party practice)
- CWOPS_3600-DDD.txt - CWOps minitest practice
- arrl_sweepstakes.txt - ARRL Sweepstakes

The QRN noise is lightdimmer.wav from ARRL website. Feel free record yourown and store it in qrn.wav file. Make sure that it is int16 wav and not float 32 @ 24000 samples per second at least

The QRM is slightly off frequency CQing from NU6N

Premessage checkbox controls if the app sends the pre exchange word: tu, r, qsl to simulate contest environment. There is no uniformity and requirements in the contests and I hear that operators send any of those with tu being the most frequent. Like in real contest sometimes the premessage is not sent

Ser Num checkbox will allow sending random numbers with both cut and full numbers like you will hear in real contest


## Latest Release V1.1.0.0

Supports customizable message formation policies, expanding support for various contest exchanges. This version adds support for ARRL Sweepstakes exchanges. Provides extended statistics accumulated across sessions, including sustained speed with errors below a 3% threshold and maximum speed with errors above a 25% threshold.

Mac: 2cb40bc61a5fd1983e1646537c4dee841efc3165664117eb352cf082e1f61d67  MorseCodeX.zip
Windows: c02a101ea93499c7a19a45548efe125d2f82a8047bc29f7d34e24f08ac0b4c30 MorseCodeX.zip

