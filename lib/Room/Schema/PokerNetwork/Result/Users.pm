package Room::Schema::PokerNetwork::Result::Users;

# Created by DBIx::Class::Schema::Loader
# DO NOT MODIFY THE FIRST PART OF THIS FILE

use strict;
use warnings;

use base 'DBIx::Class::Core';

__PACKAGE__->load_components(
  "InflateColumn::DateTime",
  "FrozenColumns",
  "FilterColumn",
  "EncodedColumn",
);

=head1 NAME

Room::Schema::PokerNetwork::Result::Users

=cut

__PACKAGE__->table("users");

=head1 ACCESSORS

=head2 serial

  data_type: 'integer'
  extra: {unsigned => 1}
  is_auto_increment: 1
  is_nullable: 0

=head2 created

  data_type: 'integer'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 name

  data_type: 'varchar'
  is_nullable: 1
  size: 64

=head2 email

  data_type: 'varchar'
  is_nullable: 1
  size: 128

=head2 affiliate

  data_type: 'integer'
  default_value: 0
  extra: {unsigned => 1}
  is_nullable: 1

=head2 skin_url

  data_type: 'varchar'
  default_value: 'random'
  is_nullable: 1
  size: 255

=head2 skin_outfit

  data_type: 'text'
  is_nullable: 1

=head2 skin_image

  data_type: 'text'
  is_nullable: 1

=head2 skin_image_type

  data_type: 'varchar'
  default_value: 'image/png'
  is_nullable: 1
  size: 32

=head2 password

  data_type: 'varchar'
  is_nullable: 1
  size: 512

=head2 privilege

  data_type: 'integer'
  default_value: 1
  is_nullable: 1

=head2 locale

  data_type: 'varchar'
  default_value: 'en_US'
  is_nullable: 1
  size: 32

=head2 rating

  data_type: 'integer'
  default_value: 1000
  is_nullable: 1

=head2 future_rating

  data_type: 'float'
  default_value: 1000
  is_nullable: 1

=head2 games_count

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=head2 data

  data_type: 'text'
  is_nullable: 1

=cut

__PACKAGE__->add_columns(
  "serial",
  {
    data_type => "integer",
    extra => { unsigned => 1 },
    is_auto_increment => 1,
    is_nullable => 0,
  },
  "created",
  { data_type => "integer", extra => { unsigned => 1 }, is_nullable => 0 },
  "name",
  { data_type => "varchar", is_nullable => 1, size => 64 },
  "email",
  { data_type => "varchar", is_nullable => 1, size => 128 },
  "affiliate",
  {
    data_type => "integer",
    default_value => 0,
    extra => { unsigned => 1 },
    is_nullable => 1,
  },
  "skin_url",
  {
    data_type => "varchar",
    default_value => "random",
    is_nullable => 1,
    size => 255,
  },
  "skin_outfit",
  { data_type => "text", is_nullable => 1 },
  "skin_image",
  { data_type => "text", is_nullable => 1 },
  "skin_image_type",
  {
    data_type => "varchar",
    default_value => "image/png",
    is_nullable => 1,
    size => 32,
  },
  "password",
  { data_type => "varchar", is_nullable => 1, size => 512 },
  "privilege",
  { data_type => "integer", default_value => 1, is_nullable => 1 },
  "locale",
  {
    data_type => "varchar",
    default_value => "en_US",
    is_nullable => 1,
    size => 32,
  },
  "rating",
  { data_type => "integer", default_value => 1000, is_nullable => 1 },
  "future_rating",
  { data_type => "float", default_value => 1000, is_nullable => 1 },
  "games_count",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
  "data",
  { data_type => "text", is_nullable => 1 },
);
__PACKAGE__->set_primary_key("serial");
__PACKAGE__->add_unique_constraint("email_idx", ["email"]);


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-09-10 02:25:23
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:najOrRPxquNBM6d34xxy8Q

use JSON::XS;
use Carp;
use Hash::AsObject;
use DateTime;
use Digest::SHA1 qw(sha1_hex);
use Data::Dumper;

__PACKAGE__->add_columns(
    'password' => {
        data_type           => 'VARCHAR',
        size                => 512,
        encode_column       => 1,
        encode_class        => 'Crypt::Eksblowfish::Bcrypt',
        encode_args         => { key_nul => 0, cost => 8 },
        encode_check_method => '_check_password_blowfish',
    },
);

__PACKAGE__->inflate_column(
    'created',
    {
      inflate => sub {
        DateTime->from_epoch(
          epoch => shift
        );
      },
      deflate => sub {
        shift->epoch;
      },
    },
);

__PACKAGE__->add_json_columns(
  data => qw/bitcoin_address bitcoins_received bitcoin_checked request_password hide_gravatar emergency_address/,
);

__PACKAGE__->has_many(
  'balances' => 'Room::Schema::PokerNetwork::Result::User2money',
  { 'foreign.user_serial' => 'self.serial' },
);

__PACKAGE__->has_many(
  'userhands' => 'Room::Schema::PokerNetwork::Result::User2hand',
  { 'foreign.user_serial' => 'self.serial' },
);
__PACKAGE__->many_to_many(
  hands => 'userhands', 'hand'
);

__PACKAGE__->has_many(
  'usertables' => 'Room::Schema::PokerNetwork::Result::User2table',
  { 'foreign.user_serial' => 'self.serial' },
);
__PACKAGE__->many_to_many(
  tables => 'usertables', 'pokertable'
);

__PACKAGE__->has_many(
  'usertourneys' => 'Room::Schema::PokerNetwork::Result::User2tourney',
  { 'foreign.user_serial' => 'self.serial' },
);
__PACKAGE__->many_to_many(
  tourneys => 'usertourneys', 'tourneys'
);

