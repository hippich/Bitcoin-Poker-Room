use strict;
use warnings;
use Test::More;

BEGIN { use_ok 'Catalyst::Test', 'Room' }
BEGIN { use_ok 'Room::Controller::Admin::Tourneys' }

ok( !request('/admin/tourneys')->is_success, 'Request should not succeed for anonymous user.' );
done_testing();
