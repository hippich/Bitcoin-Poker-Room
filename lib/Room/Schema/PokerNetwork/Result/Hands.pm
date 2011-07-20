package Room::Schema::PokerNetwork::Result::Hands;

use strict;
use warnings;

use base 'DBIx::Class';
use Data::Dumper;

__PACKAGE__->load_components(
  "InflateColumn::DateTime",
  "FrozenColumns",
  "FilterColumn",
  "EncodedColumn",
  "Core",
);
__PACKAGE__->table("hands");
__PACKAGE__->add_columns(
  "serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "created",
  {
    data_type => "TIMESTAMP",
    default_value => "CURRENT_TIMESTAMP",
    is_nullable => 0,
    size => 14,
  },
  "name",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 32,
  },
  "description",
  {
    data_type => "TEXT",
    default_value => undef,
    is_nullable => 0,
    size => 65535,
  },
);
__PACKAGE__->set_primary_key("serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-09-27 11:47:31
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:1ToKcdFljUDL2gZ5bKoYSg

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

  $share = 0 unless $share > 0;

  return {total => $total, share => $share};
}

sub get_parsed_history {
  my $self = shift;
  my $parsed_history;
  my @players;
  my %players_by_id;

  my $h = $self->__parse_hands();

  ## state of the hand history
  ## flop = 1
  ## turn = 2
  ## river = 3

  my $handstate = -1;
  my @flop;
  my @turn;
  my @river;
  my $showdown;
  my $rakeindex;

  for(my $y = 0; $y < @{$h}; $y = $y + 1)
  {
	my $x = $h->[$y];
	if($x->[0] eq "round")
	{
		switch($x->[1])
		{
			# store the flop so we can recreate turn and river
			case 'flop' 	{ if($handstate < 1) { $handstate = 1; } }
			case 'turn' 	{ if($handstate < 2) { $handstate = 2; } }
			case 'river' 	{ if($handstate < 3) { $handstate = 3; } }
		}
	}
	# Save the showdown.  This only exists if state != 3
	if($x->[0] eq "showdown")
	{
		
		$showdown = $x->[1];
		@flop 	= ($showdown->[0],$showdown->[1],$showdown->[2]);
		if($handstate != 3)
		{
			@turn 	= ($showdown->[0],$showdown->[1],$showdown->[2],$showdown->[3]);
			@river	= ($showdown->[0],$showdown->[1],$showdown->[2],$showdown->[3],$showdown->[4]);
		}
	}

	if($x->[0] eq "rake")
	{
		$rakeindex = $y;
	}
  }

  my @turnblob = ('round','turn',\@turn);
  my @riverblob = ('round','river',\@river);

  if($handstate == 2)
  {
  	splice(@{$h},$rakeindex, 0, @riverblob);
  }

  if($handstate == 1)
  {
  	splice(@{$h},$rakeindex , 0, \@turnblob );
  	splice(@{$h},$rakeindex + 1, 0, \@riverblob);
  }

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

sub println { local $,=""; print +( @_ ? @_ : $_ ), "\n\n" }

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
