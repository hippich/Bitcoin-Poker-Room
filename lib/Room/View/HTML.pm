package Room::View::HTML;

use strict;
use base 'Catalyst::View::TT';

__PACKAGE__->config({
    INCLUDE_PATH => [
        Room->path_to( 'root', 'src' ),
        Room->path_to( 'root', 'lib' )
    ],
    PRE_PROCESS  => 'config/main',
    WRAPPER      => 'site/wrapper',
    ERROR        => 'error.tt2',
    TIMER        => 0
});

=head1 NAME

Room::View::HTML - Catalyst TTSite View

=head1 SYNOPSIS

See L<Room>

=head1 DESCRIPTION

Default HTML View for Room application.

=cut 

=head2 template_exists

Test if View::TT can find template specified.

=cut
sub template_exists {
    my ( $self, $subdir, $template ) = @_;

    # Prevent access to files outside of include_path
    my $base_dir = $self->include_path->[0]->subdir($subdir);
    my $file_dir = $self->include_path->[0]->subdir($subdir)->file($template)->dir;

    return 0 if !$file_dir->subsumes($base_dir);

    # Iterate through all include paths to find template
    foreach my $dir (@{ $self->include_path }) {
        return 1 if ( -e $dir->subdir($subdir)->file($template) );
    }

    return 0;
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

1;

