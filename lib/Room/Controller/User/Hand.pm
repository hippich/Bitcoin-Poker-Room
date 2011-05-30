package Room::Controller::User::Hand;
use Moose;
use namespace::autoclean;
use JSON::XS;

BEGIN {extends 'Catalyst::Controller'; }

=head1 NAME

Room::Controller::User::Hand - Catalyst Controller

=head1 DESCRIPTION

Catalyst Controller.

=head1 METHODS

=cut

our @poker_cards_string = ( '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', 'Th', 'Jh', 'Qh', 'Kh', 'Ah', '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd', 'Ax', '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c', 'Tc', 'Jc', 'Qc', 'Kc', 'Ac', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks', 'As' );

sub base : Chained PathPart('user/hands') CaptureArgs(0) {
  my ($self, $c) = @_;

  if (!$c->user) {
    $c->res->redirect(
      $c->uri_for('/user/login', '', {'destination' => $c->action,})
    );
  }

  use Data::Dumper;
  $c->stash->{hands} = $c->user->hands;
  $c->stash->{dumper} = \&Dumper;
  $c->stash->{parser} = sub {$self->__parse_hands(shift); };
}

=head2 index

=cut

sub index : Chained('base') PathPart('') Args(0) {
    my ( $self, $c ) = @_;
}


sub view_hand : Chained('base') PathPart('') Args(1) {
  my ($self, $c, $id) = @_;

  my $hand_raw = $c->stash->{hands}->search({serial => $id})->first->description; 

  use Data::Dumper;
  $c->stash->{hand} = Dumper($self->__parse_hands($hand_raw));
}

sub __parse_hands {
  my ($self, $history) = @_;

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

=head1 AUTHOR

Pavel Karoukin

=head1 LICENSE

This library is free software. You can redistribute it and/or modify
it under the same terms as Perl itself.

=cut

__PACKAGE__->meta->make_immutable;

1;
