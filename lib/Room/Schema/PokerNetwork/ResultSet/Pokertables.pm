package Room::Schema::PokerNetwork::ResultSet::Pokertables;

use strict;
use warnings;

use base qw( DBIx::Class::ResultSet );

sub advanced_search {
     my ( $self, $params, $attrs ) = @_;
     my $columns = {};

     for my $column ( keys %$params ) {

         if ( my $search = $self->can( "search_for_$column" ) ) {
             $self = $self->$search( $params );
             next;
         }

         my ( $full_name, $relation ) = $self->parse_column( $column );

         $self = $self->search({}, { join => $relation });
         $columns->{$full_name} = $params->{$column};
     }

     return $self->search( $columns, $attrs );
} 


sub parse_column {
    my ( $self, $field)  = @_;

    if ( $field =~ /(.*?)\.(.*)/ ) {
        my $first = $1;
        my $rest  = $2;
        my( $column, $join ) = $self->parse_column( $rest );
        if ( $join ) {
            return $column, { $first => $join };
        }
        else {
            return $first . '.' . $column, $first;
        }
    }
    elsif ( $field ) { 
        return $field;
    }
    else {
        return;
    }
}

1;
