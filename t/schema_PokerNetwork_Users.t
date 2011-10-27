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

ok my $currency = Currencies->find({ id => 'bitcoin' })
    => "Currency with serial=1 loaded.";

### Test depositing
#
# Empty address returned test 
$user->deposit_bitcoin($currency, sub {
        return 0;
    }, sub {
        return;
    }
);

ok $user->bitcoin_balance(1)->address eq "", "Address should be empty.";

$user->deposit_bitcoin($currency, sub {
        return 0;
    }, sub {
        return "12345";
    }
);

ok $user->bitcoin_balance(1)->address ne "", "Address should NOT be empty.";

# Test deposit procedure
$user->deposit_bitcoin($currency, sub {
        my $bitcoin = shift;
        return 1;
    }, sub {
        return "12345";
    }
);

ok $user->balance(1)->amount == 20000
    => "new_balance(1,1) call should add 100 to user's balance(1)";

$user->deposit_bitcoin($currency, sub {
        my $bitcoin = shift;
        return 2;
    }, sub {
        return "12345";
    }
);

ok $user->balance(1)->amount == 30000
    => "new_balance(1,2) call should add 100 to user's balance(1)";

ok $user->bitcoin_balance(1)->address eq '12345'
    => "bitcoin deposit address should equal to '12345' (returned ". $user->bitcoin_balance(1)->address .")";


### Test withdrawals
$user->withdraw_bitcoin(
    $currency,
    0.5,
    sub {
        return ('', ''); 
    }
);

ok $user->balance(1)->amount == 25000
    => "new balance should be equal to 25000";

done_testing();

