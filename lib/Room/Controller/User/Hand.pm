package Room::Controller::User::Hand;
use Moose;
use namespace::autoclean;

BEGIN {extends 'Catalyst::Controller'; }

=head1 NAME

Room::Controller::User::Hand - Catalyst Controller

=head1 DESCRIPTION

Catalyst Controller.

=head1 METHODS

=cut


sub base : Chained PathPart('user/hands') CaptureArgs(0) {
  my ($self, $c) = @_;

  if (!$c->user) {
    $c->res->redirect(
      $c->uri_for('/user/login', '', {'destination' => $c->action,})
    );
  }

  $c->stash->{user} = $c->user;
}

=head2 index

=cut

sub index : Chained('base') PathPart('') Args(0) {
  my ( $self, $c ) = @_;
  my $page = $c->req->params->{'page'};
  $page = 1 if $page < 1;

  $c->stash->{hands} = $c->user->hands->search(undef, {
      rows => 50,
      page => $page,
      order_by => {
        -desc => 'serial',
      },
  });
}

sub view_hand : Chained('base') PathPart('') Args(1) {
  my ($self, $c, $id) = @_;

  $c->stash->{hands} = $c->user->hands;
  my $hand = $c->stash->{hands}->search({serial => $id})->first;

  if (! $hand && $c->user->privilege == 2) {
    $hand = $c->model('PokerNetwork::Hands')->search({serial => $id})->first;
  }

  if (! $hand) {
    $c->detach('/default');
  }

  $c->stash->{hand} = $hand->get_parsed_history;
}


=head1 AUTHOR

Pavel Karoukin

=head1 LICENSE

This library is free software. You can redistribute it and/or modify
it under the same terms as Perl itself.

=cut

__PACKAGE__->meta->make_immutable;

1;