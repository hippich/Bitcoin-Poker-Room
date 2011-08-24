use strict;
use warnings;
use Test::More;
use Test::DBIx::Class;

fixtures_ok "basic", "Tourneys fixtures loaded.";

ok my $user = Users->find({ email => 'admin@test.com' })
    => 'Fetch admin user object.';

# Store hash directly in column data to prevent EncodedColumn hashing 
# this value again. This us SHA-1 hash of 'admin' word.
$user->{_column_data}{password} = 'd033e22ae348aeb5660fc2140aec35850c4da997';
$user->{_dirty_column}{password} = 1;
$user->update();

is $user->name, 'admin', 'This is admin.';

# Test migration to Bcrypt
ok $user->check_password('admin')
    => "Initial password 'admin' should be recognized via SHA-1 hash.";

my $hash = $user->password;
$user->password('zed');
$user->update();
my $new_hash = $user->password;
isnt $hash, $new_hash, "Old and new hashes should be different.";

ok $user->check_password('zed')
    => "New password 'admin' should be recognized via Bcrypt hash.";

done_testing();

