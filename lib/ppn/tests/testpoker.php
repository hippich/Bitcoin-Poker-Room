<?php // -*- php -*-
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

define('VERBOSE', 0);

class nusoapclient
{
  function nusoapclient($host) {
    $this->cookies = array();
    $this->host = $host;
    $this->serial = 1;
    $this->serials = array();
    $this->infos = array();
    $this->images = array();
    $this->wallets = array();
    $this->cookies = array(array('value' => ''));
    $this->fault = FALSE;
    $this->error = FALSE;
    $this->logged_in = FALSE;
    $this->e_personal_info_answer = FALSE;
    $this->e_image_ack = FALSE;
    $this->e_cash_in_info_answer = FALSE;
    $this->e_cash_out_info_answer = FALSE;
    $this->e_cash_out_commit = FALSE;
  }

  function call($what, $message) {
    if(ereg('badscheme', $this->host)) {
      $this->error = 'bad scheme';
      return false;
    }
    return $this->handle($message[1]);
  }

  function handle($packet) {
    if(VERBOSE > 1) error_log('nusoapclient:input: ' . print_r($packet, true));
    if($packet['type'] == 'PacketLogin') {
      if(ereg('badpassword', $packet['password'])) {
        $result = array(array('type' => 'PacketAuthRefused'));
      } elseif(ereg('missingserial', $packet['password'])) {
        $result = array(array('type' => 'PacketAuthOk'));
      } elseif(ereg('unknown', $packet['password'])) {
        $result = array(array('type' => 'UnknownPacketType'));
      } else {
        $name = $packet['name'];
        if(!isset($this->serials[$name])) {
          $serial = $this->serial;
          $this->serials[$name] = $serial;
          $this->infos[$serial] = array('name' => $name);
          $this->wallets[$serial] = 0;
          $this->images[$serial] = '';
          $this->serial++;
        } 
        $_COOKIE['TWISTED_SESSION'] = 'TWISTED_SESSION_COOKIE';
        $this->logged_in = true;
        $result = array(array('type' => 'PacketAuthOk'),
                        array('type' => 'PacketSerial',
                              'serial' => $this->serials[$name]));
      }

    } elseif($packet['type'] == 'PacketError') {
      return array(array('type' => 'PacketError'));

    } elseif($packet['type'] == 'SoapFault') {
      $this->fault = true;
      return array();

    } elseif($packet['type'] == 'NoType') {
      return array(array('notype' => 'ahahaha'));

    } elseif($packet['type'] == 'PacketLogout') {
      $this->logged_in = false;
      $result = array();

    } elseif($packet['type'] == 'PacketPokerGetPersonalInfo') {
      if($this->e_personal_info_answer) {
        $result = array(array('type' => 'UnknownPacket'));
      } elseif($this->logged_in) {
        $result = array(array_merge($this->infos[$packet['serial']],
                                    array('type' => 'PacketPokerPersonalInfo')));
      } else {
        $result = array(array('type' => 'PacketAuthRequest'));
      }

    } elseif($packet['type'] == 'PacketPokerSetAccount') {
      unset($packet['type']);
      $this->infos[$serial] = $packet;
      $result = array(array_merge($this->infos[$packet['serial']],
                                  array('type' => 'PacketPokerPersonalInfo')));

    } elseif($packet['type'] == 'PacketPokerPlayerImage') {
      $serial = $packet['serial'];
      if($this->e_image_ack) {
        $result = array(array('type' => 'UnknownPacket'));
      } elseif(isset($this->infos[$serial])) {
        $this->images[$serial] = $packet['image'];
        $result = array(array('type' => 'PacketAck'));
      } else {
        $result = array(array('type' => 'PacketError'));
      }

    } elseif($packet['type'] == 'PacketPokerGetPlayerImage') {
      $serial = $packet['serial'];
      if(isset($this->images[$serial])) {
        $result = array(array('type' => 'PacketPokerPlayerImage',
                              'serial' => $serial,
                              'image' => $this->images[$serial]));
      } else {
        $result = array(array('type' => 'UnknownPacket'));
      }

    } elseif($packet['type'] == 'PacketPokerCashIn') {
      if($this->e_cash_in_info_answer) {
        $result = array(array('type' => 'UnknownPacket'));
      } else {
        $this->wallets[$packet['serial']] += $packet['value'];
        $result = array(array('type' => 'PacketAck'));
      }

    } elseif($packet['type'] == 'PacketPokerCashOut') {
      if($this->e_cash_out_info_answer) {
        $result = array(array('type' => 'UnknownPacket'));
      } else {
        $this->wallets[$packet['serial']] -= $packet['value'];
        $result = array(array('type' => 'PacketPokerCashOut'));
      }

    } elseif($packet['type'] == 'PacketPokerCashOutCommit') {
      if($this->e_cash_out_commit) {
        $result = array(array('type' => 'UnknownPacket'));
      } else {
        $this->wallets[$packet['serial']] -= $packet['value'];
        $result = array(array('type' => 'PacketAck'));
      }

    } else {
      throw Exception('unknown packet type ' . $packet['type']);
    }
    if(VERBOSE > 1) error_log('nusoapclient:output: ' . print_r($result, true));
    return $result;
  }