__PACKAGE__->has_many(
  'deposits' => 'Room::Schema::PokerNetwork::Result::Deposits',
  { 'foreign.user_serial' => 'self.serial' },
);

__PACKAGE__->has_many(
  'withdrawals' => 'Room::Schema::PokerNetwork::Result::Withdrawal',
  { 'foreign.user_serial' => 'self.serial' },
);

__PACKAGE__->has_many(
  'bitcoin' => 'Room::Schema::PokerNetwork::Result::User2bitcoin',
  { 'foreign.user_serial' => 'self.serial' },
);


=head2 check_password 

Used for authentication. This function first check hash for BCrypt 
hash and if check fails - tries SHA hash. If both checks fails - 
return false value.

=cut 

sub check_password {
    my ($self, $password) = @_;
    my $result;

    eval {
        $result = $self->_check_password_blowfish($password);
    };

    if (!$result) {
        $result = $self->password eq sha1_hex($password);
    }

    return $result;
}


=head2 get_bitcoin_deposit_address 

Retrieve user's stored bitcoin deposit address.

=cut 
sub get_bitcoin_deposit_address {
  my ($self) = @_;

  return $self->data->bitcoin_address;
}


=head2 balance 

Retrieve single currency balance Result object.

Set $update to 1 in order to get SELECT .. FOR UPDATE 
SQL query (to lock row).

=cut
sub balance {
    my ($self, $serial, $update) = @_;

    return 
        ($update)
        ? $self->balances->find_or_create({ currency_serial => $serial }, { for => 'update' })
        : $self->balances->find_or_create({ currency_serial => $serial });
}


=head2 bitcoin_balance 

Retrieve single currency current bitcoin balance Result object.

Set $update to 1 in order to get SELECT .. FOR UPDATE 
SQL query (to lock row).

=cut
sub bitcoin_balance {
    my ($self, $serial, $update) = @_;

    return 
        ($update)
        ? $self->bitcoin->find_or_create({ currency_serial => $serial }, { for => 'update' })
        : $self->bitcoin->find_or_create({ currency_serial => $serial });
}


=head2 deposit_bitcoin 

Update user's balance. It do the following:
- Start transaction.
- SELECT ... FOR UPDATE user2money Result object (with locking).
- SELECT ... FOR UPDATE user2bitcoin Result object (with locking).
- If bitcoin address do not exists - call callback to get new address.
- Call $new_balance_cb callback 
- Compare $new_balance_cb result to $user2bitcoin->amount and add $difference 
to $user2money->amount.
- If $difference > 0 - add new record to Deposits.
- Commit transaction.

=cut
sub deposit_bitcoin {
    my ($self, $currency, $new_balance_cb, $new_address_cb) = @_;

    croak("new_balance_cb callback is not defined.") unless $new_balance_cb;
    croak("new_address_cb callback is not defined.") unless $new_address_cb;
    croak("currency is not defined.") unless $currency;

    my $serial = $currency->serial;
    my $schema = $self->result_source->schema;

    $schema->txn_do(sub {
        my $current = $self->balance($serial, 1);
        my $bitcoin = $self->bitcoin_balance( $serial, 1 );

        if (! $bitcoin->address) {
            $bitcoin->address( &$new_address_cb ); 
            $bitcoin->update;
        }

        my $new_balance = &$new_balance_cb( $bitcoin );
        my $current_balance = $bitcoin->amount || 0;

        my $difference = $new_balance - $current_balance;

        if ($difference > 0) {
            $bitcoin->amount($new_balance);
            $bitcoin->update;

            $current->amount( 
                $current->amount + $difference * $currency->rate * 100
            );
            $current->update;

            $self->deposits->create({
              currency_serial => $serial,
              amount => $difference,
              processed => 1,
              info => $bitcoin->address,
              created_at => DateTime->now,
              processed_at => DateTime->now,
            });
        }

    });
}


=head2 withdraw_bitcoin 

Transactional bitcoin withdrawal. Similar to deposit_bitcoin.

$serial - currency serial 
$amount - amount to withdraw 
$withdraw_cb - callback function to do actual bitcoin withdrawal.

=cut 
sub withdraw_bitcoin {
    my ($self, $currency, $amount, $withdraw_cb) = @_;

    croak("withdraw_cb callback is not defined.") unless $withdraw_cb;
    croak("amount is not defined.") unless $amount > 0;
    croak("currency is not defined.") unless $currency;

    my $serial = $currency->serial;
    my $schema = $self->result_source->schema;
    my $adj_amount = $amount * $currency->rate * 100;

    $schema->txn_do(sub {
        my $current = $self->balance($serial, 1);
        croak("Not enough funds available.") unless $current->amount >= $adj_amount;

        # Remove $amount from user's balance 
        $current->amount(
          $current->amount() - $adj_amount
        );
        $current->update();

        # Create withdrawal record for tracking purposes.
        my $withdrawal = $self->withdrawals->create({
          currency_serial => $serial,
          amount => $amount,
          created_at => DateTime->now,
          processed => 0,
          info => "",
          processed_at => "",
        });

        my ($result, $error) = &$withdraw_cb($withdrawal);

        $withdrawal->info(
            "Result: ". $result ."\n\nError: ". Dumper($error)
        );

        if (! $error) {
          # Mark as processed if successful
          $withdrawal->processed_at( DateTime->now() );
          $withdrawal->processed(1);
        }

        $withdrawal->update();
    });
}


=head1 AUTHOR

Pavel Karoukin

=head1 LICENSE

Copyright (C) 2010 Pavel A. Karoukin <pavel@yepcorp.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

=cut

1;
