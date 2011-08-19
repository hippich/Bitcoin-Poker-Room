return {
    schema_class => 'Room::Schema::PokerNetwork',

    resultsets => [
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
        tourneys => [
            Users => [
                [ 'serial', 'name', 'email', 'password', 'privilege', 'created' ],
                [ 22, 'admin', 'admin@test.com', 'd033e22ae348aeb5660fc2140aec35850c4da997', 1, 0 ],
                [ 23, 'test', 'test@test.com', 'd033e22ae348aeb5660fc2140aec35850c4da997', 1, 0 ],
            ],

            Pokertables => [
                [ 'serial', 'seats', 'currency_serial', 'name', 'variant', 'betting_structure', 'skin', 'tourney_serial' ],
                [ 8251, 10, 0, 'tourney table', 'holdem', 'level-001', 'default', 2071 ],
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
            ]
        ]
    },
};
