<?php

require_once __DIR__ . '/config.php';

$update = json_decode(file_get_contents('php://input'), true);

if (!$update) {
    http_response_code(200);
    exit('OK');
}

/*
|--------------------------------------------------------------------------
| Message
|--------------------------------------------------------------------------
*/

if (isset($update['message'])) {

    $message = $update['message'];

    $chatId = $message['chat']['id'] ?? null;
    $text   = trim($message['text'] ?? '');

    if (!$chatId) {
        exit('OK');
    }

    /*
    |--------------------------------------------------------------------------
    | /start
    |--------------------------------------------------------------------------
    */

    if ($text === '/start') {

        $keyboard = [
            'inline_keyboard' => [
                [
                    [
                        'text' => '🎵 موزیک',
                        'callback_data' => 'music'
                    ],
                    [
                        'text' => '📥 دانلود',
                        'callback_data' => 'download'
                    ]
                ],
                [
                    [
                        'text' => '👤 حساب کاربری',
                        'callback_data' => 'profile'
                    ],
                    [
                        'text' => '💎 اشتراک',
                        'callback_data' => 'vip'
                    ]
                ],
                [
                    [
                        'text' => '⚙️ تنظیمات',
                        'callback_data' => 'settings'
                    ]
                ],
                [
                    [
                        'text' => '📞 پشتیبانی',
                        'callback_data' => 'support'
                    ]
                ]
            ]
        ];

        telegram('sendMessage', [
            'chat_id' => $chatId,
            'text' =>
                "🤖 <b>به ربات خوش آمدید</b>\n\n" .
                "یکی از گزینه‌های زیر را انتخاب کنید:",
            'parse_mode' => 'HTML',
            'reply_markup' => json_encode($keyboard)
        ]);

        exit('OK');
    }

    /*
    |--------------------------------------------------------------------------
    | Other messages
    |--------------------------------------------------------------------------
    */

    telegram('sendMessage', [
        'chat_id' => $chatId,
        'text' => "برای شروع روی /start بزنید."
    ]);

    exit('OK');
}


/*
|--------------------------------------------------------------------------
| Callback Query
|--------------------------------------------------------------------------
*/

