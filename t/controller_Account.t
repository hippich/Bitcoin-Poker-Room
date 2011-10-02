use strict;
use warnings;
use Test::More;

BEGIN { use_ok 'Catalyst::Test', 'Room' }
BEGIN { use_ok 'Room::Controller::Account' }

ok( request('/account')->is_redirect, 'Request to /acccount should succeed' );
ok( request('/account/login')->is_success, 'Request to /acccount/login should succeed' );
ok( request('/account/register')->is_success, 'Request to /acccount/register should succeed' );
ok( request('/account/forgot_password')->is_success, 'Request to /acccount/forgot_password should succeed' );
ok( request('/account/no_avatar/1')->is_redirect, 'Request to /acccount/no_avatar/1 should succeed' );
done_testing();
