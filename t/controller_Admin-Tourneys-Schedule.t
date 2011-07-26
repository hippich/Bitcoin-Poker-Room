use strict;
use warnings;
use Test::More;

BEGIN { use_ok 'Catalyst::Test', 'Room' }
BEGIN { use_ok 'Room::Controller::Admin::Tourneys::Schedule' }

ok( !request('/admin/tourneys/schedule')->is_success, 'Request should not succeed for anonymous user.' );
done_testing();
