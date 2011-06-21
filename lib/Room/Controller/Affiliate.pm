package Room::Controller::Affiliate;
use Moose;
use namespace::autoclean;

BEGIN {extends 'Catalyst::Controller'; }

=head1 NAME

Room::Controller::Affiliate - Catalyst Controller

=head1 DESCRIPTION

Catalyst Controller.

=head1 METHODS

=cut

=head2 base

Affiliate actions take the form /affiliate/<id>/<key>/action...

base authenticates the affiliate and adds the result to the stash (or rejects invalid authentication)

=cut

sub base :Chained('/') :PathPart('affiliate') :CaptureArgs(2) {
  my ( $self, $c, $affiliate_serial, $affiliate_key, $username ) = @_;

  my $affiliate = $c->model("PokerNetwork::Affiliates")->find($affiliate_serial);
  if ($affiliate->key != $affiliate_key) {
    $c->response->body('nope');
    $c->detach();
  }

  $c->stash(affiliate => $affiliate)
}

=head2 auth_user

Authenticate a federated user to the poker network, creating their user object if necessary.

=cut

sub auth_user :Chained('base') :PathPart('auth_user') :Args(1) {
  my ( $self, $c, $username ) = @_;

  my $affiliate_serial = $c->stash->{affiliate}->serial;

  my $user = $c->model("PokerNetwork::Users")->affiliate_username($affiliate_serial, $username)->first();

  if (!$user) {
    $user = $c->model("PokerNetwork::Users")->new({
        name => $username,
        affiliate => $affiliate_serial,
        created => DateTime->now,
        });

    $user->insert();
  }

  my $auth_id_generator = new String::Random;
  my $auth = $auth_id_generator->randregex('[A-Z0-9]{40}');

  $c->model("PokerNetwork")->set_user_id_by_auth(
      $user->serial,
      $auth
      );

  $c->response->body('&auth=' . $auth . '&uid=' . $user->serial);
}

=head1 AUTHOR

Isis,,,

=head1 LICENSE

This library is free software. You can redistribute it and/or modify
it under the same terms as Perl itself.

=cut

__PACKAGE__->meta->make_immutable;

1;
