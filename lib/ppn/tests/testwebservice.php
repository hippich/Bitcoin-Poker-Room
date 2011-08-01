<?php // -*- php -*-
//
// Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
// Copyright (C) 2007 Mekensleep <licensing@mekensleep.com>
//                    24 rue vieille du temple, 75004 Paris
//
// This software's license gives you freedom; you can copy, convey,
// propagate, redistribute and/or modify this program under the terms of
// the GNU Affero General Public License (AGPL) as published by the Free
// Software Foundation (FSF), either version 3 of the License, or (at your
// option) any later version of the AGPL published by the FSF.
//
// This program is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
// General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program in a file in the toplevel directory called
// "AGPLv3".  If not, see <http://www.gnu.org/licenses/>.
//
// Authors:
//  Johan Euphrosine <proppy@aminche.com>
//

ini_set('include_path', ini_get('include_path') . ":" . "../pokerweb/pages");

require_once 'PHPUnit/Framework/TestCase.php';

require_once 'webservice.php';

class pokermockup
{
	function pokermockup($data)
	{
	$this->data = $data;
	}
	function send($packet)
	{
	return $this->data;
	}
}

class testwebservice extends PHPUnit_Framework_TestCase
{
	public function test01_handle_packet()
	{
		$data = array("what" => "to be json encoded string");
		$poker = new pokermockup($data);
		$this->assertEquals(json_encode($data), handle_packet($poker, ""));
	}
}

//
// Interpreted by emacs
// Local Variables:
// compile-command: "( cd .. ; ./config.status tests/testwebservice.php ) ; ( cd ../tests || cd ../../tests ; make TESTS='testwebservice.php' check )"
// End:
?>
