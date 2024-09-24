Summary

MorseCodeX is somewhat similar to RufzXP that I wanted for myself on Mac. Though since it is Python it should work on Widnows and Linux as well. I extended the capabilities so it can be used to pactice contest environment for both calls and messages. The data source is selectable and can be SCP(supercheck partial), text (every message in separate line) or call history files. Format of the file determined automatically. In case of call history files the application extracts only message part it randomly select names for entries without names. As v1.0.0.0 only few contest formants supported that usually include serial number, name, state, spc
The application supports English and Cyrillic characters data sources for V1.

Source Code Installation (prefered)

Python 3.9 + required (it can be used with lower version of Python but coloring of the result screens will be incorrect due to a bug in tkinter)
Following packages (channel::package) with all the dependencies need to be installed:
* conda-forge::python-sounddevice (numpy will be installed as dependency)
* only for macs: tkmacosx (that needs to be installed through pip3: pip3 install tkmacosx)

Binary Installation MacOS

* download and unarchive MorseCode_win.zip for Windows or for Macs
* verify sha:
  * 2a186a10fe6cb907783b064808740e4796ec0ffa93626ee80009ee37710144f1 *MorseCodeX_win.zip
  * 2d71e542ce40eb9bbcf7c244950bf0642a9d725d993ef1d974617f270a953a40  MorseCodeX_macOS.zip
* drag MorseCodeX app into your /Applications folder on Macs or your preferred location for Windows
* Run MorseCodeX and approve security requests for it

Training files are supercheck partials or call history files from N1MM+ logger website thus the training will be on callsignes or exchange messages. However the same way one can form any text file. For example the most common 100 words or anything one desires. Another example can be exchanges for specific contests, letters, numbers, mix and groups. 

Several message source files are povided for your convinuence.

SCPs for call practice (detailed description https://www.supercheckpartial.com):
* MASTER.SCP World contest
* MASTERSS.SCP - US and US territories and Canada
* MASTERDX.SCP - Everything but not US and VE
* MASTERUSVE.SCP - US and Canada

Words: (general practice)
* letters.txt
* numbers.txt
* common100.txt - most common 100 enblish words

Call history: (for exchange practice)
* NAQPCW.txt - North America QSO party 
* states_provinces.txt (US states and Canada provinces)
* ca_counties.txt - California counties (for California QSO Party practice)
* cqp.txt - California counties + US states and Canada provinces (for California QSO Party practice)
* CWOPS_3600-DDD.txt - CWOps minitest practice

The QRN noise is lightdimmer.wav from ARRL website. Feel free record yourown and store it in qrn.wav file. Make sure that it is int16 wav and not float 32 @ 24000 samples per second at least

The QRM is slightly off frequency CQing from NU6N

Premessage checkbox controls if the app sends the pre exchange word: tu, r, qsl to simulate contest environment. There is no uniformity and requirements in the contests and I hear that operators send any of those with tu being the most frequent. Like in real contest sometimes the premessage is not sent

Ser Num checkbox will allow sending random numbers with both cut and full numbers like you will hear in real contest


Latest Release

V1.0.0.0

