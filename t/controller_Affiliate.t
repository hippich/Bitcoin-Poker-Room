use strict;
use warnings;
use Test::More;


use Catalyst::Test 'Room';
use Room::Controller::Affiliate;

ok( request('/affiliate')->is_success, 'Request should succeed' );
done_testing();