  function getError() {
    return $this->error;
  }
}

require_once 'poker.php';

function auth_handler($name, $uri) {
  $GLOBALS['auth_handler_called'] = array('name' => $name, 'uri' => $uri);
}

ob_start();

class testpoker extends PHPUnit_Framework_TestCase
{
  public function test01_login()
  {
    $poker = new poker('fakehost');
    $poker->verbose = VERBOSE;
    $poker->setTimeoutCookie('5');
    $poker->login('user', 'password');
    $this->assertNotEquals(false, $poker->isLoggedIn());
  }

  public function test02_image()
  {
    $poker = new poker('fakehost');
    $poker->verbose = VERBOSE;
    $poker->login('user', 'password');
    $poker->setPlayerImage('../tests/chameleon.png', 'image/png', 100, 100);
    $poker->getPlayerImage($poker->serial);
    $poker->setPlayerImage('../tests/chameleon.png', 'image/png', 2, 100);
    $poker->setPlayerImage('../tests/chameleon.png', 'image/png', 100, 2);
    $poker->setPlayerImage('../tests/chameleon.png', 'image/png', 2, 2);
  }

  public function test03_fail_connect()
  {
    try {
      $poker = new poker('badscheme://fakehost');
      $poker->login('user', 'password');
    } catch (Exception $e) {
      if($e->getCode() == poker::E_SEND_CALL_SOAP_ERROR)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_SEND_CALL_SOAP_ERROR');
    }
    $this->fail('no exception raised where E_SEND_CALL_SOAP_ERROR expected');
  }

  public function test04_login_failed()
  {
    try {
      $poker = new poker('fakehost');
      $poker->login('user', 'badpassword');
    } catch (Exception $e) {
      if($e->getCode() == poker::E_LOGIN_FAILED)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_LOGIN_FAILED');
    }
    $this->fail('no exception raised where E_LOGIN_FAILED expected');
  }

  public function test05_login_serial()
  {
    try {
      $poker = new poker('fakehost');
      $poker->login('user', 'missingserial');
    } catch (Exception $e) {
      if($e->getCode() == poker::E_LOGIN_SERIAL)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_LOGIN_SERIAL');
    }
    $this->fail('no exception raised where E_LOGIN_SERIAL expected');
  }

  public function test05_login_unknown()
  {
    try {
      $poker = new poker('fakehost');
      $poker->login('user', 'unknown');
    } catch (Exception $e) {
      if($e->getCode() == poker::E_LOGIN_UNKNOWN)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_LOGIN_UNKNOWN');
    }
    $this->fail('no exception raised where E_LOGIN_UNKNOWN expected');
  }

  public function test06_logout() {
    $poker = new poker('fakehost');
    $poker->logout();
    $this->assertEquals(null, $poker->serial);
    $this->assertEquals(null, $poker->twisted_session);
  }

  public function test07_getPersonalInfo() {
    $poker = new poker('fakehost');
    $poker->login('user', 'password');
    $info = $poker->getPersonalInfo();
    $this->assertEquals('user', $info['name']);

    $poker->client->e_personal_info_answer = TRUE;
    try {
      $info = $poker->getPersonalInfo();
    } catch (Exception $e) {
      if($e->getCode() == poker::E_PERSONAL_INFO_ANSWER)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_PERSONAL_INFO_ANSWER');
    }
    $this->fail('no exception raised where E_PERSONAL_INFO_ANSWER expected');
  }

  public function test08_send_server_error() {
    $poker = new poker('fakehost');
    try {
      $poker->send(array('type' => 'PacketError'));
    } catch (Exception $e) {
      if($e->getCode() == poker::E_SEND_SERVER_ERROR)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_SEND_SERVER_ERROR');
    }
    $this->fail('no exception raised where E_SEND_SERVER_ERROR expected');
  }

  public function test09_auth_handler() {
    $poker = new poker('fakehost');
    $poker->setNoAuthHandler('auth_handler');
    $_GET['name'] = 'user';
    $poker->getPersonalInfo();
    unset($_GET['name']);
    $this->assertEquals(true, isset($GLOBALS['auth_handler_called']));
    $this->assertEquals('user', $GLOBALS['auth_handler_called']['name']);

    $poker->setNoAuthHandler(null);
    try {
      $poker->getPersonalInfo();
    } catch (Exception $e) {
      if($e->getCode() == poker::E_SEND_AUTH_REQUEST)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_SEND_AUTH_REQUEST');
    }
    $this->fail('no exception raised where E_SEND_AUTH_REQUEST expected');
  }

  public function test10_send_fatal_soap_error() {
    $poker = new poker('fakehost');
    try {
      $poker->send(array('type' => 'SoapFault'));
    } catch (Exception $e) {
      if($e->getCode() == poker::E_SEND_FATAL_SOAP_ERROR)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_SEND_FATAL_SOAP_ERROR');
    }
    $this->fail('no exception raised where E_SEND_FATAL_SOAP_ERROR expected');
  }

