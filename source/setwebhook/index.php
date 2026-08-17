<?php
# ! -- @GRT_Team | @MC_Source -- !
error_reporting(0);

set_time_limit(0);

flush();

$API_KEY = '[TOKEN]';
##------------------------------##
define('API_KEY',$API_KEY);
function bot($method,$datas=[]){
    $url = "https://api.telegram.org/bot".API_KEY."/".$method;
    $ch = curl_init();
    curl_setopt($ch,CURLOPT_URL,$url);
    curl_setopt($ch,CURLOPT_RETURNTRANSFER,true);
    curl_setopt($ch,CURLOPT_POSTFIELDS,$datas);
    $res = curl_exec($ch);
    if(curl_error($ch)){
        var_dump(curl_error($ch));
    }else{
        return json_decode($res);
    }
}
 function sendmessage($chat_id, $text, $model){
	bot('sendMessage',[
	'chat_id'=>$chat_id,
	'text'=>$text,
	'parse_mode'=>$mode
	]);
	}
	function sendaction($chat_id, $action){
	bot('sendchataction',[
	'chat_id'=>$chat_id,
	'action'=>$action
	]);
	}
	function Forward($KojaShe,$AzKoja,$KodomMSG)
{
    bot('ForwardMessage',[
        'chat_id'=>$KojaShe,
        'from_chat_id'=>$AzKoja,
        'message_id'=>$KodomMSG
    ]);
}
function sendphoto($chat_id, $photo, $action){
	bot('sendphoto',[
	'chat_id'=>$chat_id,
	'photo'=>$photo,
	'action'=>$action
	]);
	}
	function objectToArrays($object)
    {
        if (!is_object($object) && !is_array($object)) {
            return $object;
        }
        if (is_object($object)) {
            $object = get_object_vars($object);
        }
        return array_map("objectToArrays", $object);
    }
	//====================bot_sazan_good======================//
$update = json_decode(file_get_contents('php://input'));
$message = $update->message;
$chat_id = $message->chat->id;
$message_id = $message->message_id;
$from_id = $message->from->id;
$text = $message->text;
$bot_type = file_get_contents("data/bottype.txt");
@mkdir("data/$chat_id");
$data = $update->callback_query->data;
$chatid = $update->callback_query->message->chat->id;
$message_id2 = $update->callback_query->message->message_id;
@$rasol = file_get_contents("data/$chat_id/rasol.txt");
$ADMIN = "[ADMIN]";
$homebaks = json_encode([
                        'inline_keyboard' => [
                            [
                                ['text' => "بازگشت", 'callback_data' => "home"]
                            ],
    ]
]);

//====================bot_sazan_good======================//
if($text == "/start"){
if (!file_exists("data/$chat_id/rasol.txt")) {
        file_put_contents("data/$chat_id/rasol.txt","none");
        $myfile2 = fopen("data/Member.txt", "a") or die("Unable to open file!");
		  $add_user = file_get_contents('data/Member.txt');
            $add_user .= $from_id . "\n";
        fwrite($myfile2, "$chat_id\n");
        fclose($myfile2);
		
    }
        sendAction($chat_id, 'typing');
if($bot_type != "gold"){
    bot('sendmessage',[
	'chat_id'=>$chat_id,
	'text'=>"ربات خود را بسازید♻️
💠 @m_y002",
        ]);
}
	bot('sendmessage',[
	'chat_id'=>$chat_id,
	'text'=>"سلام من یه ربات کاربردی هستم میتونم کار های زیرو انجام بدم🙃",
            'parse_mode' => "MarkDown",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        ['text' => "ست وب هوک📡", 'callback_data' => "setwebhook"],['text' => "اطلاعات توکن🔍", 'callback_data' => "infotoken"]
                    ],
                    [
                        ['text' => "دلیت وب هوک❌", 'callback_data' => "deletewebhook"]
                    ],
                ]
            ])
        ]);
	} elseif($data == "home"){
file_put_contents("data/$chatid/rasol.txt","no");
file_put_contents("data/$chatid/token.txt","no");
file_put_contents("data/$chatid/url.txt","no");
        bot('editmessagetext', [
            'chat_id' => $chatid,
            'message_id' => $message_id2,
	'text'=>"به منوی اصلی برگشتید🙃",
            'parse_mode' => "MarkDown",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        ['text' => "ست وب هوک📡", 'callback_data' => "setwebhook"],['text' => "اطلاعات توکن🔍", 'callback_data' => "infotoken"]
                    ],
                    [
                        ['text' => "دلیت وب هوک❌", 'callback_data' => "deletewebhook"]
                    ],
                    
                ]
            ])
        ]);
	}
