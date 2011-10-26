#!/usr/bin/perl 
#===============================================================================
#
#         FILE:  generate_sql.pl
#
#        USAGE:  ./generate_sql.pl  
#
#  DESCRIPTION:  Generate migration SQL files.
#
#      OPTIONS:  --force_overwrite  
#              
# REQUIREMENTS:  ---
#         BUGS:  ---
#        NOTES:  ---
#       AUTHOR:  Pavel A. Karoukin
#      COMPANY:  Yep Corp Limited
#      VERSION:  1.0
#      CREATED:  10/25/2011 06:58:21 PM
#     REVISION:  ---
#===============================================================================

use strict;
use warnings;
use v5.10;

BEGIN {
    use FindBin qw($Bin);
    use lib $Bin . "/../lib";
}

use aliased 'DBIx::Class::DeploymentHandler' => 'DH';
use Room::Schema::PokerNetwork;
use Getopt::Long;

my $force_overwrite = 0;

unless ( GetOptions( 'force_overwrite!' => \$force_overwrite ) ) {
    die "Invalid options";
}

my $s = Room::Schema::PokerNetwork->connect({
        dsn => 'dbi:mysql:pythonpokernetwork',
        user => 'root',
        password => '',
        AutoCommit => 1,
});

my $dh = DH->new(
    {
        schema              => $s,
        script_directory    => "$FindBin::Bin/../sql",
        databases           => 'MySQL',
        sql_translator_args => { add_drop_table => 0 },
        force_overwrite     => $force_overwrite,
    }
);

my $version = Room::Schema::PokerNetwork->VERSION;

say "generating deployment script";
$dh->prepare_install;
 
if ( $version > 1 ) {
    say "generating upgrade script";
    $dh->prepare_upgrade( {
            from_version => $version - 1,
            to_version   => $version,
            version_set  => [ $version - 1, $version ],
        } );
 
    say "generating downgrade script";
    $dh->prepare_downgrade( {
            from_version => $version,
            to_version   => $version - 1,
            version_set  => [ $version, $version - 1 ],
        } );
}

say "generating graph";
 
my $trans = SQL::Translator->new(
    parser        => 'SQL::Translator::Parser::DBIx::Class',
    parser_args   => { package => $s },
    producer      => 'Diagram',
    producer_args => {
        out_file         => $FindBin::Bin .'/sql/diagram-v' . $version . '.png',
        show_constraints => 1,
        show_datatypes   => 1,
        show_sizes       => 1,
        show_fk_only     => 0,
    } );
 
$trans->translate;
 
say "done";