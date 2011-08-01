<?php // -*- php -*-
//
// Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
// Copyright (C) 2006 Mekensleep <licensing@mekensleep.com>
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
//  Loic Dachary <loic@dachary.org>
//

ini_set('include_path', ini_get('include_path') . ":" . "../pokerweb/pages");

require_once 'PHPUnit/Framework/TestCase.php';

require_once 'currency.php';

$GLOBALS['currency_db_base'] = 'currencytest';
$GLOBALS['currency_db_user'] = 'root';
$GLOBALS['currency_db_password'] = '';

function test_extension_loaded($what) {
  return false;
}

function test_dl($what) {
  return false;
}

class testcurrency extends PHPUnit_Framework_TestCase
{
    private $currency;
  
    protected function setUp()
    {
      error_reporting(E_ALL);

      $this->id = 0;

      $GLOBALS['currency_extension_loaded'] = 'extension_loaded';
      $GLOBALS['currency_dl'] = 'dl';
      $c = mysql_connect($GLOBALS['currency_db_host'], $GLOBALS['currency_db_user'], $GLOBALS['currency_db_password']);
      if(!$c) 
        print "unable to connect to mysql";
      if(!mysql_query("DROP DATABASE IF EXISTS " . $GLOBALS['currency_db_base'], $c)) 
        print "mysql error " . mysql_error($c);
      mysql_close($c);
      $this->currency = new currency($GLOBALS['currency_db_base'], $GLOBALS['currency_db_user'], $GLOBALS['currency_db_password']);
    }
    
    protected function tearDown()
    {
      $this->currency->__destruct();
    }

    public function test01_get_note()
    {
      $note = $this->currency->get_note('100', $this->id);
      $this->assertEquals('http://fake/', $note[0]);
      $this->assertEquals(1, $note[1]);
      $this->assertEquals(40, strlen($note[2]));
      $this->assertEquals('100', $note[3]);
      $this->assertEquals(TRUE, $this->currency->commit($note[2]));
      $this->assertEquals($note, $this->currency->_check_note($note, $this->id));
      return $note;
    }

    public function test02_change_note()
    {
      $note = $this->test01_get_note();
      $other_note = $this->currency->change_note($note[1], $note[2], $note[3], $this->id);
      $this->assertEquals('http://fake/', $note[0]);
      $this->assertEquals(2, $other_note[1]);
      $this->assertEquals(40, strlen($other_note[2]));
      $this->assertNotEquals($note[2], $other_note[2]);
      $this->assertEquals('100', $other_note[3]);
      $this->assertEquals(TRUE, $this->currency->commit($other_note[2]));
      $this->assertEquals($other_note, $this->currency->_check_note($other_note, $this->id));
      return $other_note;
    }

    public function test03_merge_note()
    {
      $note = $this->test01_get_note();
      $notes = $this->currency->merge_notes_columns(array($note[1]), array($note[2]), array($note[3]), $this->id);
      $other_note = $notes[0];
      $this->assertEquals('http://fake/', $note[0]);
      $this->assertEquals(2, $other_note[1]);
      $this->assertEquals(40, strlen($other_note[2]));
      $this->assertNotEquals($note[2], $other_note[2]);
      $this->assertEquals('100', $other_note[3]);
      $this->assertEquals(TRUE, $this->currency->commit($other_note[2]));
      $this->assertEquals($other_note, $this->currency->_check_note($other_note, $this->id));
    }

    public function test03_merge_two_notes()
    {
      $note1 = $this->currency->get_note('100', $this->id);
      $this->assertEquals(TRUE, $this->currency->commit($note1[2]));
      $note2 = $this->currency->get_note('100', $this->id);
      $this->assertEquals(TRUE, $this->currency->commit($note2[2]));
      $this->assertNotEquals($note1[2], $note2[2]);
      $notes = $this->currency->merge_notes_columns(array($note1[1], $note2[1]), array($note1[2], $note2[2]), array($note1[3], $note2[3]), $this->id);
      $this->assertEquals(1, count($notes));
      $other_note = $notes[0];
      $this->assertEquals('http://fake/', $note1[0]);
      $this->assertEquals(1, $other_note[1]);
      $this->assertEquals(40, strlen($other_note[2]));
      $this->assertNotEquals($note1[2], $other_note[2]);
      $this->assertEquals('200', $other_note[3]);
      $this->assertEquals(TRUE, $this->currency->commit($other_note[2]));
      $this->assertEquals($other_note, $this->currency->_check_note($other_note, $this->id));
    }

