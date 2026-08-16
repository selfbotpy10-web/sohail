<?php

/*

بسم الله الرحمن الرحیم
! ----------------------- !
Source » ربات ساز !
Author » @m_y002
Channels » @GRT_Team | @MC_Source
! ----------------------- !
اسکی بدون ذکر منبع و نویسنده ممنوع می باشد !

*/

error_reporting(0);
define('API_KEY',''); //Token
function yzi($method,$datas=[]){
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

function SendMessage($chatid,$text,$parsmde,$disable_web_page_preview,$keyboard){
	yzi('sendMessage',[
	'chat_id'=>$chatid,
	'text'=>$text,
	'parse_mode'=>$parsmde,
	'disable_web_page_preview'=>$disable_web_page_preview,
	'reply_markup'=>$keyboard
	]);
	}
function ForwardMessage($KojaShe,$AzKoja,$KodomMSG)
{
    yzi('ForwardMessage',[
        'chat_id'=>$KojaShe,
        'from_chat_id'=>$AzKoja,
        'message_id'=>$KodomMSG
    ]);
}
function deleteFolder($path){
    if (is_dir($path) === true) {
        $files = array_diff(scandir($path), array('.', '..'));
        foreach ($files as $file)
            deleteFolder(realpath($path) . '/' . $file);
            
        return rmdir($path);
    } else if (is_file($path) === true)
        return unlink($path);
 
    return false;
}
function save($filename,$TXTdata){
	$myfile = fopen($filename, "w") or die("Unable to open file!");
	fwrite($myfile, "$TXTdata");
	fclose($myfile);
	}

//============(config)==========
$token = "8874940402:AAFXnMVQT5xrpMSpQ4TcZ6K5quiGvIW3hOE"; //Token
$channel = "@Nim_Shab2"; //Channel ID with @
$id_support ="KHAN_Sohail_580"; //Support ID without @
$bot_id = "Helper_Yaser_VIP_Bot"; //Bot ID without @
$admin = "8650091524"; // آیدی عددی ادمین
$folder = ""; //Host and Folder
//==============================
$update = json_decode(file_get_contents("php://input"));
$message = $update->message;
$from_id = $update->message->from->id;
$chat_id = $update->message->chat->id;
$text = $update->message->text;
$first_name = $message->from->first_name;
$last_name = $message->from->last_name;
$username = $message->from->username;$command = file_get_contents("data/$from_id/command.txt");
@mkdir("data/$from_id");
$username = $update->message->from->username;
$truechannel = json_decode(file_get_contents("https://api.telegram.org/bot$token/getChatMember?chat_id=$channel&user_id=".$from_id));
$tch = $truechannel->result->status;
$state = file_get_contents("data/$from_id/state.txt");
$created = file_get_contents("data/$from_id/create.txt");
$my_id = file_get_contents("bots/$text/other/$from_id/my_id.txt"or"bots/$text/data/my_id.txt");
$user_bots = file_get_contents("data/$from_id/bots.txt");
$message_id = $update->message->message_id;
$da = $update->message->reply_to_message->forward_from->id;
$type = file_get_contents("data/$from_id/type.txt");
$Bots = file_get_contents("data/bots.txt");
$Members = file_get_contents("data/Member.txt");
$gold = file_get_contents("data/$from_id/gold.txt");
$bottype = file_get_contents("bots/$text/data/bottype.txt");
//==============start===========
$start = json_encode(['keyboard'=>[
[['text'=>'🌀ساخت ربات🌀']],
[['text'=>'پشتیبانی🍭'],['text'=>'حذف ربات🗂']],
[['text'=>'کد رایگان🍫']],
[['text'=>'حساب کاربری من👤'],['text'=>'ربات های من🏄🏻']],
[['text'=>'حساب ویژه👑'],['text'=>'بات اینفو⚙️']],
],'resize_keyboard'=>true]);
//==============================
$bet_info = json_encode(['keyboard'=>[
[['text'=>'زیرمجموعه گیری🔮'],['text'=>'امتیاز من💎']],
[['text'=>'ویژه کردن با زیرمجموعه💵'],['text'=>'انتقال امتیاز🍭']],
[['text'=>'بازگشت✖️️']],
],'resize_keyboard'=>true]);
//==============================
$start_admin = json_encode(['keyboard'=>[
[['text'=>'🌀ساخت ربات🌀']],
[['text'=>'پشتیبانی🍭'],['text'=>'حذف ربات🗂']],
[['text'=>'کد رایگان🍫']],
[['text'=>'حساب کاربری من👤'],['text'=>'ربات های من🏄🏻']],
[['text'=>'حساب ویژه👑'],['text'=>'بات اینفو⚙️']],
],'resize_keyboard'=>true]);
//==============================
$Create_b = json_encode(['keyboard'=>[
[['text'=>'ست وب هوک🔩️'],['text'=>'پیامرسان💬️']],
[['text'=>'️️مبدل فایل🤹‍♂️']],
[['text'=>'جست و جوی موزیک🎙'],['text'=>'فونت ساز🎭']],
[['text'=>'بازی XO🎲'],['text'=>'حرف ناشناس💍']],
[['text'=>'بازگشت✖️️']],
],'resize_keyboard'=>true]);
//===========(manage)===========
$button_manage = json_encode(['keyboard'=>[
[['text'=>'ساخت ربات⚙️'],['text'=>'حذف ربات🗂']],
[['text'=>'🎁ساخت کد']],
[['text'=>'ویژه کردن🎉'],['text'=>'🔻ربات ها']],
[['text'=>'حذف حساب ویژه❌']],
[['text'=>'💬فوروارد'],['text'=>'🎈آمار']],
[['text'=>'امتیاز به کاربر💲'],['text'=>'کم کردن امتیاز کاربر⚠️']],
[['text'=>'بازگشت✖️️']],
],'resize_keyboard'=>true]);
//==============================
$button_back = json_encode(['keyboard'=>[
[['text'=>'بازگشت✖️️']],
],'resize_keyboard'=>true]);
//==============================

if(preg_match('/^\/([Ss]tart)(.*)/',$text)){
file_put_contents("data/$from_id/state.txt","none");
preg_match('/^\/([Ss]tart)(.*)/',$text,$match);
$match[2] = str_replace(" ","",$match[2]);
$match[2] = str_replace("\n","",$match[2]);
if($match[2] != $from_id){
if (strpos($Members , "$from_id") == false){
$joins = file_get_contents('data/'.$match[2]."/joins.txt");
$check_join = explode("\n",$joins);
if(!in_array($from_id,$check_join)){
$aaddd = file_get_contents('data/'.$match[2]."/gold.txt");
save('data/'.$match[2]."/gold.txt",$aaddd+1);
SendMessage($match[2],"یک نفر با لینک شما وارد ربات شد و شما یک سکه دریافت کردید🆒️","html","true");
}
$add2 = fopen("data/$match[2]/joins.txt","a");
fwrite($add2,"$from_id\n");
fclose($add2);
file_put_contents("data/$from_id/state.txt","none");
SendMessage($chat_id,"سلام کاربر  $first_name 😉👋🏻
💎به ربات ساز ما خوش آمدید

برای ساخت ربات دکمه (🌀ساخت ربات🌀 ) را بزنید❇️
🌀 $channel
🌐 @$bot_id
","html","true",$start);
file_put_contents("data/$from_id/state.txt","none");
}else{
SendMessage($chat_id,"سلام کاربر  $first_name 😉👋🏻
💎به ربات ساز ما خوش آمدید

برای ساخت ربات دکمه (🌀ساخت ربات🌀 ) را بزنید❇️
🌀 $channel
🌐 @$bot_id","html","true",$start);
}
}
}
elseif($tch != 'member' && $tch != 'creator' && $tch != 'administrator'){
SendMessage($chat_id,"🔸برای حمایت از ما و همچنان از ربات ابتدا وارد کانال زیر شوید👇
🆔 $channel
🔹روی عبارت join بزنید سپس به ربات برگشته و گزینه
🔸 /start
🔹را ارسال کنید تا دکمه های ربات نمایش داده شوند.","html","true",$button_remov);
return false;
}	
if($text == "بازگشت✖️️"){
file_put_contents("data/$from_id/state.txt","none");
SendMessage($chat_id,"سلام کاربر  $first_name 😉👋🏻
💎به ربات ساز ما خوش آمدید

برای ساخت ربات دکمه (🌀ساخت ربات🌀 ) را بزنید❇️
🌀 $channel
🌐 @$bot_id","html","true",$start);
}
//========(Create Bot)=========
if($text =="🌀ساخت ربات🌀"){
SendMessage($chat_id,"💎یک ربات انتخاب کنید:","html","true",$Create_b);
}
if($text == "پیامرسان💬️"){
file_put_contents("data/$from_id/state.txt","create_pm");
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"توکن را ارسال کنید🎯",
'parse_mode'=>'Markdown', 
'reply_markup'=>json_encode([ 
'resize_keyboard'=>true,
            'keyboard'=>[
                [
                ['text'=>"بازگشت✖️️"],
                ]
              ],
])
]);
}
if($text == "حرف ناشناس💍"){
file_put_contents("data/$from_id/state.txt","create_harf");
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"توکن را ارسال کنید🎯",
'parse_mode'=>'Markdown', 
'reply_markup'=>json_encode([ 
'resize_keyboard'=>true,
            'keyboard'=>[
                [
                ['text'=>"بازگشت✖️️"],
                ]
              ],
])
]);
}
if($text == "ست وب هوک🔩️"){
file_put_contents("data/$from_id/state.txt","create_setwebhook");
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"توکن را ارسال کنید🎯",
'parse_mode'=>'Markdown', 
'reply_markup'=>json_encode([ 
'resize_keyboard'=>true,
            'keyboard'=>[
                [
                ['text'=>"بازگشت✖️️"],
                ]
              ],
])
]);
}

