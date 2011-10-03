package Room::Schema::PokerNetwork::Result::User2bitcoin;

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

Room::Schema::PokerNetwork::Result::User2bitcoin

=cut

__PACKAGE__->table("user2bitcoin");

=head1 ACCESSORS

=head2 serial

  data_type: 'bigint'
  extra: {unsigned => 1}
  is_auto_increment: 1
  is_nullable: 0

=head2 user_serial

  data_type: 'bigint'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 currency_serial

  data_type: 'bigint'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 balance

  data_type: 'decimal'
  extra: {unsigned => 1}
  is_nullable: 0
  size: [52,8]

=cut

__PACKAGE__->add_columns(
  "serial",
  {
    data_type => "bigint",
    extra => { unsigned => 1 },
    is_auto_increment => 1,
    is_nullable => 0,
  },
  "user_serial",
  { data_type => "bigint", extra => { unsigned => 1 }, is_nullable => 0 },
  "currency_serial",
  { data_type => "bigint", extra => { unsigned => 1 }, is_nullable => 0 },
  "balance",
  {
    data_type => "decimal",
    extra => { unsigned => 1 },
    is_nullable => 0,
    size => [52, 8],
  },
);
__PACKAGE__->set_primary_key("serial");


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-10-02 23:19:36
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:4qNGWTkA2JaZbr/rJ1KrOQ


# You can replace this text with custom code or comments, and it will be preserved on regeneration
1;