if (isset($update['callback_query'])) {

    $callback = $update['callback_query'];

    $callbackId = $callback['id'];
    $chatId = $callback['message']['chat']['id'];
    $messageId = $callback['message']['message_id'];
    $data = $callback['data'];

    telegram('answerCallbackQuery', [
        'callback_query_id' => $callbackId
    ]);


    /*
    |--------------------------------------------------------------------------
    | Music
    |--------------------------------------------------------------------------
    */

    if ($data === 'music') {

        telegram('editMessageText', [
            'chat_id' => $chatId,
            'message_id' => $messageId,
            'text' =>
                "🎵 <b>بخش موزیک</b>\n\n" .
                "نام آهنگ مورد نظر خود را ارسال کنید.",
            'parse_mode' => 'HTML',
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        [
                            'text' => '🔙 بازگشت',
                            'callback_data' => 'home'
                        ]
                    ]
                ]
            ])
        ]);

        exit('OK');
    }


    /*
    |--------------------------------------------------------------------------
    | Download
    |--------------------------------------------------------------------------
    */

    if ($data === 'download') {

        telegram('editMessageText', [
            'chat_id' => $chatId,
            'message_id' => $messageId,
            'text' =>
                "📥 <b>دانلود</b>\n\n" .
                "لینک مورد نظر خود را ارسال کنید.",
            'parse_mode' => 'HTML',
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        [
                            'text' => '🔙 بازگشت',
                            'callback_data' => 'home'
                        ]
                    ]
                ]
            ])
        ]);

        exit('OK');
    }


    /*
    |--------------------------------------------------------------------------
    | Profile
    |--------------------------------------------------------------------------
    */

    if ($data === 'profile') {

        telegram('editMessageText', [
            'chat_id' => $chatId,
            'message_id' => $messageId,
            'text' =>
                "👤 <b>حساب کاربری</b>\n\n" .
                "🆔 شناسه: <code>" . htmlspecialchars((string)$chatId) . "</code>\n" .
                "💎 موجودی: 0\n" .
                "⭐ وضعیت: رایگان",
            'parse_mode' => 'HTML',
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        [
                            'text' => '🔙 بازگشت',
                            'callback_data' => 'home'
                        ]
                    ]
                ]
            ])
        ]);

        exit('OK');
    }


    /*
    |--------------------------------------------------------------------------
    | VIP
    |--------------------------------------------------------------------------
    */

    if ($data === 'vip') {

        telegram('editMessageText', [
            'chat_id' => $chatId,
            'message_id' => $messageId,
            'text' =>
                "💎 <b>اشتراک ویژه</b>\n\n" .
                "⭐ امکانات نسخه VIP\n" .
                "⚡ سرعت بیشتر\n" .
                "📥 امکانات بیشتر\n" .
                "🚀 دسترسی ویژه",
            'parse_mode' => 'HTML',
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        [
                            'text' => '💳 خرید اشتراک',
                            'callback_data' => 'buy_vip'
                        ]
                    ],
                    [
                        [
                            'text' => '🔙 بازگشت',
                            'callback_data' => 'home'
                        ]
                    ]
                ]
            ])
        ]);

        exit('OK');
    }


    /*
    |--------------------------------------------------------------------------
    | Settings
    |--------------------------------------------------------------------------
    */

    if ($data === 'settings') {

        telegram('editMessageText', [
            'chat_id' => $chatId,
            'message_id' => $messageId,
            'text' => "⚙️ <b>تنظیمات</b>\n\nتنظیمات ربات در این بخش قرار می‌گیرد.",
            'parse_mode' => 'HTML',
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        [
                            'text' => '🔙 بازگشت',
                            'callback_data' => 'home'
                        ]
                    ]
                ]
            ])
        ]);

        exit('OK');
    }


    /*
    |--------------------------------------------------------------------------
    | Support
    |--------------------------------------------------------------------------
    */

    if ($data === 'support') {

        telegram('editMessageText', [
            'chat_id' => $chatId,
            'message_id' => $messageId,
            'text' =>
                "📞 <b>پشتیبانی</b>\n\n" .
                "برای ارتباط با پشتیبانی پیام خود را ارسال کنید.",
            'parse_mode' => 'HTML',
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        [
                            'text' => '🔙 بازگشت',
                            'callback_data' => 'home'
                        ]
                    ]
                ]
            ])
        ]);

        exit('OK');
    }


    /*
    |--------------------------------------------------------------------------
    | Buy VIP
    |--------------------------------------------------------------------------
    */

    if ($data === 'buy_vip') {

        telegram('answerCallbackQuery', [
            'callback_query_id' => $callbackId,
            'text' => '💎 بخش خرید به‌زودی فعال می‌شود.',
            'show_alert' => true
        ]);

        exit('OK');
    }


    /*
    |--------------------------------------------------------------------------
    | Home
    |--------------------------------------------------------------------------
    */

    if ($data === 'home') {

        $keyboard = [
            'inline_keyboard' => [
                [
                    [
                        'text' => '🎵 موزیک',
                        'callback_data' => 'music'
                    ],
                    [
                        'text' => '📥 دانلود',
                        'callback_data' => 'download'
                    ]
                ],
                [
                    [
                        'text' => '👤 حساب کاربری',
                        'callback_data' => 'profile'
                    ],
                    [
                        'text' => '💎 اشتراک',
                        'callback_data' => 'vip'
                    ]
                ],
                [
                    [
                        'text' => '⚙️ تنظیمات',
                        'callback_data' => 'settings'
                    ]
                ],
                [
                    [
                        'text' => '📞 پشتیبانی',
                        'callback_data' => 'support'
                    ]
                ]
            ]
        ];

        telegram('editMessageText', [
            'chat_id' => $chatId,
            'message_id' => $messageId,
            'text' => "🤖 <b>منوی اصلی</b>\n\nیکی از گزینه‌ها را انتخاب کنید:",
            'parse_mode' => 'HTML',
            'reply_markup' => json_encode($keyboard)
        ]);

        exit('OK');
    }
}

http_response_code(200);
echo 'OK';