    public function test03_merge_change_note()
    {
      $note = $this->test02_change_note();
      $notes = $this->currency->merge_notes_columns(array($note[1]), array($note[2]), array($note[3]), $this->id);
      $other_note = $notes[0];
      $this->assertEquals('http://fake/', $note[0]);
      $this->assertEquals(3, $other_note[1]);
      $this->assertEquals(40, strlen($other_note[2]));
      $this->assertNotEquals($note[2], $other_note[2]);
      $this->assertEquals('100', $other_note[3]);
      $this->assertEquals(TRUE, $this->currency->commit($other_note[2]));
      $this->assertEquals($other_note, $this->currency->_check_note($other_note, $this->id));
    }

    //
    // Checks that the 5000 special table is used when merging 2000+3000
    //
    public function test03_merge_note_5000()
    {
      $note1 = $this->currency->get_note('2000', $this->id);
      $this->assertEquals(TRUE, $this->currency->commit($note1[2]));
      $note2 = $this->currency->get_note('3000', $this->id);
      $this->assertEquals(TRUE, $this->currency->commit($note2[2]));

      $notes = $this->currency->merge_notes(array($note1, $note2), $this->id);
      $other_note = $notes[0];
      $this->assertEquals('http://fake/', $other_note[0]);
      $this->assertEquals(1, $other_note[1], "serial");
      $this->assertEquals(40, strlen($other_note[2]));
      $this->assertNotEquals($note1[2], $other_note[2]);
      $this->assertNotEquals($note2[2], $other_note[2]);
      $this->assertEquals('5000', $other_note[3]);
      $this->assertEquals(TRUE, $this->currency->commit($other_note[2]));
      $this->assertEquals($other_note, $this->currency->_check_note($other_note, $this->id));
    }

    public function test04_break_note()
    {
      $note = $this->test01_get_note();
      $notes = $this->currency->break_note($note[1], $note[2], $note[3], $this->id, array('27', '13', '1'));
      $this->assertEquals(10, count($notes));
      $this->assertEquals('http://fake/', $notes[0][0]);
      $this->assertEquals('27', $notes[2][3]);
      $this->assertEquals('13', $notes[3][3]);
      $this->assertEquals('1', $notes[9][3]);
    }

    public function test04_break_note_incomplete()
    {
      $note = $this->test01_get_note();
      $notes = $this->currency->break_note($note[1], $note[2], $note[3], $this->id, array('27'));
      $this->assertEquals(4, count($notes));
      $this->assertEquals('http://fake/', $notes[0][0]);
      $this->assertEquals('27', $notes[2][3]);
      $this->assertEquals('19', $notes[3][3]);
    }

    public function test05_put_note()
    {
      $note = $this->test01_get_note();
      $this->currency->put_note($note[1], $note[2], $note[3], $this->id);
    }

    public function test06_fail_check_note()
    {
      try {
        $this->currency->check_note(1, 'bugous " name', '10', $this->id);
      } catch(Exception $error) {
        $this->assertEquals(currency::E_INVALID_NOTE, $error->getCode());
        return;
      }
      $this->fail('should throw an exception');
    }

    public function test07_fail_check_note()
    {
      $note = $this->currency->get_note('100', $this->id);
      try {
        $other_note = $this->currency->check_note($note[1], $note[2], $note[3], $this->id);
      } catch(Exception $error) {
        $this->assertEquals(currency::E_CHECK_NOTE_FAILED, $error->getCode());
        return;
      }
      $this->fail('should throw an exception');
    }

    public function test08_get_big_note()
    {
      $note = $this->currency->get_note('10000000000000', $this->id);
      $this->assertEquals('http://fake/', $note[0]);
      $this->assertEquals(1, $note[1]);
      $this->assertEquals(40, strlen($note[2]));
      $this->assertEquals('10000000000000', $note[3]);
      $this->assertEquals(TRUE, $this->currency->commit($note[2]));
      $this->assertEquals($note, $this->currency->_check_note($note, $this->id));
      return $note;
    }

    public function test09_mysql_extension()
    {
      $GLOBALS['currency_extension_loaded'] = 'test_extension_loaded';
      $GLOBALS['currency_dl'] = 'test_dl';
      $caught = FALSE;
      try {
        $this->currency = new currency($GLOBALS['currency_db_base'], $GLOBALS['currency_db_user'], $GLOBALS['currency_db_password']);
      } catch(Exception $e) {
        $caught = TRUE;
      }
      $this->assertTrue($caught);
    }

