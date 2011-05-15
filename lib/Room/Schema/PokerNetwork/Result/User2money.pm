package Room::Schema::PokerNetwork::Result::User2money;

use strict;
use warnings;

use base 'DBIx::Class';

__PACKAGE__->load_components(
  "InflateColumn::DateTime",
  "FrozenColumns",
  "FilterColumn",
  "EncodedColumn",
  "Core",
);
__PACKAGE__->table("user2money");
__PACKAGE__->add_columns(
  "user_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "currency_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "amount",
  { data_type => "BIGINT", default_value => undef, is_nullable => 0, size => 20 },
  "rake",
  { data_type => "BIGINT", default_value => 0, is_nullable => 0, size => 20 },
  "points",
  { data_type => "BIGINT", default_value => 0, is_nullable => 0, size => 20 },
);
__PACKAGE__->set_primary_key("user_serial", "currency_serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-09-27 11:47:31
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:Cpd8s2D1DR39dA36MZK7NQ


__PACKAGE__->filter_column(
  amount => {
    filter_to_storage => '__filter_multi',
    filter_from_storage =>  '__filter_divide',
  }
);


__PACKAGE__->filter_column(
  rake => {
    filter_to_storage => '__filter_multi',
    filter_from_storage =>  '__filter_divide',
  }
);


sub __filter_multi { my $self = shift; shift() * 10000 }
sub __filter_divide { my $self = shift; shift() / 10000 }

__PACKAGE__->has_one(
  'currency' => 'Room::Schema::PokerNetwork::Result::Currencies',
  { 'foreign.serial' => 'self.currency_serial' },
);



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