//====================bot_sazan_good======================//
elseif($data == "setwebhook"){
			file_put_contents("data/$chatid/rasol.txt","to");
        bot('editmessagetext', [
            'chat_id' => $chatid,
            'message_id' => $message_id2,
		'text'=>"خوب کاربر عزیز ابتدا توکن ربات خودتون را بفرستید",
            'parse_mode' => "MarkDown",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        ['text' => "🔸 بازگشت", 'callback_data' => "home"]
					],  
                ]
            ])
        ]);
	} elseif($rasol == "to"){
$token = $text;
    $rasol1 = json_decode(file_get_contents("https://api.telegram.org/bot" . $token . "/getwebhookinfo"));
    $rasol2 = json_decode(file_get_contents("https://api.telegram.org/bot" . $token . "/getme"));
        //==================
    $tik2 = objectToArrays($rasol1);
    $ur = $tik2["result"]["url"];
    $ok2 = $tik2["ok"];
    $tik1 = objectToArrays($rasol2);
    $un = $tik1["result"]["username"];
    $fr = $tik1["result"]["first_name"];
    $id = $tik1["result"]["id"];
    $ok = $tik1["ok"];
    if ($ok != 1) {
        //Token Not True
        SendMessage($chat_id, "عه توکن را اشتباه وارد کردید😐\n لطفا توکن را بدرستی وارد کنید😉");
    } else{
    file_put_contents("data/$chat_id/rasol.txt","url");
    file_put_contents("data/$chat_id/token.txt",$text);
	SendAction($chat_id,'typing');
	bot('sendmessage',[
    'chat_id'=>$chat_id,
    'text'=>"خوب حالا ادرس جای که سورستون قرار داره را بفرستید 

    مثلا:
    https://ادس.ir/index.php
    
        حتما ابتدا با https://  شروع شود",
            'parse_mode' => "MarkDown",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        ['text' => "🔸 بازگشت", 'callback_data' => "home"]
					],  
                ]
            ])
        ]);
}
} elseif($rasol == "url"){
if (!preg_match("/\b(?:(?:https?|ftp):\/\/|www\.)[-a-z0-9+&@#\/%?=~_|!:,.;]*[-a-z0-9+&@#\/%=~_|]/i",$text))
  {
  SendAction($chat_id,'typing');
	bot('sendmessage',[
    'chat_id'=>$chat_id,
    'text'=>" سایتتون اشتباهه",
            'parse_mode' => "MarkDown",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        ['text' => "🔸 بازگشت", 'callback_data' => "home"]
					],  
                ]
            ])
        ]);
 } else {
 file_put_contents("data/$chat_id/rasol.txt","no");
 file_put_contents("data/$chat_id/url.txt",$text);
 $token = file_get_contents("data/$chat_id/token.txt"); 
 $url = file_get_contents("data/$chat_id/url.txt"); 
  file_get_contents("https://api.telegram.org/bot$token/setwebhook?url=$url");
	bot('sendmessage',[
    'chat_id'=>$chat_id,
    'text'=>"وب هوک ست شد  موفق  و موید باشید 
    توکن ربات شما :
    $token
    ادرس سورس شما 
    $text",
            'parse_mode' => "MarkDown",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        ['text' => "ست وب هوک📡", 'callback_data' => "setwebhook"],['text' => "اطلاعات توکن🔍", 'callback_data' => "infotoken"]
                    ],
                    [
                        ['text' => "دلیت وب هوک❌", 'callback_data' => "deletewebhook"]
                    ],
                ]
            ])
        ]);
 }
}
/////--------
elseif($data == "infotoken"){
    file_put_contents("data/$chatid/rasol.txt","token");
        bot('editmessagetext', [
            'chat_id' => $chatid,
            'message_id' => $message_id2,
    'text'=>"خوب دوست عزیز توکن خودتون را بفرستید:",
            'parse_mode' => "MarkDown",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        ['text' => "🔸 بازگشت", 'callback_data' => "home"]
          ],  
                ]
            ])
        ]);
} elseif($rasol == "token"){
    $rasol1 = json_decode(file_get_contents("https://api.telegram.org/bot" . $text . "/getwebhookinfo"));
    $rasol2 = json_decode(file_get_contents("https://api.telegram.org/bot" . $text . "/getme"));
        //==================
    $tik2 = objectToArrays($rasol1);
    $ur = $tik2["result"]["url"];
    $ok2 = $tik2["ok"];
    $tik1 = objectToArrays($rasol2);
    $un = $tik1["result"]["username"];
    $fr = $tik1["result"]["first_name"];
    $id = $tik1["result"]["id"];
    $ok = $tik1["ok"];
    if ($ok != 1) {
        //Token Not True
        SendMessage($chat_id,"عه توکن را اشتباه وارد کردید😐\n لطفا توکن را بدرستی وارد کنید😉");
    }else{
    file_put_contents("data/$chat_id/rasol.txt","no");
  bot('sendmessage',[
    'chat_id'=>$chat_id,
    'text'=>"وضعیت توکن : True

خوب اطلاعات ربات شما😉👇
username: @$un
Id : $id
name : $fr
ادرس ست شده سورس:
$ur",
            'parse_mode' => "MarkDown",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        ['text' => "ست وب هوک📡", 'callback_data' => "setwebhook"],['text' => "اطلاعات توکن🔍", 'callback_data' => "infotoken"]
                    ],
                    [
                        ['text' => "دلیت وب هوک❌", 'callback_data' => "deletewebhook"]
                    ],
                ]
            ])
        ]);
}
}
/////--------
elseif($data == "deletewebhook" ){
    file_put_contents("data/$chat_id/rasol.txt","del");
	sendaction($chat_id,'typing');
        bot('editmessagetext', [
            'chat_id' => $chatid,
            'message_id' => $message_id2,
    'text'=>"خوب دوست عزیز توکن خودتون را بفرستید:",
            'parse_mode' => "MarkDown",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        ['text' => "🔸 بازگشت", 'callback_data' => "home"]
					],  
                ]
            ])
        ]);
}elseif($rasol == "del"){
$token = $text;
    $rasol1 = json_decode(file_get_contents("https://api.telegram.org/bot" . $text . "/getwebhookinfo"));
    $rasol2 = json_decode(file_get_contents("https://api.telegram.org/bot" . $text . "/getme"));
        //==================
    $tik2 = objectToArrays($rasol1);
    $ur = $tik2["result"]["url"];
    $ok2 = $tik2["ok"];
    $tik1 = objectToArrays($rasol2);
    $un = $tik1["result"]["username"];
    $fr = $tik1["result"]["first_name"];
    $id = $tik1["result"]["id"];
    $ok = $tik1["ok"];
    if ($ok != 1) {
        //Token Not True
        SendMessage($chat_id, "عه توکن را اشتباه وارد کردید😐\n لطفا توکن را بدرستی وارد کنید😉");
    } else{
    file_put_contents("data/$chat_id/rasol.txt","no");
file_get_contents("https://api.telegram.org/bot$text/deletewebhook");
	SendAction($chat_id,'typing');
 	bot('sendmessage',[
    'chat_id'=>$chat_id,
    'text'=>"دلیت وب هوک با موفقیت انجام شد.",
            'parse_mode' => "MarkDown",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        ['text' => "ست وب هوک📡", 'callback_data' => "setwebhook"],['text' => "اطلاعات توکن🔍", 'callback_data' => "infotoken"]
                    ],
                    [
                        ['text' => "دلیت وب هوک❌", 'callback_data' => "deletewebhook"]
                    ],
                ]
            ])
        ]);
}
}
//====================bot_sazan_good======================//
if ($text == "/panel") {
        file_put_contents("data/$chat_id/rasol.txt", "no");
        bot('sendmessage', [
            'chat_id' => $ADMIN,
            'text' => "مدیر گرامی به پنل مدیریت ربات ‌موشکی خوش امدید🙂",
            'parse_mode' => "MarkDown",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
[
                        ['text' => "📈آمار کلی و وضعیت ربات📉", 'callback_data' => "am"]
                    ],
                    [
                        ['text' => "ارسال پیام به همه کاربران🙂", 'callback_data' => "send"], ['text' => "فروارد همگانی🤓", 'callback_data' => "fwd"]
                    ],
                    [
                        ['text' => "برگرد خونه🏡🤠", 'callback_data' => "home"]
                    ],
                ]
            ])
        ]);
    } elseif ($data == "homee") {
        file_put_contents("data/$chat_id/rasol.txt", "no");
        sendAction($chat_id, 'typing');
            bot('sendMessage', [
            'chat_id' => $chat_id,
            'message_id' => $message_id2,
            'text' => "الان مثلا تو ادمین ربات ؟😐
این قسمت برای ادمیناس لطفا دیگر تلاش نکنید😁",
        ]);
        bot('editmessagetext', [
            'chat_id' => $ADMIN,
            'message_id' => $message_id2,
            'text' => "خوش امدید",
            'parse_mode' => "MarkDown",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        ['text' => "📈آمار کلی و وضعیت ربات📉", 'callback_data' => "am"]
                    ],
                    [
                        ['text' => "ارسال پیام به همه کاربران🙂", 'callback_data' => "send"], ['text' => "فروارد همگانی🤓", 'callback_data' => "fwd"]
                    ],
                    [
                        ['text' => "برگرد خونه🏡🤠", 'callback_data' => "home"]
                    ],
                ]
            ])
        ]);
    } 
 elseif ($data == "am") {
        $user = file_get_contents("data/Member.txt");
        $member_id = explode("\n", $user);
        $member_count = count($member_id) - 1;
        bot('answercallbackquery', [
            'callback_query_id' => $update->callback_query->id,
            'text' => "تعداد ممبر ها : $member_count
",

            'show_alert' => true
        ]);
    }
	elseif ($data == "send") {
        file_put_contents("data/$chatid/rasol.txt", "send");
        bot('editmessagetext', [
            'chat_id' => $chatid,
            'message_id' => $message_id2,
            'text' => "خوب پیام خودتون را برام بفرستید تا بفرستم برا  کاربرا  . بدو وقت ندارم😑",
        ]);
    } elseif ($rasol == "send") {
        file_put_contents("data/$chat_id/rasol.txt", "no");
        $fp = fopen("data/Member.txt", 'r');
        while (!feof($fp)) {
            $ckar = fgets($fp);
            sendmessage($ckar, $text);
        }
        bot('sendMessage', [
            'chat_id' => $chat_id,
            'text' => "با موفقیت برای همه کاربران ارسال شد",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        ['text' => "برگرد خونه🏡🤠", 'callback_data' => "home"]
                    ],
                    [
                        ['text' => "برگشت مدیریت", 'callback_data' => "homee"]
                    ],
                ]
            ])
        ]);
    } elseif ($data == "fwd") {
        file_put_contents("data/$chatid/rasol.txt", "fwd");
        bot('editmessagetext', [
            'chat_id' => $chatid,
            'message_id' => $message_id2,
            'text' => "خوب پیام خودتون را فروارد کنید فقط زود که حوصله ندارم😤",
        ]);
    } elseif ($rasol == 'fwd') {
        file_put_contents("data/$chat_id/rasol.txt", "no");
        $forp = fopen("data/Member.txt", 'r');
        while (!feof($forp)) {
            $fakar = fgets($forp);
            Forward($fakar, $chat_id, $message_id);
        }
        bot('sendMessage', [
            'chat_id' => $chat_id,
            'text' => "با موفقیت فروارد شد.",
            'reply_markup' => json_encode([
                'inline_keyboard' => [
                    [
                        ['text' => "برگرد خونه🏡🤠", 'callback_data' => "home"]
                    ],
                    [
                        ['text' => "برگشت مدیریت", 'callback_data' => "homee"]
                    ],
                ]
            ])
        ]);
    } 
?>

