package Room::Schema::PokerNetwork::Result::User2money;

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

Room::Schema::PokerNetwork::Result::User2money

=cut

__PACKAGE__->table("user2money");

=head1 ACCESSORS

=head2 user_serial

  data_type: 'integer'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 currency_serial

  data_type: 'integer'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 amount

  data_type: 'bigint'
  is_nullable: 0

=head2 rake

  data_type: 'bigint'
  default_value: 0
  is_nullable: 0

=head2 points

  data_type: 'decimal'
  default_value: 0.0000
  is_nullable: 0
  size: [64,4]

=head2 points_cashed

  data_type: 'decimal'
  default_value: 0.0000
  is_nullable: 0
  size: [64,4]

=cut

__PACKAGE__->add_columns(
  "user_serial",
  { data_type => "integer", extra => { unsigned => 1 }, is_nullable => 0 },
  "currency_serial",
  { data_type => "integer", extra => { unsigned => 1 }, is_nullable => 0 },
  "amount",
  { data_type => "bigint", is_nullable => 0 },
  "rake",
  { data_type => "bigint", default_value => 0, is_nullable => 0 },
  "points",
  {
    data_type => "decimal",
    default_value => "0.0000",
    is_nullable => 0,
    size => [64, 4],
  },
  "points_cashed",
  {
    data_type => "decimal",
    default_value => "0.0000",
    is_nullable => 0,
    size => [64, 4],
  },
);
__PACKAGE__->set_primary_key("user_serial", "currency_serial");


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-09-10 02:25:23
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:TR1tCNvK+k72YfcPIF03Aw


__PACKAGE__->has_one(
  'currency' => 'Room::Schema::PokerNetwork::Result::Currencies',
  { 'foreign.serial' => 'self.currency_serial' },
);


=head2 points_cashout 

Move points to available amount 

=cut 
sub points_cashout {
    my ($self, $amount) = @_;

    if ($self->points < $amount || $amount <= 0) {
        return 0;
    }

    $self->amount( $self->amount + $amount );
    $self->points( $self->points - $amount );
    $self->points_cashed( $self->points_cashed + $amount );

    $self->update();

    return 1;
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
