use strict;
use warnings;
use Test::More;

BEGIN { use_ok 'Catalyst::Test', 'Room' }
BEGIN { use_ok 'Room::Controller::Pages' }

Room->config->{require_ssl}->{disabled} = 1;

ok( request('/pages/about_us')->is_success, 'Request to About Us page should succeed.' );
ok( !request('/pages')->is_success, 'Request to index page should NOT succeed.' );
ok( !request('/pages/NOTEXISTS')->is_success, 'Request to non-existing page should NOT succeed.' );
ok( !request('/pages/../../../room_sample.conf')->is_success, 'Request to random files should NOT succeed.' );

done_testing();
