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
    
    if (! $c->user) {
      push @{$c->flash->{messages}}, "Please, login or create new user account.";
      $c->res->redirect(
        $c->uri_for('/user/login')
      );
      
      return;
    }

    $c->res->redirect(
      $c->uri_for('/tables')
    );
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

This library is free software. You can redistribute it and/or modify
it under the same terms as Perl itself.

=cut

__PACKAGE__->meta->make_immutable;

1;