if($text == "فونت ساز🎭"){
file_put_contents("data/$from_id/state.txt","create_font");
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"توکن را ارسال کنید🎯",
'parse_mode'=>'Markdown', 
'reply_markup'=>json_encode([ 
'resize_keyboard'=>true,
            'keyboard'=>[
                [
                ['text'=>"بازگشت✖️️"],
                ]
              ],
])
]);
}

if($text == "بازی XO🎲"){
file_put_contents("data/$from_id/state.txt","create_XO");
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"توکن را ارسال کنید🎯",
'parse_mode'=>'Markdown', 
'reply_markup'=>json_encode([ 
'resize_keyboard'=>true,
            'keyboard'=>[
                [
                ['text'=>"بازگشت✖️️"],
                ]
              ],
])
]);
}
if($text == "️️مبدل فایل🤹‍♂️"){
file_put_contents("data/$from_id/state.txt","create_File");
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"توکن را ارسال کنید🎯",
'parse_mode'=>'Markdown', 
'reply_markup'=>json_encode([ 
'resize_keyboard'=>true,
            'keyboard'=>[
                [
                ['text'=>"بازگشت✖️️"],
                ]
              ],
])
]);
}
if($text == "جست و جوی موزیک🎙"){
file_put_contents("data/$from_id/state.txt","create_music");
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"توکن را ارسال کنید🎯",
'parse_mode'=>'Markdown', 
'reply_markup'=>json_encode([ 
'resize_keyboard'=>true,
            'keyboard'=>[
                [
                ['text'=>"بازگشت✖️️"],
                ]
              ],
])
]);
}

