<?php

$BOT_TOKEN = getenv('BOT_TOKEN');

if (!$BOT_TOKEN) {
    die('BOT_TOKEN is not configured');
}

define('BOT_TOKEN', $BOT_TOKEN);
define('API_URL', 'https://api.telegram.org/bot' . BOT_TOKEN . '/');

function telegram(string $method, array $data = [])
{
    $ch = curl_init(API_URL . $method);

    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => $data,
        CURLOPT_CONNECTTIMEOUT => 10,
        CURLOPT_TIMEOUT => 30,
    ]);

    $result = curl_exec($ch);

    if ($result === false) {
        error_log('Telegram CURL Error: ' . curl_error($ch));
        curl_close($ch);
        return null;
    }

    curl_close($ch);

    return json_decode($result, true);
}