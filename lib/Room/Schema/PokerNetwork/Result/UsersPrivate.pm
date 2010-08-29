package Room::Schema::PokerNetwork::Result::UsersPrivate;

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
__PACKAGE__->table("users_private");
__PACKAGE__->add_columns(
  "serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "firstname",
  { data_type => "VARCHAR", default_value => "", is_nullable => 1, size => 255 },
  "lastname",
  { data_type => "VARCHAR", default_value => "", is_nullable => 1, size => 255 },
  "addr_street",
  { data_type => "VARCHAR", default_value => "", is_nullable => 1, size => 255 },
  "addr_street2",
  { data_type => "VARCHAR", default_value => "", is_nullable => 1, size => 255 },
  "addr_zip",
  { data_type => "VARCHAR", default_value => "", is_nullable => 1, size => 64 },
  "addr_town",
  { data_type => "VARCHAR", default_value => "", is_nullable => 1, size => 64 },
  "addr_state",
  { data_type => "VARCHAR", default_value => "", is_nullable => 1, size => 128 },
  "addr_country",
  { data_type => "VARCHAR", default_value => "", is_nullable => 1, size => 64 },
  "phone",
  { data_type => "VARCHAR", default_value => "", is_nullable => 1, size => 64 },
  "gender",
  { data_type => "CHAR", default_value => "", is_nullable => 1, size => 1 },
  "birthdate",
  { data_type => "DATE", default_value => undef, is_nullable => 1, size => 10 },
  "verified",
  { data_type => "CHAR", default_value => "n", is_nullable => 1, size => 1 },
  "verified_time",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
);
__PACKAGE__->set_primary_key("serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-27 00:26:16
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:/crhOJSGyKcZ/LHuziDjNA


# You can replace this text with custom content, and it will be preserved on regeneration
1;