if($state == "create_pm" && $text !="بازگشت✖️️"){
			function objectToArrays( $object ) {
				if( !is_object( $object ) && !is_array( $object ) )
				{
				return $object;
				}
				if( is_object( $object ) )
				{
				$object = get_object_vars( $object );
				}
			return array_map( "objectToArrays", $object );
			}
$userbot = json_decode(file_get_contents("https://api.telegram.org/bot".$text."/getme"));
	$resultb = objectToArrays($userbot);
	$un = $resultb["result"]["username"];
	$ok = $resultb["ok"];
		if($ok != 1) {
			//Token Not True

yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"
توکن نامعتبر است،لطفا یک توکن معتبر ارسال کنید💢"
  ]);
}else{
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"درحال ساخت...",
  ]);
  
if($type =="Gold"){
file_put_contents("bots/$un/data/bottype.txt","gold");
}else{
file_put_contents("bots/$un/data/bottype.txt","free");
}
 //=================================
mkdir("bots/$un");
mkdir("bots/$un/data");
file_put_contents("bots/$un/data/my_id.txt","$from_id");
file_put_contents("bots/$un/other/$from_id/my_id.txt","$from_id");
file_put_contents("data/$from_id/state.txt","none");
		$source = file_get_contents("source/pv/index.php");
		$source = str_replace("[TOKEN]",$text,$source);
		$source = str_replace("[ADMIN]",$from_id,$source);
file_put_contents("bots/$un/index.php",$source);
//==================================
file_get_contents("https://api.telegram.org/bot".$text."/setwebhook?url=".$folder."/bots/".$un."/index.php");
file_put_contents("data/$from_id/create.txt","yes");
 $users = file_get_contents('data/bots.txt');
    $member = explode("\n",$users);
    if (!in_array($un,$member)){
$add_bot = file_get_contents('data/bots.txt');
$add_bot .= $un."\n";
file_put_contents('data/bots.txt',$add_bot);
}
$user_b = file_get_contents("data/$from_id/bots.txt");
$member_b = explode("\n",$user_b);
if (!in_array($un,$member_b)){
$add_bot = file_get_contents("data/$from_id/bots.txt");
$add_bot .= $un."\n";
file_put_contents("data/$from_id/bots.txt",$add_bot);
}
yzi('sendMessage',[
'chat_id'=>$admin,
'text'=>"ربات جدیدی ساخته شد😇
پیامرسان",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"ربات شما ساخته شد🎁",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
}
}
if($state == "create_harf" && $text !="بازگشت✖️️"){
			function objectToArrays( $object ) {
				if( !is_object( $object ) && !is_array( $object ) )
				{
				return $object;
				}
				if( is_object( $object ) )
				{
				$object = get_object_vars( $object );
				}
			return array_map( "objectToArrays", $object );
			}
$userbot = json_decode(file_get_contents("https://api.telegram.org/bot".$text."/getme"));
	$resultb = objectToArrays($userbot);
	$un = $resultb["result"]["username"];
	$ok = $resultb["ok"];
		if($ok != 1) {
			//Token Not True

yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"
توکن نامعتبر است،لطفا یک توکن معتبر ارسال کنید💢"
  ]);
}else{
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"درحال ساخت...",
  ]);
  
if($type =="Gold"){
file_put_contents("bots/$un/data/bottype.txt","gold");
}else{
file_put_contents("bots/$un/data/bottype.txt","free");
}
 //=================================
mkdir("bots/$un");
mkdir("bots/$un/data");
file_put_contents("bots/$un/data/my_id.txt","$from_id");
file_put_contents("data/$from_id/state.txt","none");
		$source = file_get_contents("source/harfnashenas/index.php");
		$source = str_replace("[TOKEN]",$text,$source);
		$source = str_replace("[ADMIN]",$from_id,$source);
		$source = str_replace("[USERBOT]",$un,$source);
file_put_contents("bots/$un/index.php",$source);
//==================================
file_get_contents("https://api.telegram.org/bot".$text."/setwebhook?url=".$folder."/bots/".$un."/index.php");
file_put_contents("data/$from_id/create.txt","yes");
 $users = file_get_contents('data/bots.txt');
    $member = explode("\n",$users);
    if (!in_array($un,$member)){
$add_bot = file_get_contents('data/bots.txt');
$add_bot .= $un."\n";
file_put_contents('data/bots.txt',$add_bot);
}
$user_b = file_get_contents("data/$from_id/bots.txt");
$member_b = explode("\n",$user_b);
if (!in_array($un,$member_b)){
$add_bot = file_get_contents("data/$from_id/bots.txt");
$add_bot .= $un."\n";
file_put_contents("data/$from_id/bots.txt",$add_bot);
}
yzi('sendMessage',[
'chat_id'=>$admin,
'text'=>"ربات جدیدی ساخته شد😇
حرف ناشناس",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"ربات شما ساخته شد🎁",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
}
}
if($state == "create_File" && $text !="بازگشت✖️️"){
			function objectToArrays( $object ) {
				if( !is_object( $object ) && !is_array( $object ) )
				{
				return $object;
				}
				if( is_object( $object ) )
				{
				$object = get_object_vars( $object );
				}
			return array_map( "objectToArrays", $object );
			}
$userbot = json_decode(file_get_contents("https://api.telegram.org/bot".$text."/getme"));
	$resultb = objectToArrays($userbot);
	$un = $resultb["result"]["username"];
	$ok = $resultb["ok"];
		if($ok != 1) {
			//Token Not True

yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"
توکن نامعتبر است،لطفا یک توکن معتبر ارسال کنید💢"
  ]);
}else{
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"درحال ساخت...",
  ]);
  