  public function test11_send_reply_no_type() {
    $poker = new poker('fakehost');
    try {
      $poker->send(array('type' => 'NoType'));
    } catch (Exception $e) {
      if($e->getCode() == poker::E_SEND_REPLY_NO_TYPE)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_SEND_REPLY_NO_TYPE');
    }
    $this->fail('no exception raised where E_SEND_REPLY_NO_TYPE expected');
  }

  public function test12_serial_changed() {
    $poker = new poker('fakehost');
    $poker->setNoAuthHandler('auth_handler');
    $poker->login('user', 'password');
    $this->assertNotEquals(false, $poker->isLoggedIn());
    $_GET['serial'] = 4242;
    $_GET['name'] = 'user';
    $poker->getPersonalInfo();
    unset($_GET['serial']);
    unset($_GET['name']);
    $this->assertEquals(true, isset($GLOBALS['auth_handler_called']));
    $this->assertEquals('user', $GLOBALS['auth_handler_called']['name']);
  }

  public function test13_serial_changed_no_auth_handler() {
    $poker = new poker('fakehost');
    $poker->login('user', 'password');
    try {
      $_GET['serial'] = 4242;
      $poker->getPersonalInfo();
    } catch (Exception $e) {
      unset($_GET['serial']);
      if($e->getCode() == poker::E_SEND_SERIAL_MISMATCH)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_SEND_SERIAL_MISMATCH');
    }
    $this->fail('no exception raised where E_SEND_SERIAL_MISMATCH expected');
  }

  public function test14_not_logged_in() {
    $poker = new poker('fakehost');
    $this->assertEquals(false, $poker->isLoggedIn());
  }

  public function test15_e_image_set() {
    $poker = new poker('fakehost');
    try {
      $poker->getPlayerImage(10);
    } catch (Exception $e) {
      if($e->getCode() == poker::E_IMAGE_SET)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_IMAGE_SET');
    }
    $this->fail('no exception raised where E_IMAGE_SET expected');
  }

  public function test16_e_image_ack() {
    $poker = new poker('fakehost');
    $poker->login('user', 'password');
    $poker->client->e_image_ack = true;
    try {
      $poker->setPlayerImage('../tests/chameleon.png', 'image/png');
    } catch (Exception $e) {
      if($e->getCode() == poker::E_IMAGE_ACK)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_IMAGE_ACK');
    }
    $this->fail('no exception raised where E_IMAGE_ACK expected');
  }

  public function test17_cashIn() {
    $poker = new poker('fakehost');
    $poker->login('user', 'password');
    $poker->cashIn(array('moneyurl', 1000, 'cryptoname', 100), '');
    $this->assertEquals(100, $poker->client->wallets[$poker->serial]);

    try {
      $poker->client->e_cash_in_info_answer = true;
      $poker->cashIn(array('moneyurl', 1001, 'cryptoname', 300), '');
    } catch (Exception $e) {
      if($e->getCode() == poker::E_CASH_IN_INFO_ANSWER)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_CASH_IN_INFO_ANSWER');
    }
    $this->fail('no exception raised where E_CASH_IN_INFO_ANSWER expected');
  }

  public function test18_cashOut() {
    $poker = new poker('fakehost');
    $poker->login('user', 'password');
    $poker->cashOut('moneyurl', 100, '');
    $this->assertEquals(-100, $poker->client->wallets[$poker->serial]);

    try {
      $poker->client->e_cash_out_info_answer = true;
      $poker->cashOut('moneyurl', 100, '');
    } catch (Exception $e) {
      if($e->getCode() == poker::E_CASH_OUT_INFO_ANSWER)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_CASH_OUT_INFO_ANSWER');
    }
    $this->fail('no exception raised where E_CASH_OUT_INFO_ANSWER expected');
  }

  public function test19_cashOutCommit() {
    $poker = new poker('fakehost');
    $poker->login('user', 'password');
    $poker->cashOutCommit('1234');

    try {
      $poker->client->e_cash_out_commit = true;
      $poker->cashOutCommit('1234');
    } catch (Exception $e) {
      if($e->getCode() == poker::E_CASH_OUT_COMMIT)
        return;
      $this->fail('exception code ' . $e->getCode() . ' ' . $e->getMessage() . ' raised instead of expected poker::E_CASH_OUT_COMMIT');
    }
    $this->fail('no exception raised where E_CASH_OUT_COMMIT expected');
  }

  public function test20_get_empty_image() {
    $poker = new poker('fakehost');
    $poker->login('user', 'password');
    $this->assertEquals('', $poker->getPlayerImage($poker->serial));
  }

}

//
// Interpreted by emacs
// Local Variables:
// compile-command: "( cd .. ; ./config.status tests/testpoker.php ) ; ( cd ../tests || cd ../../tests ; make TESTS='testpoker.php' check )"
// End:
?>
