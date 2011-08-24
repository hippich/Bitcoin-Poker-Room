#!/usr/bin/env perl
# IMPORTANT: if you delete this file your app will not work as
# expected.  You have been warned.
use inc::Module::Install;

name 'Room';
all_from 'lib/Room.pm';

requires 'Catalyst::Runtime' => '5.80022';
requires 'Catalyst::Plugin::ConfigLoader';
requires 'Catalyst::Plugin::Static::Simple';
requires 'Catalyst::Action::RenderView';
requires 'Moose';
requires 'namespace::autoclean';
requires 'Config::General'; # This should reflect the config file format you've chosen
                 # See Catalyst::Plugin::ConfigLoader for supported formats
requires 'Cache::Memcached';
requires 'DateTime';
requires 'Catalyst::Plugin::Session';
requires 'Catalyst::Plugin::Session::Store::FastMmap';
requires 'Catalyst::Plugin::Session::State::Cookie';
requires 'Catalyst::Plugin::Static::Simple';
requires 'Catalyst::Plugin::Authentication';
requires 'String::Random';
requires 'Catalyst::Controller::HTML::FormFu' => '0.09003';
requires 'Catalyst::Plugin::StackTrace';
requires 'DBIx::Class::EncodedColumn';
requires 'DBIx::Class::TimeStamp';
requires 'JSON::RPC::Client';
requires 'JSON::XS';
requires 'DBIx::Class::FrozenColumns';
requires 'DBIx::Class::FilterColumn';
requires 'DBIx::Class::EncodedColumn';
requires 'Hash::AsObject';
requires 'String::Random';
requires 'Catalyst::Plugin::Email';
requires 'Log::Handler';
requires 'Catalyst::Plugin::LogWarnings';
requires 'Catalyst::Plugin::Log::Handler' => '0.08';
requires 'Net::Twitter::Lite';
requires 'Catalyst::Plugin::RequireSSL';
requires 'Catalyst::Plugin::Authentication';
requires 'Catalyst::Authentication::Store::DBIx::Class';
requires 'Catalyst::Model::Bitcoin';
requires 'HTML::FormFu::Model::DBIC';
requires 'DBIx::Class::DateTime::Epoch';
requires 'CatalystX::RoleApplicator';
requires 'Catalyst::TraitFor::Request::BrowserDetect';
requires 'Test::DBIx::Class';
requires 'Crypt::Eksblowfish';
requires 'Digest::SHA1';


test_requires 'Test::More' => '0.88';
catalyst;

install_script glob('script/*.pl');
auto_install;
WriteAll;