if($type =="Gold"){
file_put_contents("bots/$un/data/bottype.txt","gold");
}else{
file_put_contents("bots/$un/data/bottype.txt","free");
}
 //=================================
mkdir("bots/$un");
mkdir("bots/$un/data");
file_put_contents("bots/$un/data/my_id.txt","$from_id");
file_put_contents("bots/$un/other/$from_id/my_id.txt","$from_id");
file_put_contents("data/$from_id/state.txt","none");
		$source = file_get_contents("source/File/index.php");
		$source = str_replace("[TOKEN]",$text,$source);
		$source = str_replace("[ADMIN]",$from_id,$source);
file_put_contents("bots/$un/index.php",$source);
//==================================
file_get_contents("https://api.telegram.org/bot".$text."/setwebhook?url=".$folder."/bots/".$un."/index.php");
file_put_contents("data/$from_id/create.txt","yes");
 $users = file_get_contents('data/bots.txt');
    $member = explode("\n",$users);
    if (!in_array($un,$member)){
$add_bot = file_get_contents('data/bots.txt');
$add_bot .= $un."\n";
file_put_contents('data/bots.txt',$add_bot);
}
$user_b = file_get_contents("data/$from_id/bots.txt");
$member_b = explode("\n",$user_b);
if (!in_array($un,$member_b)){
$add_bot = file_get_contents("data/$from_id/bots.txt");
$add_bot .= $un."\n";
file_put_contents("data/$from_id/bots.txt",$add_bot);
}
yzi('sendMessage',[
'chat_id'=>$admin,
'text'=>"ربات جدیدی ساخته شد😇
تبدیل فایل",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"ربات شما ساخته شد🎁",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
}
}

if($state == "create_XO" && $text !="بازگشت✖️️"){
			function objectToArrays( $object ) {
				if( !is_object( $object ) && !is_array( $object ) )
				{
				return $object;
				}
				if( is_object( $object ) )
				{
				$object = get_object_vars( $object );
				}
			return array_map( "objectToArrays", $object );
			}
$userbot = json_decode(file_get_contents("https://api.telegram.org/bot".$text."/getme"));
	$resultb = objectToArrays($userbot);
	$un = $resultb["result"]["username"];
	$ok = $resultb["ok"];
		if($ok != 1) {
			//Token Not True

yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"
توکن نامعتبر است،لطفا یک توکن معتبر ارسال کنید💢"
  ]);
}else{
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"درحال ساخت...",
  ]);
  
if($type =="Gold"){
file_put_contents("bots/$un/data/bottype.txt","gold");
}else{
file_put_contents("bots/$un/data/bottype.txt","free");
}
 //=================================
mkdir("bots/$un");
mkdir("bots/$un/data");
file_put_contents("bots/$un/data/my_id.txt","$from_id");
file_put_contents("bots/$un/other/$from_id/my_id.txt","$from_id");
file_put_contents("data/$from_id/state.txt","none");
		$source = file_get_contents("source/XObot/index.php");
		$source = str_replace("[TOKEN]",$text,$source);
file_put_contents("bots/$un/index.php",$source);
//==================================
file_get_contents("https://api.telegram.org/bot".$text."/setwebhook?url=".$folder."/bots/".$un."/index.php");
file_put_contents("data/$from_id/create.txt","yes");
 $users = file_get_contents('data/bots.txt');
    $member = explode("\n",$users);
    if (!in_array($un,$member)){
$add_bot = file_get_contents('data/bots.txt');
$add_bot .= $un."\n";
file_put_contents('data/bots.txt',$add_bot);
}
$user_b = file_get_contents("data/$from_id/bots.txt");
$member_b = explode("\n",$user_b);
if (!in_array($un,$member_b)){
$add_bot = file_get_contents("data/$from_id/bots.txt");
$add_bot .= $un."\n";
file_put_contents("data/$from_id/bots.txt",$add_bot);
}
yzi('sendMessage',[
'chat_id'=>$admin,
'text'=>"ربات جدیدی ساخته شد😇
ربات XO",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"ربات شما ساخته شد🎁",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
}
}
if($state == "create_font" && $text !="بازگشت✖️️"){
			function objectToArrays( $object ) {
				if( !is_object( $object ) && !is_array( $object ) )
				{
				return $object;
				}
				if( is_object( $object ) )
				{
				$object = get_object_vars( $object );
				}
			return array_map( "objectToArrays", $object );
			}
$userbot = json_decode(file_get_contents("https://api.telegram.org/bot".$text."/getme"));
	$resultb = objectToArrays($userbot);
	$un = $resultb["result"]["username"];
	$ok = $resultb["ok"];
		if($ok != 1) {
			//Token Not True

yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"
توکن نامعتبر است،لطفا یک توکن معتبر ارسال کنید💢"
  ]);
}else{
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"درحال ساخت...",
  ]);
  
