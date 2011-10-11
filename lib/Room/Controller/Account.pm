package Room::Controller::Account;
use Moose;
use namespace::autoclean;

BEGIN {extends 'Catalyst::Controller::HTML::FormFu'; }

=head1 NAME

Room::Controller::Account - Provides Login/Logout, Register, 
Password restore, etc functions.

=head1 DESCRIPTION

Catalyst Controller.

=head1 METHODS

=cut

=head2 auto 

Redirect all authenticated user to /user page 

=cut 
sub auto :Private {
  my ($self, $c) = @_;

  if ($c->user && $c->action->private_path !~ /account\/no_avatar/) {
    $c->res->redirect(
      $c->uri_for('/user')
    );

    return;
  }

  1;
}


sub login :Local :Args(0) :FormConfig {
    my ( $self, $c ) = @_;

    my $form = $c->stash->{form};

    if ($form->submitted_and_valid) {
    
      my $user = $c->authenticate({
                    name => $form->params->{name},
                    password => $form->params->{password},
                 });

      if ($user) {
        if ($c->req->param('destination')) {
          my $dest = $c->req->param('destination');
          
          # clean up destination URL
          $dest = '/'. $dest unless $dest =~ /^\//;
          $dest =~ s/\/index$//;

          $c->res->redirect( $dest );

          return 1;
        }
        
        $c->res->redirect(
          $c->uri_for('/user')
        );
      }
      else {
        push @{$c->stash->{errors}}, "Invalid Username or Password.";
      }
    }
}


sub register :Local :Args(0) :FormConfig {
  my ( $self, $c ) = @_;

  my $form = $c->stash->{form};

  if ($form->submitted_and_valid) {

    if (
          $c->model("PokerNetwork::Users")->search({ name => $form->params->{name} })->count > 0
       ) {
      $form->get_field("name")->get_constraint({ type => "Callback" })->force_errors(1);
      $form->process();
      return;
    }

    if (
          $form->params->{email} ne '' &&
          $c->model("PokerNetwork::Users")->search({ email => $form->params->{email} })->count > 0
    ) {
      $form->get_field("email")->get_constraint({ type => "Callback" })->force_errors(1);
      $form->process();
      return;
    }

    my $user = $c->model("PokerNetwork::Users")->new({
      name => $form->params->{name},
      password => $form->params->{password},
      created => DateTime->now,
    });

    if ( $form->params->{email} ) {
      $user->email( $form->params->{email} );
    }

    $user->insert();

    push @{$c->flash->{messages}}, "Account successfully created. Please, login with your details.";

    $c->res->redirect(
      $c->uri_for('/account/login')
    );
  }
}



sub forgot_password :Local :Args(0) :FormConfig {
  my ($self, $c) = @_;

  my $form = $c->stash->{form};

  if ($form->submitted_and_valid) {
    my $user = $c->model("PokerNetwork::Users")->search({ email => $form->params->{email} })->first;

    if (! $user) {
      $form->get_field("email")->get_constraint({ type => "Callback" })->force_errors(1);
      $form->process();
      return;
    }

    my $gen = new String::Random;
    my $key = unpack('h*', $gen->randpattern('b'x10));

    $user->request_password($key);
    $user->update();

    # This is ugly. Need to refactor somehow later
    my $message = "Someone requested to reset your password at ". $c->uri_for('/') ."\n\nYour username: ". $user->name ."\n\nTo reset password, please open (or copy/paste) this URL: ". $c->uri_for('/account/reset_password', $user->id, $key) ."\n\nIf this was not you, just ignore this email.";

    $c->log->debug($message);

    $c->email(
        header => [
            From    => $c->config->{site_email},
            To      => $user->email,
            Subject => 'Password reset link.'
        ],
        body => $message,
    );

    $c->stash->{email} = $user->email;
  }
}



sub reset_password :Local :Args(2) :FormConfig {
  my ($self, $c, $id, $key) = @_;

  my $user = $c->model("PokerNetwork::Users")->find($id);
  
  if (!defined($user) || !defined($user->request_password) || $user->request_password ne $key) {
    $c->page_not_found;
  }

  my $form = $c->stash->{form};

  if ($form->submitted_and_valid) {
    $user->password( $form->params->{password} );
    $user->update();
    
    push @{$c->flash->{messages}}, "Password successfully reset.";

    $c->res->redirect(
      $c->uri_for('/account/login')
    );
  }
}

sub no_avatar :Local :Args(1) {
  my ($self, $c, $uid) = @_;

  $c->res->redirect(
    $c->uri_for("/static/css/images/jpoker_table/avatar". ($uid % 19) .".png")
  );
}


=head2 index

Default action. Simply redirect user to login page

=cut

sub index :Path :Args(0) {
    my ( $self, $c ) = @_;

    $c->response->redirect( $c->uri_for('/account/login') ); 
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