    public function test09_randname()
    {
      $this->assertEquals(currency::key_size_ascii, strlen($this->currency->get_randname()));
      $this->currency->__destruct();
      $this->assertEquals(currency::key_size_ascii, strlen($this->currency->get_randname()));
      $this->currency->random_fd = TRUE;
      $level = error_reporting(0);
      try {
        $this->currency->get_randname();
      } catch(Exception $e) {
        $this->currency->random_fd = FALSE;
      }
      error_reporting($level);
      $this->assertFalse($this->currency->random_fd, "Expected exception when random_fd is TRUE");
    }

    public function test10_fixedname()
    {
      $this->assertEquals($this->currency->fixedname, $this->currency->get_fixedname());
    }

    public function test11_set_url()
    {
      $this->currency->set_url('URL');
      $this->assertEquals("URL", $this->currency->url);
    }

    public function test12_db_check_selected()
    {
      $this->currency->db_base = "NOT NOT";
      $caught = FALSE;
      try {
        $this->currency->db_check_selected();
      } catch(Exception $e) {
        $this->assertContains("selected(1)", $e->getMessage());
        $caught = TRUE;
      }
      $this->assertTrue($caught);
    }

    public function test13_db_check_selected()
    {
      $this->currency->db_prefix = "YARG' YARG";
      $caught = FALSE;
      try {
        $this->currency->db_check_selected();
      } catch(Exception $e) {
        $this->assertContains("selected(3)", $e->getMessage());
        $caught = TRUE;
      }
      $this->assertTrue($caught);
    }

    public function test14_db_check_selected()
    {
      $this->currency->db_prefix = "ZOG ZOG";
      $caught = FALSE;
      try {
        $this->currency->db_check_selected();
      } catch(Exception $e) {
        $this->assertContains("selected(4)", $e->getMessage());
        $caught = TRUE;
      }
      $this->assertTrue($caught);
    }

    public function test15_db_check_selected()
    {
      $this->currency->db_check_connection();
      $this->currency->__destruct();
      $c = mysql_connect($GLOBALS['currency_db_host'], $GLOBALS['currency_db_user'], $GLOBALS['currency_db_password']);
      if(!$c)
        print "mysql connection failed (test15)";
      if(!mysql_query("CREATE DATABASE " . $this->currency->db_base, $c)) 
        print "ERROR create database";
      if(!mysql_select_db($this->currency->db_base, $c))
        print "ERROR select_db " . mysql_error($c) . " " . $this->currency->db_base;
      if(!mysql_query("CREATE TABLE " . $this->currency->db_prefix . "_50 (rowid INT );", $c)) {
        print "ERROR " . mysql_error($c) . " " . $this->currency->db_base;
      }
      mysql_close($c);
      $this->currency->db_check_selected();
      $this->assertEquals('currency_50', $this->currency->value2table[50]);
    }

    public function test16_db_check_selected()
    {
      $this->currency->db_check_connection();
      $this->currency->__destruct();
      $c = mysql_connect($GLOBALS['currency_db_host'], $GLOBALS['currency_db_user'], $GLOBALS['currency_db_password']);
      if(!$c)
        print "mysql connection failed (test16)";
      if(!mysql_query("CREATE DATABASE " . $this->currency->db_base, $c)) 
        print "ERROR create database";
      if(!mysql_select_db($this->currency->db_base, $c))
        print "ERROR select_db " . mysql_error($c) . " " . $this->currency->db_base;
      if(!mysql_query("CREATE TABLE " . $this->currency->db_prefix . "_123 (rowid INT );", $c)) {
        print "ERROR " . mysql_error($c) . " " . $this->currency->db_base;
      }
      mysql_close($c);
      $caught = FALSE;
      try {
        $this->currency->db_check_selected();
      } catch(Exception $e) {
        $this->assertContains('123', $e->getMessage());
        $caught = TRUE;
      }
      $this->assertTrue($caught);
    }

    public function test17_currency_id()
    {
      $GLOBALS['currency_id'] = TRUE;
      $note = $this->currency->get_note('10000000000000', 1);
      $this->assertEquals('http://fake/', $note[0]);
      $this->assertEquals('10000000000000', $note[3]);
      $note = $this->currency->get_note('100', 2);
      $this->assertEquals('http://fake/', $note[0]);
      $this->assertEquals('100', $note[3]);
    }
}

//
// Interpreted by emacs
// Local Variables:
// compile-command: "( cd .. ; ./config.status tests/testcurrency.php ) ; ( cd ../tests || cd ../../tests ; make TESTS='testcurrency.php' check )"
// End:
?>
