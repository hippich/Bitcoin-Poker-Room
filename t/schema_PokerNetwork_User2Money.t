use strict;
use warnings;
use Test::More;
use Test::DBIx::Class;

fixtures_ok "basic", "DB fixtures loaded.";

ok my $user = Users->find({ email => 'admin@test.com' })
    => 'Fetch admin user object.';

is $user->name, 'admin', 'This is admin.';

ok my $balance = $user->balance(1);

is $balance->amount, 10000, "Amount should be 10000";
is $balance->rake, 100, "Rake should be 100";
is $balance->points, 20, "Points should be 20";

ok !$balance->points_cashout(40), "Should not be able to cash out 40 points";
ok !$balance->points_cashout(-40), "Should not be able to cash out negative amount of points";
ok $balance->points_cashout(15), "Cash out 15 bonus points";

is $balance->points_cashed, 15, "Cashed points should be equal 15";

is $balance->amount, 10015, "Amount should be equal to 10015 after points cash out";
is $balance->points, 5, "There should be left 5 points";

done_testing();


