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


=head2 index

=cut

sub base :Chained :PathPart('admin') :CaptureArgs(0) {
  my ($self, $c) = @_;

  if ($c->user->privilege != 2) {
    $c->detach( '/default' );
  }
}


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

  $c->stash->{total_ingame_balance} = $row->get_column('total_amount') / 100;
}


sub withdrawals :Chained('base') :Args(0) {
  my ($self, $c) = @_;

  $c->stash->{withdrawals} = $c->model("PokerNetwork::Withdrawal")->search({}, { 
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

