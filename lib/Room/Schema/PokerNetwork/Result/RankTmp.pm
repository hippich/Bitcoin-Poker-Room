package Room::Schema::PokerNetwork::Result::RankTmp;

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
__PACKAGE__->table("rank_tmp");
__PACKAGE__->add_columns(
  "user_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "currency_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "amount",
  { data_type => "BIGINT", default_value => undef, is_nullable => 0, size => 20 },
  "rank",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "percentile",
  { data_type => "TINYINT", default_value => 0, is_nullable => 0, size => 3 },
);
__PACKAGE__->set_primary_key("user_serial", "currency_serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-27 00:26:16
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:ebZHdrlfB0OrEuYaomHPcQ


# You can replace this text with custom content, and it will be preserved on regeneration

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
