package Room::Schema::PokerNetwork::Result::Hands;

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

Room::Schema::PokerNetwork::Result::Hands

=cut

__PACKAGE__->table("hands");

=head1 ACCESSORS

=head2 serial

  data_type: 'integer'
  extra: {unsigned => 1}
  is_auto_increment: 1
  is_nullable: 0

=head2 created

  data_type: 'timestamp'
  datetime_undef_if_invalid: 1
  default_value: current_timestamp
  is_nullable: 0

=head2 name

  data_type: 'varchar'
  is_nullable: 1
  size: 32

=head2 description

  data_type: 'text'
  is_nullable: 0

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
  {
    data_type => "timestamp",
    datetime_undef_if_invalid => 1,
    default_value => \"current_timestamp",
    is_nullable => 0,
  },
  "name",
  { data_type => "varchar", is_nullable => 1, size => 32 },
  "description",
  { data_type => "text", is_nullable => 0 },
);
__PACKAGE__->set_primary_key("serial");


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-09-10 02:29:51
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:fKv0lpei09x0D8c7tJPTyg

use JSON::XS;
use Switch;

our @poker_cards_string = ( '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', 'Th', 'Jh', 'Qh', 'Kh', 'Ah', '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd', 'Ad', '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c', 'Tc', 'Jc', 'Qc', 'Kc', 'Ac', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks', 'As' );

__PACKAGE__->has_many(
  'userhands' => 'Room::Schema::PokerNetwork::Result::User2hand',
  { 'foreign.hand_serial' => 'self.serial' },
);
__PACKAGE__->many_to_many(
  users => 'userhands', 'user'
);

sub get_amounts {
  my ($self, $serial) = @_;

  my ($totals_string) = $self->description =~ /'total': {([^}]+)}/;
  my ($shares_string) = $self->description =~ /'serial2share': {([^}]+)}/;

  # Sometimes Python adds L to integers
  $totals_string =~ s/(\d+)L/$1/g;
  $shares_string =~ s/(\d+)L/$1/g;

  my ($total) = $totals_string =~ /$serial: ([\.\d]+)/;
  my ($share) = $shares_string =~ /$serial: ([\.\d]+)/;

  $share = $share || 0;
  $total = $total || 0;

  return {total => $total, share => $share};
}

sub get_parsed_history {

    my $self = shift;
    my ($parsed_history, @players, %players_by_id);

    my $h = $self->__parse_hands();

    my ($handstate, @flop, @turn, @river, $showdown, $rakeindex);
    my %rounds = ( 'pre-flop' => 0, 'flop' => 1, 'turn' => 2, 'river' => 3 ); 

    for(my $y = 0; $y < @{$h}; $y = $y + 1) {
        my $x = $h->[$y];

        if($x->[0] eq "round") {
          $handstate = $x->[1];
        }

        # Save the showdown.  This only exists if state ne 'river'
        if($x->[0] eq "showdown") {
          $showdown = $x->[1];

          @flop = @{$showdown}[0..2];
          @turn = @{$showdown}[0..3];
          @river = @{$showdown}[0..4];
        }

        if($x->[0] eq "rake") {
            $rakeindex = $y;
        }
    }

    my @flopblob = ('round','flop',\@flop);
    my @turnblob = ('round','turn',\@turn);
    my @riverblob = ('round','river',\@river);

    splice(@{$h}, $rakeindex, 0, \@riverblob) unless $rounds{ $handstate } > 2;
    splice(@{$h}, $rakeindex, 0, \@turnblob) unless $rounds{ $handstate } > 1;
    splice(@{$h}, $rakeindex, 0, \@flopblob) unless $rounds{ $handstate } > 0;

    $parsed_history->{game_history} = $h;
    $parsed_history->{self} = $self;

    foreach my $uid (@{$h->[0]->[7]}) {
        my $player = $self->result_source->schema->resultset("Users")->find($uid);
        push @players, $player;

        if (! $player) {
            $player = $self->result_source->schema->resultset("Users")->new({
                serial => $uid,
                name => 'Anonymous',
            });
        }

        $players_by_id{$player->serial} = $player;
    }

    $parsed_history->{players} = \@players;
    $parsed_history->{players_by_id} = \%players_by_id;
    return $parsed_history;
}


sub __parse_hands {
  my $self = shift;
  my $history = $self->description;

  $history =~ s/PokerCards\(\[([^\]]*)\]\)/$self->__parse_cards($1)/ge;
  $history =~ s/Decimal\('([^\']+)'\)/$1/g;

  $history =~ s/None/null/g;
  $history =~ s/True/1/g;
  $history =~ s/False/0/g;

  $history =~ s/(\d+)L/$1/g;

  $history =~ s/^\[\(/[[/;
  $history =~ s/\)\]/]]/;
  $history =~ s/\), \(/], [/g;
  $history =~ s/'/"/g;

  $history =~ s/(\d+): /"$1": /g;

  return decode_json $history;
}

sub __parse_cards {
  my ($self, $cards_str) = @_;
  my @cards = split /, /, $cards_str;

  foreach my $card (@cards) {
    $card = '"'. $poker_cards_string[$card & 0x3F] . '"';
  }

  return '['. (join ', ', @cards) .']';
}


sub format_hi_hand {
  my $self = shift;
  my $hand = shift;

  if ($hand) {
    my $best = shift @{$hand};
    foreach my $card (@{$hand}) {
      $card = $poker_cards_string[$card & 0x3F];
    }

    switch ($best) {
      case 'NoPair' { $best = 'High card'; }
      case 'OnePair' { $best = 'One pair'; }
      case 'TwoPair' { $best = 'Two pairs'; }
      case 'Trips' { $best = 'Three of a kind'; }
      case 'Straight' { $best = 'Straight'; }
      case 'Flush' { $best = 'Flush'; }
      case 'FlHouse' { $best = 'Full House'; }
      case 'Quads' { $best = 'Four of a kind'; }
      case 'StFlush' { $best = 'Straight flush'; }
    }

    return { best => $best, cards => $hand }
  }
  else {
    return;
  }
}


sub get_all_players {
  my $self = shift;
  my @players;
  my $users = $self->users;
  while (my $user = $users->next) {
    push @players, $user->name;
  }
  return \@players;
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
