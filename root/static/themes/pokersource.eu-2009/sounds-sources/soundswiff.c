/*
*     Copyright (C) 2008 Loic Dachary <loic@dachary.org>
*
*     This program is free software: you can redistribute it and/or modify
*     it under the terms of the GNU General Public License as published by
*     the Free Software Foundation, either version 3 of the License, or
*     (at your option) any later version.
*
*     This program is distributed in the hope that it will be useful,
*     but WITHOUT ANY WARRANTY; without even the implied warranty of
*     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*     GNU General Public License for more details.
*
*     You should have received a copy of the GNU General Public License
*     along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
#include <ming.h>
#include <stdlib.h>
#include <assert.h>

int main(int argc, char** argv)
{
  Ming_useSWFVersion(6);
  assert(argc == 3 && "usage: soundswiff sound.wav sound.swf");
  SWFMovie movie = newSWFMovie();
  SWFMovie_setDimension(movie, 800, 600);
  SWFMovie_setBackground(movie, rand()%255, rand()%255, rand()%255);
  
  SWFSound sound1 = newSWFSound(fopen(argv[1], "rb"), SWF_SOUND_44KHZ|SWF_SOUND_16BITS|SWF_SOUND_STEREO);
  SWFSoundInstance soundInstance1 = SWFMovie_startSound(movie, sound1);
  SWFMovie_nextFrame(movie);
  SWFMovie_save(movie, argv[2]);
  destroySWFMovie(movie);
  return 0;
}

// Interpreted by emacs
// Local Variables:
// compile-command: "gcc -Wall -o soundswiff soundswiff.c -lming"
// End:
