use strict;
use warnings;
use Test::More;
use Test::DBIx::Class;

fixtures_ok {
    Users => [
        [ 'serial', 'name', 'email', 'password', 'privilege', 'created' ],
        [ 22, 'admin', 'admin@test.com', 'd033e22ae348aeb5660fc2140aec35850c4da997', 1, 0 ],
        [ 23, 'test', 'test@test.com', 'd033e22ae348aeb5660fc2140aec35850c4da997', 1, 0 ],
    ],

    Pokertables => [
        [ 'serial', 'seats', 'currency_serial', 'name', 'variant', 'betting_structure', 'skin', 'tourney_serial' ],
        [ 8251, 10, 0, 'tourney table', 'holdem', 'level-001', 'default', 2071 ],
    ],

    Tourneys => [
        [ 'serial' ],
        [ 2071 ],
    ],
    
    User2table => [
        [ 'user_serial', 'table_serial', 'money', 'bet' ],
        [ 22, 8251, 132000, 0 ],
        [ 23, 8251, 10000, 0 ], 
    ],

    User2tourney => [
        [ 'user_serial', 'currency_serial', 'tourney_serial', 'table_serial', 'rank' ],
        [ 22, 1, 2071, 8251, 1 ],
        [ 23, 1, 2071, 8251, 2 ], 
    ]
}, "Installed tourneys fixtures";

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

