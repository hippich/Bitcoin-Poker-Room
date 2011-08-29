package Room::Controller::Pages;
use Moose;
use namespace::autoclean;

BEGIN {extends 'Catalyst::Controller'; }

=head1 NAME

Room::Controller::Pages - Custom pages controller.

=head1 DESCRIPTION

Allows you to create pages inside View::HTML include path and 
access these pages via /pages/[template_file_name] URLs. 

Useful when you need to create simple static page and do not 
want to create separate controller/action for it.

Page templates should be saved to /pages/ folder inside 
one of View::HTML include_path. 

=head1 METHODS

=cut


=head2 index

=cut

sub index :Path {
    my ( $self, $c, @page ) = @_;
    my $template = join '/', @page;

    $c->page_not_found unless $template ne "";

    if ( $c->view('HTML')->template_exists('pages', $template) ) {
        $c->stash->{template} = 'pages/' . $template;
        $c->forward( $c->view('HTML') ); 
    }
    else {
        $c->page_not_found; 
    }
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
