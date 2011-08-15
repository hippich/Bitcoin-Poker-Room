package Room::Controller::Root;
use Moose;
use namespace::autoclean;
use String::Random;
use URI::Escape qw(uri_escape);
use Digest::MD5 qw(md5_hex);

BEGIN { extends 'Catalyst::Controller::HTML::FormFu'; }

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
    my $tables_rs = $c->model("PokerNetwork::Pokertables")->search({
                                currency_serial => 1,
                                tourney_serial => 0,
                          },
                          {
                                order_by => {
                                  -desc => 'players',
                                },
                                page => 1,
                                rows => 1,
                          });

   my $table = $tables_rs->first;

   if ($table->players > 4) {
     $c->stash->{table} = $table;
   }
}


sub auto :Path {
    my ( $self, $c ) = @_;

    $c->require_ssl;

    if ($c->config->{offline} && !($c->user && $c->user->privilege == 2)) {
      $c->res->body('Working on updates. Should be up and running shortly.');
    }

    if ($c->user) {
      if (!$c->session->{pokernetwork_auth}) {
        $c->session->{pokernetwork_auth} = $c->sessionid;
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

sub AVATAR :Global :Args(1) {
  my ($self, $c, $uid) = @_;

  my $user = $c->model("PokerNetwork::Users")->find($uid);
  my $default = uri_escape($c->uri_for(
      "/user/no_avatar/". $uid
  ));

  if ($user && $user->email && !$user->hide_gravatar) {
    my $grav_url = "https://secure.gravatar.com/avatar/".md5_hex(lc $user->email)."?d=". $default ."&s=". $c->config->{gravatar_size};
    $c->res->redirect($grav_url);
  }
  else {
    $c->forward('/user/no_avatar/'. $uid);
  }
}

sub contactus :Local :FormConfig {
    my ($self, $c) = @_;
    my $form = $c->stash->{form};

    if ($form->submitted) {
        if ($form->submitted_and_valid) {
            # This is ugly. Need to refactor somehow later
            my $message = "Name: ". $form->params->{name} . "\nEmail: ". $form->params->{email} ."\nText:\n". $form->params->{body};

            $c->log->debug($message);

            $c->email(
                header => [
                    From    => $form->params->{email},
                    To      => $c->config->{site_email},
                    Subject => $form->params->{subject},
                ],
                body => $message,
            );

            push @{$c->flash->{messages}}, "Message sent. Thank you.";

            $c->res->redirect(
              $c->action
            );
        }
        else {
            push @{$c->stash->{errors}}, "Please correct input and re-submit form.";
        }
    }
}

sub credits :Local {}
sub rake :Local {}

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
