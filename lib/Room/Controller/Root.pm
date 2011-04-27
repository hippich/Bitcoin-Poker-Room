package Room::Controller::Root;
use Moose;
use namespace::autoclean;
use String::Random;

BEGIN { extends 'Catalyst::Controller' }

#
# Sets the actions in this controller to be registered with no prefix
# so they function identically to actions created in MyApp.pm
#
__PACKAGE__->config(namespace => '');

=head1 NAME

Room::Controller::Root - Root Controller for Room

=head1 DESCRIPTION

[enter your description here]

=head1 METHODS

=head2 index

The root page (/)

=cut

sub index :Path :Args(0) {
    my ( $self, $c ) = @_;
}


sub auto :Path {
    my ( $self, $c ) = @_;

    $c->require_ssl;

    if ($c->user) {
      if (!$c->session->{pokernetwork_auth}) {
        my $auth_id_generator = new String::Random;
        $c->session->{pokernetwork_auth} = $auth_id_generator->randregex('[A-Z0-9]{40}');
      }
      
      $c->model("PokerNetwork")->set_user_id_by_auth(
        $c->user->serial,
        $c->session->{pokernetwork_auth}
      );
    }

    1;
}

sub notify :Global {
  my ( $self, $c ) = @_;

  my $players = $c->model("PokerNetwork::Pokertables")->get_column('players');
  my $total = $players->sum;

  if ($total > 0) {
    my $nt = Net::Twitter::Lite->new(
      consumer_key => $c->config->{twitter_consumer_key},
      consumer_secret => $c->config->{twitter_consumer_secret},
      access_token => $c->config->{twitter_access_token},
      access_token_secret => $c->config->{twitter_access_token_secret}
    );

    my $generator = new String::Random;
    my $addon = $generator->randregex('[a-z]{5}');

    my $result = eval { $nt->update($total . ' player(s) sits right now at poker tables at #poker room http://bit.ly/dF1K8h ' . $addon) }; 
  }

  $c->response->body('Done');
}


sub credits :Local {}
sub contactus :Local {}

=head2 default

Standard 404 error page

=cut

sub default :Path {
    my ( $self, $c ) = @_;
    $c->response->body( 'Page not found' );
    $c->response->status(404);
}

=head2 end

Attempt to render a view, if needed.

=cut

sub end : ActionClass('RenderView') {
  my ($self, $c) = @_;
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

__PACKAGE__->meta->make_immutable;

1;