if($type =="Gold"){
file_put_contents("bots/$un/data/bottype.txt","gold");
}else{
file_put_contents("bots/$un/data/bottype.txt","free");
}
 //=================================
  mkdir("bots/$un");
  mkdir("bots/$un/data");
  file_put_contents("bots/$un/data/$from_id/my_id.txt","$from_id");
 //=================================

file_put_contents("data/$from_id/state.txt","none");
		$source = file_get_contents("source/font/index.php");
		$source = str_replace("[TOKEN]",$text,$source);
		$source = str_replace("[ADMIN]",$from_id,$source);
file_put_contents("bots/$un/index.php",$source);
file_get_contents("https://api.telegram.org/bot".$text."/setwebhook?url=".$folder."/bots/".$un."/index.php");
file_put_contents("data/$from_id/create.txt","yes");
 $users = file_get_contents('data/bots.txt');
    $member = explode("\n",$users);
    if (!in_array($un,$member)){
$add_bot = file_get_contents('data/bots.txt');
$add_bot .= $un."\n";
file_put_contents('data/bots.txt',$add_bot);
}
$user_b = file_get_contents("data/$from_id/bots.txt");
$member_b = explode("\n",$user_b);
if (!in_array($un,$member_b)){
$add_bot = file_get_contents("data/$from_id/bots.txt");
$add_bot .= $un."\n";
file_put_contents("data/$from_id/bots.txt",$add_bot);
}
yzi('sendMessage',[
'chat_id'=>$admin,
'text'=>"ربات جدیدی ساخته شد😇
فونت ساز",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"ربات شما ساخته شد🎁",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
 yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"به بات فادر رفته و حال اینلاین را فعال کنید تا ربات شما به درستی کار کند.",
  ]);
}
}

if($state == "create_setwebhook" && $text !="بازگشت✖️️"){
			function objectToArrays( $object ) {
				if( !is_object( $object ) && !is_array( $object ) )
				{
				return $object;
				}
				if( is_object( $object ) )
				{
				$object = get_object_vars( $object );
				}
			return array_map( "objectToArrays", $object );
			}
$userbot = json_decode(file_get_contents("https://api.telegram.org/bot".$text."/getme"));
	$resultb = objectToArrays($userbot);
	$un = $resultb["result"]["username"];
	$ok = $resultb["ok"];
		if($ok != 1) {
			//Token Not True

yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"
توکن نامعتبر است،لطفا یک توکن معتبر ارسال کنید💢"
  ]);
}else{
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"درحال ساخت...",
  ]);
  
if($type =="Gold"){
file_put_contents("bots/$un/data/bottype.txt","gold");
}else{
file_put_contents("bots/$un/data/bottype.txt","free");
}
 //=================================
  mkdir("bots/$un");
  file_put_contents("bots/$un/other/setting/start.txt","Hi!✋ 
  <b>Welcome To My bots</b>");
  file_put_contents("bots/$un/other/$from_id/my_id.txt","$from_id");
  file_put_contents("bots/$un/other/setting/send.txt","<b>Sent To My Admin!</b>");
 //=================================

mkdir("bots/$un/data");
file_put_contents("data/$from_id/state.txt","none");
		$source = file_get_contents("source/setwebhook/index.php");
		$source = str_replace("[TOKEN]",$text,$source);
		$source = str_replace("[ADMIN]",$from_id,$source);
file_put_contents("bots/$un/index.php",$source);
file_get_contents("https://api.telegram.org/bot".$text."/setwebhook?url=".$folder."/bots/".$un."/index.php");
file_put_contents("data/$from_id/create.txt","yes");
 $users = file_get_contents('data/bots.txt');
    $member = explode("\n",$users);
    if (!in_array($un,$member)){
$add_bot = file_get_contents('data/bots.txt');
$add_bot .= $un."\n";
file_put_contents('data/bots.txt',$add_bot);
}
$user_b = file_get_contents("data/$from_id/bots.txt");
$member_b = explode("\n",$user_b);
if (!in_array($un,$member_b)){
$add_bot = file_get_contents("data/$from_id/bots.txt");
$add_bot .= $un."\n";
file_put_contents("data/$from_id/bots.txt",$add_bot);
}
yzi('sendMessage',[
'chat_id'=>$admin,
'text'=>"ربات جدیدی ساخته شد😇",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"ربات شما ساخته شد🎁",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
}
}
if($state == "create_music" && $text !="بازگشت✖️️"){
			function objectToArrays( $object ) {
				if( !is_object( $object ) && !is_array( $object ) )
				{
				return $object;
				}
				if( is_object( $object ) )
				{
				$object = get_object_vars( $object );
				}
			return array_map( "objectToArrays", $object );
			}
$userbot = json_decode(file_get_contents("https://api.telegram.org/bot".$text."/getme"));
	$resultb = objectToArrays($userbot);
	$un = $resultb["result"]["username"];
	$ok = $resultb["ok"];
		if($ok != 1) {
			//Token Not True

yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"
توکن نامعتبر است،لطفا یک توکن معتبر ارسال کنید💢"
  ]);
}else{
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"درحال ساخت...",
  ]);
  
if($type =="Gold"){
file_put_contents("bots/$un/data/bottype.txt","gold");
}else{
file_put_contents("bots/$un/data/bottype.txt","free");
}
 //=================================
mkdir("bots/$un");
mkdir("bots/$un/data");
file_put_contents("bots/$un/data/my_id.txt","$from_id");
file_put_contents("bots/$un/other/$from_id/my_id.txt","$from_id");
file_put_contents("data/$from_id/state.txt","none");
		$source = file_get_contents("source/music/index.php");
		$source = str_replace("[TOKEN]",$text,$source);
		$source = str_replace("[ADMIN]",$from_id,$source);
		$source = str_replace("[BOTUSER]",$un,$source);
