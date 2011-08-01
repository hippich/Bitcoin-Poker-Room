<?php // -*- php -*-
  //
  // Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
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

ini_set('include_path', ini_get('include_path') . ":" . "../pokerweb/pages");

require_once 'PHPUnit/Framework/TestCase.php';

define('VERBOSE', 0);

require_once 'birthday.php';

class testbirthday extends PHPUnit_Framework_TestCase
{
  public function test01_get_fields()
  {
    $birthday = new birthday();
    $_GET['field1'] = '1';
    $this->assertEquals(1, $birthday->get_field('field1'));
    $_POST['field1'] = '2';
    $this->assertEquals(2, $birthday->get_field('field1'));
  }

  
  public function test02_form_day()
  {
    $_GET['birthday'] = '3';
    $birthday = new birthday();
    $this->assertRegExp('/selected">3/', $birthday->form_day());
  }

  public function test03_form_month()
  {
    $_GET['birthmonth'] = '2';
    $birthday = new birthday();
    $this->assertRegExp('/value="2" selected/', $birthday->form_month());
  }

  public function test04_form_year()
  {
    $_GET['birthyear'] = '1959';
    $birthday = new birthday();
    $this->assertRegExp('/value="1959" selected/', $birthday->form_year());
  }
  
  public function test05_form()
  {
    $birthday = new birthday();
    $this->assertRegExp('/ - /', $birthday->form());    
  }

  public function test06_as_string()
  {
    $_GET['birthday'] = 1;
    $_GET['birthmonth'] = 2;
    $_GET['birthyear'] = 3;
    $birthday = new birthday();
    $this->assertEquals('3-2-1', $birthday->as_string());
    $birthday->day = '';
    $this->assertEquals('', $birthday->as_string());
  }

  public function test07_set()
  {
    $birthday = new birthday(strtotime('1965-3-1'));
    $this->assertEquals(1, $birthday->day);
    $this->assertEquals(3, $birthday->month);
    $this->assertEquals(1965, $birthday->year);
  }
}

//
// Interpreted by emacs
// Local Variables:
// compile-command: "( cd .. ; ./config.status tests/testbirthday.php ) ; ( cd ../tests || cd ../../tests ; make TESTS='testbirthday.php' check )"
// End:
?>
