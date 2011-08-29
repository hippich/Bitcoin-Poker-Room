package Room::Controller::Admin::Tourneys::Schedule;
use Moose;
use namespace::autoclean;

BEGIN {extends 'Catalyst::Controller::HTML::FormFu'; }

=head1 NAME

Room::Controller::Admin::Tourneys::Schedule - Catalyst Controller

=head1 DESCRIPTION

Catalyst Controller.

=head1 METHODS

=cut


=head2 index

=cut

sub index :Path :Args(0) {
    my ( $self, $c ) = @_;

    $c->stash->{schedules} = $c->model('PokerNetwork::TourneysSchedule')->search(undef, {
      page => $c->req->params->{page} || 1,
      rows => 50,
      order_by => {
        -desc => 'serial',
      },
    });
}


=head2 schedule_base

Base chain start 

=cut 
sub schedule_base :Chained :PathPart('admin/tourneys/schedule') :CaptureArgs(1) {
    my ($self, $c, $serial) = @_;

    $c->stash->{schedule} = $c->model('PokerNetwork::TourneysSchedule')->find($serial);
    $c->page_not_found unless $c->stash->{schedule};
}


=head2 view 

Display schedule details.

=cut
sub view :Chained('schedule_base') :PathPart('') {
    my ($self, $c) = @_;
}


=head2 edit 

Update newly created or already existing schedule.

=cut
sub edit :Chained('schedule_base') :FormConfig {
    my ($self, $c) = @_;

    my $form = $c->stash->{form};
    my $schedule = $c->stash->{schedule};
    $form->stash->{schedule} = $schedule;

    if ($form->submitted_and_valid && !$c->req->param('cancel')) {
        $form->model->update($schedule); 
        $c->res->redirect('/admin/tourneys/schedule/'. $schedule->serial);
        push @{$c->flash->{messages}}, 'Schedule saved.';
    }
    elsif ( $c->req->param('cancel') ) {
        $c->res->redirect('/admin/tourneys/schedule/'. $schedule->serial);
    } 
    elsif ( !$form->submitted ) {
        $form->model->default_values($schedule);
    }
}


=head2 delete 

Delete tourney schedule. 

=cut 
sub delete :Chained('schedule_base') {
    my ($self, $c) = @_;

    $c->stash->{schedule}->delete();

    $c->forward('return_back');
}

=head2 activate 

Activate schedule 

=cut 
sub activate :Chained('schedule_base') {
    my ($self, $c) = @_;

    $c->stash->{schedule}->active('y');
    $c->stash->{schedule}->update();

    $c->forward('return_back');
}


=head2 deactivate 

Deactivate schedule 

=cut 
sub deactivate :Chained('schedule_base') {
    my ($self, $c) = @_;

    $c->stash->{schedule}->active('n');
    $c->stash->{schedule}->update();

    $c->forward('return_back');
}


=head2 create 

Create new schedule in DB and redirect to edit it. 

=cut 
sub create :Local :Args(0) {
    my ($self, $c) = @_;

    my $schedule = $c->model('PokerNetwork::TourneysSchedule')->create({
        active => 'no',
    });

    $c->res->redirect( '/admin/tourneys/schedule/'. $schedule->serial .'/edit');
}


=head2 return_back

Returns user either to tourneys/index or to destination specified in 
dest request parameter.

=cut 
sub return_back :Private {
    my ($self, $c) = @_;

    my $dest = $c->req->params->{dest} || '/admin/tourneys/schedule';
    $c->res->redirect($dest);
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
