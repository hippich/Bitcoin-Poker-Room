use strict;
use warnings;
use Test::More;

BEGIN { use_ok 'Catalyst::Test', 'Room' }
BEGIN { use_ok 'Room::Controller::Tourneys' }

ok( request('/tourneys')->is_success, 'Request should succeed' );
done_testing();
