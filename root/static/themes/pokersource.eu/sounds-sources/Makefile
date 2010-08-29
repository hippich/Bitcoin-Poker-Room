#
#     Copyright (C) 2008 - 2010 Loic Dachary <loic@dachary.org>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
SOUNDS = \
	player_arrive.ogg \
	player_hand.ogg \
	player_bet.ogg \
	player_call.ogg \
	player_fold.ogg \
	player_check.ogg \
	player_fold.ogg \
	player_timeout_notice.ogg \
	player_timeout_warning.ogg \
	player_win.ogg \
	deal_card.ogg


SWFS = $(SOUNDS:.ogg=.swf)
WAVS = $(SOUNDS:.ogg=.wav)

all build install clobber clean maintainer-clean check::

build:: soundswiff $(SWFS) $(WAVS)
	mkdir -p ../sounds
	cp *.swf ../sounds

maintainer-clean::
	rm -f $(SWFS) $(WAVS) soundswiff

clobber::
	rm -fr ../sounds

soundswiff: soundswiff.c
	gcc -Wall -o $@ $< -lming

license:
	for file in $(SOUNDS) ; do vorbiscomment $$file -w -c copyright.txt ; done

%.wav : %.ogg
	oggdec $<

%.swf : %.wav 
	./soundswiff $< $@