file_put_contents("bots/$un/index.php",$source);
file_get_contents("https://api.telegram.org/bot".$text."/setwebhook?url=".$folder."/bots/".$un."/index.php");
file_put_contents("data/$from_id/create.txt","yes");
 $users = file_get_contents('data/bots.txt');
    $member = explode("\n",$users);
    if (!in_array($un,$member)){
$add_bot = file_get_contents('data/bots.txt');
$add_bot .= $un."\n";
file_put_contents('data/bots.txt',$add_bot);
}
$user_b = file_get_contents("data/$from_id/bots.txt");
$member_b = explode("\n",$user_b);
if (!in_array($un,$member_b)){
$add_bot = file_get_contents("data/$from_id/bots.txt");
$add_bot .= $un."\n";
file_put_contents("data/$from_id/bots.txt",$add_bot);
}
yzi('sendMessage',[
'chat_id'=>$admin,
'text'=>"ربات جدیدی ساخته شد😇
🎙جست و جوی موزیک",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
yzi('sendMessage',[
'chat_id'=>$chat_id,
'text'=>"ربات شما ساخته شد🎁",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
	[
	['text'=>"@$un",'url'=>"https://t.me/$un"]
	]
    ]
    ])
  ]);
}
}

if($text == "حذف ربات🗂"){
if($created == "yes"){
file_put_contents("data/$from_id/state.txt","delete");
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"♠️آیدی ربات را بدون @ وارد کنید.
🔻به کوچک و بزرگی حروف دقت کنید.",
'parse_mode'=>'Markdown', 
'reply_markup'=>json_encode([ 
'resize_keyboard'=>true,
            'keyboard'=>[
                [
                ['text'=>"بازگشت✖️️"],
                ]
              ],
])
]);
}else{
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"شما رباتی در این ربات ساز ندارید❌",
'parse_mode'=>'Markdown', 
'reply_markup'=>json_encode([ 
'resize_keyboard'=>true,
            'keyboard'=>[
                [
                ['text'=>"بازگشت✖️️"],
                ]
              ],
])
]);
}
}

if($state =="delete" && $text !="بازگشت✖️️"){
if($from_id != $my_id  && $from_id != $admin){
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"حاجی ربات مال تو نیست😐😂",
]);
}else{
deletefolder("bots/$text");
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"🔺 با موفقیت حذف شد.",
]);
}
}

/*

بسم الله الرحمن الرحیم
! ----------------------- !
Source » ربات ساز !

Author » @m_y002

Channels » @GRT_Team | @MC_Source
! ----------------------- !
اسکی بدون ذکر منبع و نویسنده ممنوع می باشد !

*/

if($text=="بات اینفو⚙️"){
SendMessage($chat_id,"به بخش بات اینفو خوش آمدید😁","html","true",$bet_info);
}
if($text=="زیرمجموعه گیری🔮"){
SendMessage($chat_id,"https://t.me/$bot_id?start=$from_id

هرکس با لینک تو عضو ربات بشه یک امتیاز میگیری😃","html","true");
}
if($text=="ویژه کردن با زیرمجموعه💵"  && $text != "بازگشت✖️"){
if($gold >= 6){
file_put_contents("data/$from_id/state.txt","VIP12");
SendMessage($chat_id,"آیدی ربات خود را بدون @ وارد کنید","html","true",$button_back);
}else{
SendMessage($chat_id,"امتیازات شما کافی نمیباشد☹️","html","true");
}
}
if($text =="پشتیبانی🍭"){
file_put_contents("data/$from_id/state.txt","mok");
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"پیام خود را ارسال کنید✅ :
    برای اتمام چت با ادمین بازگشت را بزنید!",
'parse_mode'=>'Markdown', 
'reply_markup'=>json_encode([ 
'resize_keyboard'=>true,
            'keyboard'=>[
                [
                ['text'=>"بازگشت✖️️"],
                ]
              ],
])
]);
}
if($state == "mok" && $text !="بازگشت✖️") {
yzi('ForwardMessage',[
 'chat_id'=>$admin,
 'from_chat_id'=>$from_id,
 'message_id'=>$message_id
]);
}elseif($da != "" && $from_id == $admin){
yzi('sendMessage',[
'chat_id'=>$da,
 'text'=>$text,
'parse_mode'=>'MarkDown',
]);
yzi('sendMessage',[
 'chat_id'=>$chat_id,
 'text'=>"sent to user 😐",
'parse_mode'=>'MarkDown',
 ]);
}
if($text =="امتیاز من💎"){
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"▪️امتیاز شما : $gold امتیاز است .
▪️قیمت اکانت ویژه 6 امتیاز.",
]);
}
if($text =="ربات های من🏄🏻"){
 if($created == "yes"){
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"لیست ربات های شما🍬:

$user_bots",
]);
}else{
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"شما رباتی در ربات ساز ما ندارید❌",
]);
}
}

