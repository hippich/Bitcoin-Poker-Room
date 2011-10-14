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

=head2 amount

  data_type: 'decimal'
  default_value: 0.00000000
  extra: {unsigned => 1}
  is_nullable: 0
  size: [52,8]

=head2 address

  data_type: 'varchar'
  default_value: (empty string)
  is_nullable: 0
  size: 40

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
  "amount",
  {
    data_type => "decimal",
    default_value => "0.00000000",
    extra => { unsigned => 1 },
    is_nullable => 0,
    size => [52, 8],
  },
  "address",
  { data_type => "varchar", default_value => "", is_nullable => 0, size => 40 },
);
__PACKAGE__->set_primary_key("serial");


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-10-05 01:21:04
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:YiVc6DGajsbDuaO6LyCfDQ


__PACKAGE__->belongs_to(
  user => 'Room::Schema::PokerNetwork::Result::Users',
  { serial => 'user_serial' }
);



1;
