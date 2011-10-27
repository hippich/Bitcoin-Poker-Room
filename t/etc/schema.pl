return {
    schema_class => 'Room::Schema::PokerNetwork',

    resultsets => [
        'Currencies',
        'Deposits',
        'Hands',
        'Messages',
        'Pokertables',
        'Tourneys',
        'TourneysSchedule',
        'User2hand',
        'User2money',
        'User2table',
        'User2tourney',
        'Users',
        'Withdrawal',
    ],

    fixture_sets => {
        basic => [
            Currencies => [
                [ 'serial', 'url', 'id', 'rate', 'minconf', 'class' ],
                [ 1, 'http://bitcoin.org/', 'bitcoin', 100, 0, 'BitcoinServer' ], 
            ],
            Users => [
                [ 'serial', 'name', 'email', 'password', 'privilege', 'created' ],
                [ 22, 'admin', 'admin@test.com', 'admin', 1, 0 ],
                [ 23, 'test', 'test@test.com', 'test', 1, 0 ],
            ],

            Pokertables => [
                [ 'serial', 'seats', 'currency_serial', 'name', 'variant', 'betting_structure', 'small_blind', 'big_blind', 'ante_value', 'ante_bring_in', 'limit_type', 'betting_description', 'skin', 'tourney_serial' ],
                [ 8251, 10, 0, 'tourney table', 'holdem', 'level-001', '0', '0', '0', '0', 'no-limit', 'No limit', 'default', 2071 ],
                [ 8252, 10, 0, 'regular table', 'holdem', '100-200-no-limit', '10000', '20000', '0', '0', 'no-limit', 'No limit 100/200', 'default', 0 ],
            ],

            Tourneys => [
                [ 'serial' ],
                [ 2071 ],
            ],
            
            User2table => [
                [ 'user_serial', 'table_serial', 'money', 'bet' ],
                [ 22, 8251, 132000, 0 ],
                [ 23, 8251, 10000, 0 ], 
            ],

            User2tourney => [
                [ 'user_serial', 'currency_serial', 'tourney_serial', 'table_serial', 'rank' ],
                [ 22, 1, 2071, 8251, 1 ],
                [ 23, 1, 2071, 8251, 2 ], 
            ],

            User2money => [
                [ 'user_serial', 'currency_serial', 'amount', 'rake', 'points' ],
                [ 22, 1, 10000, 100, 20 ], 
            ],
        ]
    },
};
