package Room::Controller::Admin;
use Moose;
use namespace::autoclean;
use DateTime;
use Data::Dumper;

BEGIN {extends 'Catalyst::Controller'; }

=head1 NAME

Room::Controller::Admin - Catalyst Controller

=head1 DESCRIPTION

Catalyst Controller.

=head1 METHODS

=cut

=head2 auto 

Protect access to all admin-related actions to users with 
privilege == 2

=cut
sub auto :Private {
  my ($self, $c) = @_;

  if (!$c->user || $c->user->privilege != 2) {
    $c->res->redirect( '/404-not-found' );
    return 0;
  }

  1;
}


=head2 base 
 
Beginning of the chain 

=cut
sub base :Chained :PathPart('admin') :CaptureArgs(0) {
  my ($self, $c) = @_;
}


=head2 index

=cut

sub index :Chained('base') :PathPart('') :Args(0) {
  my ($self, $c) = @_;

  $c->stash->{bitcoin_balance} = $c->model("BitcoinServer")->get_balance();

  my $rs = $c->model("PokerNetwork::User2Money")->search(
            { currency_serial => 1 },
            {
              '+select' => [{ SUM => 'amount' }],
              '+as'     => [qw/total_amount/],
           });

  my $row = $rs->first;

  $c->stash->{total_ingame_balance} = $row->get_column('total_amount') / 10000;

  $rs = $c->model("PokerNetwork::User2Table")->search(
            {},
            {
              '+select' => [{ SUM => 'money + bet' }],
              '+as'     => [qw/total_on_tables/],
           });

  $row = $rs->first;

  $c->stash->{total_ingame_on_tables} = $row->get_column('total_on_tables') / 10000;
}


sub users :Chained('base') :Args(0) {
  my ($self, $c) = @_;
  my $name = $c->req->params->{'name'} || '';
  my $email = $c->req->params->{'email'} || '';
  my $page = $c->req->params->{'page'} || 0;
  $page = 1 if $page < 1;

  $c->stash->{users} = $c->model('PokerNetwork::Users')->search(undef, {
    rows => 50,
    page => $page,
    order_by => 'name' 
  });

  $c->stash->{users} = $c->stash->{users}->search({ 'name' => { 'LIKE' => '%'. $name .'%' } }) unless $name eq '';
  $c->stash->{users} = $c->stash->{users}->search({ 'email' => { 'LIKE' => '%'. $email .'%' } }) unless $email eq '';
}


sub user :Chained('base') :CaptureArgs(1) {
  my ($self, $c, $user_id) = @_;
  
  $c->stash->{user} = $c->model("PokerNetwork::Users")->find($user_id);
}

sub kick :Chained('user') :Args(0) {
  my ($self, $c) = @_;

}

sub profile :Chained('user') :PathPart('') :Args(0) {}


sub hands :Chained('user') :Args(0) {
  my ($self, $c) = @_;
  my $page = $c->req->params->{'page'} || 1;

  $c->stash->{hands} = $c->stash->{user}->hands->search(undef, {
    rows => 50,
    page => $page,
    order_by => {
      -desc => 'serial',
    }
  });

  $c->stash->{template} = 'user/hand/index';
}


sub view_hand :Chained('user') :PathPart('hands') :Args(1) {
  my ($self, $c, $id) = @_;

  my $hand = $c->model('PokerNetwork::Hands')->search({serial => $id})->first;

  if (! $hand) {
    $c->detach('/default');
  }

  $c->stash->{hand} = $hand->get_parsed_history;
  
  $c->stash->{template} = 'user/hand/view_hand_only';
}


sub withdrawals :Chained('base') :Args(0) {
  my ($self, $c) = @_;

  my $page = $c->req->params->{'page'};
  $page = 1 if $page < 1;

  $c->stash->{withdrawals} = $c->model("PokerNetwork::Withdrawal")->search({}, { 
      rows => 50,
      page => $page,
      order_by => { 
        -desc => 'withdrawal_id' 
      } 
  });
}


sub withdrawal_base :Chained('base') :PathPart('withdrawal') :CaptureArgs(1) {
  my ($self, $c, $id) = @_;

  my $withdrawal = $c->model("PokerNetwork::Withdrawal")->find($id);

  if (! $withdrawal) {
    $c->detach( '/default' );
  }

  $c->stash->{withdrawal} = $withdrawal;
}


sub withdrawal :Chained('withdrawal_base') :PathPart('') :Args(0) {
  my ($self, $c) = @_;
}

sub withdrawal_info :Chained('withdrawal_base') :PathPart('info') :Args(0) {
  my ($self, $c) = @_;

  $c->stash->{withdrawal}->info(
    $c->req->param('withdrawal_info')
  );
  $c->stash->{withdrawal}->update();
  
  push @{$c->flash->{messages}}, "Order additional info updated.";

  $c->res->redirect(
    $c->uri_for('/admin/withdrawal/' . $c->stash->{withdrawal}->id)
  );
}


sub withdrawal_reprocess :Chained('withdrawal_base') :PathPart('reprocess') :Args(0) {
  my ($self, $c) = @_;
  my $withdrawal = $c->stash->{withdrawal};

  # Hardcoded to handle only Bitcoins right now
  if ($withdrawal->currency->serial == 1) {
    my $result = $c->model("BitcoinServer")->send_to_address($withdrawal->dest, $withdrawal->amount);

    if (! $c->model('BitcoinServer')->api->error) {
      # Mark as processed if successful
      $withdrawal->processed_at( DateTime->now() );
      $withdrawal->processed(1);
      $withdrawal->update();

      push @{$c->flash->{messages}}, "Order reprocessed. Bitcoins sent.";
    }
    else {
      push @{$c->flash->{errors}}, "Bitcoins not sent. Here is daemon answer: <pre>\n" . Dumper($result);
    }
  }
  else {
    push @{$c->flash->{errors}}, "Currently, only one currency supported. Currency serial should be equal 1.";
  }
  
  $c->res->redirect(
    $c->uri_for('/admin/withdrawal/' . $withdrawal->id)
  );
}


sub mark :Chained('withdrawal_base') :CaptureArgs(0) {
  my ($self, $c) = @_;
}


sub mark_processed :Chained('mark') :PathPart('processed') {
  my ($self, $c) = @_;
  
  $c->stash->{withdrawal}->processed_at( DateTime->now() );
  $c->stash->{withdrawal}->processed(1);
  $c->stash->{withdrawal}->update();

  push @{$c->flash->{messages}}, "Withdrawal marked processed.";
  $c->res->redirect(
    $c->uri_for('/admin/withdrawal/' . $c->stash->{withdrawal}->id)
  );
}

sub mark_unprocessed :Chained('mark') :PathPart('unprocessed') {
  my ($self, $c) = @_;

  $c->stash->{withdrawal}->processed_at(undef);
  $c->stash->{withdrawal}->processed(undef);
  $c->stash->{withdrawal}->update();

  push @{$c->flash->{messages}}, "Withdrawal marked unprocessed.";
  $c->res->redirect(
    $c->uri_for('/admin/withdrawal/' . $c->stash->{withdrawal}->id)
  );
}

sub mark_canceled :Chained('mark') :PathPart('canceled') {
  my ($self, $c) = @_;
  
  $c->stash->{withdrawal}->processed_at(DateTime->now());
  $c->stash->{withdrawal}->processed( -1 );
  $c->stash->{withdrawal}->update();
  
  push @{$c->flash->{messages}}, "Order canceled.";
  $c->res->redirect(
    $c->uri_for('/admin/withdrawal/' . $c->stash->{withdrawal}->id)
  );
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