if($text =="حساب کاربری من👤"){
if($gold > 1){
if($type !="Gold"){
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"💠اطلاعات حساب شما :

📝 نام : $first_name $last_name

🔢آیدی عددی : $from_id

🆔 آیدی : @$username

🅰️نوع حساب : free

🎖 امتیاز : $gold
",
]);
}else{
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"💠اطلاعات حساب شما :

📝 نام : $first_name $last_name

🔢آیدی عددی : $from_id

🆔 آیدی : @$username

🅰️نوع حساب : $type

🎖 امتیاز : $gold
",
]);
}
}else{
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"💠اطلاعات حساب شما :

📝 نام : $first_name $last_name

🔢آیدی عددی : $from_id

🆔 آیدی : @$username

🅰️نوع حساب : $type

🎖 امتیاز : 0
",
]);
}
}
if($text =="حساب ویژه👑"){
yzi('sendmessage',[
'chat_id'=>$chat_id,
'text'=>"❇️پرداخت کنید !
🔸اکانت ویژه  تنها 2000 تومان",
'reply_markup'=>json_encode([ 
'resize_keyboard'=>true,
            'inline_keyboard'=>[
                [
                ['text'=>"پرداخت️",'url'=>'https://www.payping.ir/d/7cnA'],
                ]
              ],
])
]);
}
if($text == "ویژه کردن🎉" &&  $from_id == $admin){
  file_put_contents("data/$from_id/state.txt","VIP");
  SendMessage($chat_id,"الا آیدی رباتتان را بدون @ بفرست.
لطفا به حروف کوچک و بزرگ آیدی دقت کنید🤗","html","true",$button_back);
}
if($state == "VIP" && $text !="بازگشت✖️️"){
 file_put_contents("data/$from_id/state.txt","none");
file_put_contents("data/$from_id/type.txt","Gold");
file_put_contents("bots/$text/data/bottype.txt","gold");
  SendMessage($chat_id,"ویژه شد","html","true",$button_back);
}
if($state == "VIP12" && $text !="بازگشت✖️️"){
if($bottype != "gold"){
if(file_exists("bots/$text/index.php")){
file_put_contents("data/$from_id/state.txt","none");
file_put_contents("data/$from_id/type.txt","Gold");
file_put_contents("bots/$text/data/bottype.txt","gold");
$kam = $gold - 6;
file_put_contents("data/$from_id/gold.txt","$kam");
  SendMessage($chat_id,"ربات مورد نظر ویژه شد🤑","html","true",$button_back);
}else{
file_put_contents("data/$from_id/state.txt","none");
 SendMessage($chat_id,"ربات وجود ندارد😕","html","true",$start);
}
}else{
file_put_contents("data/$from_id/state.txt","none");
 SendMessage($chat_id,"ربات از اول ویژه بود😐","html","true",$button_back);
}
}
if($text == "حذف حساب ویژه❌" && $from_id == $admin){
  file_put_contents("data/$from_id/state.txt","delete_VIP");
  SendMessage($chat_id,"الا آیدی رباتتان را بدون @ بفرست.
لطفا به حروف کوچک و بزرگ آیدی دقت کنید🤗","html","true",$button_back);
}
if($state == "delete_VIP" && $text !="بازگشت✖️"){
 file_put_contents("data/$from_id/state.txt","none");
file_put_contents("data/$from_id/type.txt","Free");
file_put_contents("bots/$text/data/bottype.txt","Free");
  SendMessage($chat_id,"ویژه شد","html","true",$button_back);
}
if($text == "کد رایگان🍫"){
file_put_contents("data/$from_id/state.txt","code");
SendMessage($chat_id,"کد را وارد کنید","html","true",$button_back);
}
if($text =="کم کردن امتیاز کاربر⚠️" && $from_id == $admin){
file_put_contents("data/$from_id/state.txt","kam_kar");
SendMessage($chat_id,"🔹آیدی عددی کاربر را ارسال کنید","html","true",$button_back);
}
if($state == "kam_kar"){
file_put_contents("data/$from_id/kam_id.txt","$text");
file_put_contents("data/$from_id/state.txt","kam_kar_ted");
SendMessage($chat_id,"تعداد امتیاز را ارسال کنید","html","true",$button_back);
}
if($state == "kam_kar_ted"){
$kam_id = file_get_contents("data/$from_id/kam_id.txt");
$kam = $gold -$text;
file_put_contents("data/$kam_id/gold.txt","$kam");
file_put_contents("data/$from_id/state.txt","none");
file_put_contents("data/$from_id/kam_id.txt","none");
SendMessage($chat_id,"میزان $text سکه از کاربر کم شد.","html","true",$button_back);
}
if($text =="امتیاز به کاربر💲" && $from_id == $admin){
file_put_contents("data/$from_id/state.txt","be_kar");
SendMessage($chat_id,"🔹آیدی عددی کاربر را ارسال کنید","html","true",$button_back);
}
if($state == "be_kar"){
file_put_contents("data/$from_id/be_id.txt","$text");
file_put_contents("data/$from_id/state.txt","be_kar_ted");
SendMessage($chat_id,"تعداد امتیاز را ارسال کنید","html","true",$button_back);
}
if($state == "be_kar_ted"){
$be_id = file_get_contents("data/$from_id/be_id.txt");
$kam = $gold +$text;
file_put_contents("data/$be_id/gold.txt","$kam");
file_put_contents("data/$from_id/state.txt","none");
file_put_contents("data/$from_id/be_id.txt","none");
SendMessage($chat_id,"میزان $text امتیاز به کاربر اضافه شد !","html","true",$button_back);
}
if($text =="انتقال امتیاز🍭" && $text !="بازگشت✖️️"){
file_put_contents("data/$from_id/state.txt","kodom");
SendMessage($chat_id,"🔹آیدی عددی کاربر را ارسال کنید","html","true",$button_back);
}
if($state == "kodom" && $text !="بازگشت✖️️"){
if(file_exists("data/$text/state.txt")){
file_put_contents("data/$from_id/kodom.txt","$text");
file_put_contents("data/$from_id/state.txt","ine");
SendMessage($chat_id,"تعداد امتیاز را ارسال کنید","html","true",$button_back);
}else{
file_put_contents("data/$from_id/state.txt","none");
file_put_contents("data/$from_id/kodom.txt","none");
SendMessage($chat_id,"کاربر در ربات عضو نیست","html","true",$button_back);
}
}
if($state == "ine" && $text !="بازگشت✖️️"){
if($gold > $text){
$kodom = file_get_contents("data/$from_id/kodom.txt");
$kamas = $gold +$text;
file_put_contents("data/$kodom/gold.txt","$kamas");
$kame = $gold -$text;
file_put_contents("data/$from_id/gold.txt","$kame");
file_put_contents("data/$from_id/state.txt","none");
file_put_contents("data/$from_id/kodom.txt","none");
SendMessage($chat_id,"میزان $text امتیاز به کاربر اضافه شد !","html","true",$start);
SendMessage($kodom,"کاربر @$username به میزان $text امتیاز به شما هدیه کردند.","html","true",$start);
}else{
file_put_contents("data/$from_id/state.txt","none");
file_put_contents("data/$from_id/kodom.txt","none");
SendMessage($chat_id,"امتیاز کافی نیست","html","true",$start);
}
}
//=========================
if($state == 'code' && $text !="بازگشت✖️️"){
  if(file_exists("code/$text.txt")){
  $code = file_get_contents("code/$text.txt");
  if($code == 'true'){
  SendMessage($chat_id,"کد استفاده شده😕","html","true");
  }else{
  save("data/$from_id/state.txt","code free");
  unlink("code/$text.txt");
  SendMessage($chat_id,"الا آیدی رباتتان را بدون @ بفرست.
لطفا به حروف کوچک و بزرگ آیدی دقت کنید🤗","html","true",$button_back);
  }
  }else{
  SendMessage($chat_id,"کدی که فرستادی اصلا وجود نداره😂","html","true");
  }
  }
if($state == "code free" && $text !="بازگشت✖️️"){
file_put_contents("data/$from_id/type.txt","gold");
file_put_contents("bots/$text/data/bottype.txt","gold");
file_put_contents("data/$from_id/state.txt","none");
  SendMessage($chat_id,"ربات شما ویژه شد👌","html","true");
  SendMessage($channel,"
😎اطلاعات استفاده کننده از کد👇

👤نام : $first_name $last_name
🆔 آیدی : @$username

🤖آیدی ربات : @$text

🆑 $channel
🤖 @$bot_id","html","true");
}
//=========================
 if($text == '/panel' and $from_id == $admin){
  SendMessage($chat_id,"به پنل مدیریت خوش اومدی","html","true",$button_manage);
  }
  elseif($text == '🎈آمار' and $from_id == $admin){
	$txtt = file_get_contents('data/Member.txt');
    $member_id = explode("\n",$txtt);
    $mmeyziount = count($member_id) -1;
	SendMessage($chat_id,"کل کاربران: $mmeyziount نفر","html","true");
	}
  elseif($text == '💬فوروارد' and $from_id == $admin && $text !="بازگشت✖️️"){
	file_put_contents("data/".$from_id."/command.txt","s2a fwd");
	SendMessage($chat_id,"پیام مورد نظر را فوروارد کنید","html","true");
	}
	elseif($command == 's2a fwd' && $text !="بازگشت✖️️"){
	file_put_contents("data/".$from_id."/command.txt","none");
	SendMessage($chat_id,"پیام شما در صف ارسال قرار گرفت.","html","true",$button_manage);
	$all_member = fopen( "data/Member.txt", 'r');
		while( !feof( $all_member)) {
 			$user = fgets( $all_member);
yzi('ForwardMessage',[
 'chat_id'=>$user,
 'from_chat_id'=>$admin,
 'message_id'=>$message_id
 ]);
 }
}
//==================================
if($text =="🔻ربات ها"  && $from_id == $admin){
SendMessage($chat_id,"آیدی ربات های ساخته شده به شرح زیر می باشد😗
$Bots","html","true",$button_back);
}
if($text =="🎁ساخت کد" && $from_id == $admin){
file_put_contents("data/$from_id/state.txt","CreateCode");
SendMessage($chat_id,"کد را وارد کنید","html","true",$button_back);
}
if($state == "CreateCode"){
file_put_contents("code/$text.txt","$text");
file_put_contents("data/$from_id/state.txt","none");
SendMessage($chat_id,"کد ساخته شد.","html","true",$button_back);
yzi('sendMessage',[
'chat_id'=>$channel,
'text'=>"کد جدیدی ساخته شد✅

1-برای استفاده از کد وارد ربات (@$bot_id ) شوید.

2-روی گزینه (کد رایگان🍫) کلیک کنید.
3-کد را وارد کنید.
4- آیدی ربات خود را وارد کنید .

🎟 code: $text
🏅 @$bot_id",
  ]);
}
//==================================
	  // End Source
 $user = file_get_contents('data/Member.txt');
    $members = explode("\n",$user);
    if (!in_array($chat_id,$members)){
      $add_user = file_get_contents('data/Member.txt');
      $add_user .= $chat_id."\n";
     file_put_contents('data/Member.txt',$add_user);
    }
unlink("error_log");

/*

بسم الله الرحمن الرحیم

! ----------------------- !
Source » ربات ساز !

Author » @m_y002

Channels » @GRT_Team | @MC_Source
! ----------------------- !
اسکی بدون ذکر منبع و نویسنده ممنوع می باشد !

*/

?>