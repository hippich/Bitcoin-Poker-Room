use strict;
use warnings;
use Test::More;
use Test::DBIx::Class;

fixtures_ok "tourneys", "Tourneys fixtures loaded.";

ok my $user = Users->find({ email => 'admin@test.com' }), 'Fetch admin user object.';

is $user->name, 'admin', 'This is admin.';

ok my $user_at_table = Pokertables->find(8251)->users->find(22), "Should be able to find this user.";

is $user->serial, $user_at_table->serial, "Current users, and found user at the table should have same serial.";

ok my $tourney = Tourneys->find(2071), "Load tourney.";

is $tourney->get_users_registered, 2, "2 players should be registered by now.";

is $tourney->get_table_serial(22), 8251, "Should return table_serial #8251 for user #22.";
is $tourney->get_table_serial(300), 8251, "Should return table_serial #8251 for not sitting user.";
is $tourney->get_table_serial, 8251, "Should return table_serial #8251 for not logged in user.";

ok $tourney->is_user_registered(22), "Should return true.";
ok ! $tourney->is_user_registered(300), "Should return false.";

done_testing();

