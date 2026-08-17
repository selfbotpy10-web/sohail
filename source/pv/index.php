<?php
# ! -- @GRT_Team | @MC_Source -- !
ob_start();
define('API_KEY',"[TOKEN]");
 
function bot($method,$datas=[]){
    $url = "https://api.telegram.org/bot".API_KEY."/".$method;
    $ch = curl_init();
    curl_setopt($ch,CURLOPT_URL,$url);
    curl_setopt($ch,CURLOPT_RETURNTRANSFER,true);
    curl_setopt($ch,CURLOPT_POSTFIELDS,http_build_query($datas));
    $res = curl_exec($ch);
    if(curl_error($ch)){
        var_dump(curl_error($ch));
    }else{
        return json_decode($res);
    }
}
$up=json_decode(file_get_contents('php://input'));
$sudo=[ADMIN];
$caption=$up->message->caption;
$fwd_id=$up->message->reply_to_message->forward_from->id;
$first_name=$up->message->from->first_name;
$last_name=$up->message->from->last_name;
$msg_id=$up->message->message_id;
$username=$up->message->from->username;
$chat_id=$up->message->chat->id;
$from_id=$up->message->from->id;
$bottype = file_get_contents("data/bottype.txt");
if(!file_exists("sudo.txt")){
  file_put_contents("sudo.txt","empty");
}
$vaziyat=file_get_contents("sudo.txt");
if(!file_exists("member.txt")){
  file_put_contents("member.txt","$sudo");
}
if(file_exists("dasturat.txt")){
  unlink("dasturat.txt");
}
if(!file_exists("profile.txt")){
  file_put_contents("profile.txt","پروفایل خالی است.");
}
if(!file_exists("dasturat.json")){
  file_put_contents("dasturat.json",json_encode(["empty"=>"yes"]));
}
if(!file_exists("start.txt")){
  file_put_contents("start.txt","باسلام.خوش آمدید.\nلطفا پیام خود را ارسال نمایید.");
}
if(!file_exists("block.txt")){
  file_put_contents("block.txt","block");
}
$text=$up->message->text;
$member=file("member.txt");
if(isset($up->message)){
  if($from_id==$sudo){
    if($text=="لغو" and $vaziyat!="empty"){
      file_put_contents("sudo.txt","empty");
      var_dump(bot("sendMessage",[
        "chat_id"=>$chat_id,
        "text"=>"_عملیات لغو شد._",
        "parse_mode"=>"markdown",
        "reply_markup"=>json_encode(["remove_keyboard"=>true])
      ]));
    }elseif($vaziyat=="hazfdastur"){
     
 $json=json_decode(file_get_contents("dasturat.json"),true);    
 if(isset($json[$text]) && $text!="empty"){
        unset($json[$text]);
        $json=json_encode($json);
        file_put_contents("dasturat.json","$json");
        file_put_contents("sudo.txt","empty");
        var_dump(bot("sendMessage",[
        "chat_id"=>$chat_id,
        "text"=>"_دستور مورد نظر حذف شد._",
        "parse_mode"=>"markdown",
        "reply_markup"=>json_encode(["remove_keyboard"=>true])
      ]));
      }else{
        var_dump(bot("sendMessage",[
        "chat_id"=>$chat_id,
        "text"=>"_این دستور موجود نیست._",
        "parse_mode"=>"markdown"
      ]));
      }
    }elseif($vaziyat=="forward"){
      foreach($member as $key=>$value){
        $id=$value+0;
        var_dump(bot("forwardMessage",[
          "chat_id"=>$id,
          "from_chat_id"=>$chat_id,
          "message_id"=>$msg_id
        ]));
      }
      
      var_dump(bot("sendMessage",[
        "chat_id"=>$chat_id,
        "text"=>"_پیام شما با موفقیت به تمام کاربران ارسال شد._",
        "parse_mode"=>"markdown",
        "reply_markup"=>json_encode(["remove_keyboard"=>true])
      ]));
      file_put_contents("sudo.txt","empty");
    }elseif($vaziyat=="forward2"){
      if(isset($up->message->text)){
        foreach($member as $key=>$value){
        $id=$value+0;
        var_dump(bot("sendMessage",[
          "chat_id"=>$id,
          "text"=>$text
        ]));
      }
      var_dump(bot("sendMessage",[
        "chat_id"=>$chat_id,
        "text"=>"_پیام شما با موفقیت به تمام کاربران ارسال شد._",
        "parse_mode"=>"markdown",
        "reply_markup"=>json_encode(["remove_keyboard"=>true])
      ]));
      file_put_contents("sudo.txt","empty");
      }elseif(isset($up->message->photo)){
        $up2=json_decode(file_get_contents("php://input"),true);
        $file_id=$up2["message"]["photo"][0]["file_id"];
        foreach($member as $key=>$value){
        $id=$value+0;
        var_dump(bot("sendphoto",[
          "chat_id"=>$id,
          "photo"=>$file_id,
          "caption"=>$caption
        ]));
      }
      var_dump(bot("sendMessage",[
        "chat_id"=>$chat_id,
        "text"=>"_پیام شما با موفقیت به تمام کاربران ارسال شد._",
        "parse_mode"=>"markdown",
        "reply_markup"=>json_encode(["remove_keyboard"=>true])
      ]));
      file_put_contents("sudo.txt","empty");
      }elseif(isset($up->message->audio)){
        $file_id=$up->message->audio->file_id;
        foreach($member as $key=>$value){
        $id=$value+0;
        var_dump(bot("sendaudio",[
          "chat_id"=>$id,
          "caption"=>$caption,
          "audio"=>$file_id
        ]));
      }
      var_dump(bot("sendMessage",[
        "chat_id"=>$chat_id,
        "text"=>"_پیام شما با موفقیت به تمام کاربران ارسال شد._",
        "parse_mode"=>"markdown",
        "reply_markup"=>json_encode(["remove_keyboard"=>true])
      ]));
      file_put_contents("sudo.txt","empty");
      }elseif(isset($up->message->document)){
        $file_id=$up->message->document->file_id;
        foreach($member as $key=>$value){
        $id=$value+0;
        var_dump(bot("senddocument",[
          "chat_id"=>$id,
          "document"=>$file_id,
          "caption"=>$caption
        ]));
      }
      var_dump(bot("sendMessage",[
        "chat_id"=>$chat_id,
        "text"=>"_پیام شما با موفقیت به تمام کاربران ارسال شد._",
        "parse_mode"=>"markdown",
        "reply_markup"=>json_encode(["remove_keyboard"=>true])
      ]));
      file_put_contents("sudo.txt","empty");
      }elseif(isset($up->message->video_note)){
        $file_id=$up->message->video_note->file_id;
        foreach($member as $key=>$value){
        $id=$value+0;
        var_dump(bot("sendvideonote",[
          "chat_id"=>$id,
          "video_note"=>$file_id
        ]));
      }
      var_dump(bot("sendMessage",[
        "chat_id"=>$chat_id,
        "text"=>"_پیام شما با موفقیت به تمام کاربران ارسال شد._",
        "parse_mode"=>"markdown",
        "reply_markup"=>json_encode(["remove_keyboard"=>true])
      ]));
      file_put_contents("sudo.txt","empty");
      }elseif(isset($up->message->video)){
        $file_id=$up->message->video->file_id;
        foreach($member as $key=>$value){
        $id=$value+0;
        var_dump(bot("sendvideo",[
          "chat_id"=>$id,
          "video"=>$file_id,
          "caption"=>$caption
        ]));
      }
      var_dump(bot("sendMessage",[
        "chat_id"=>$chat_id,
        "text"=>"_پیام شما با موفقیت به تمام کاربران ارسال شد._",
        "parse_mode"=>"markdown",
        "reply_markup"=>json_encode(["remove_keyboard"=>true])
      ]));
      file_put_contents("sudo.txt","empty");
      }elseif(isset($up->message->sticker)){
        $file_id=$up->message->sticker->file_id;
        foreach($member as $key=>$value){
        $id=$value+0;
        var_dump(bot("sendsticker",[
          "chat_id"=>$id,
          "sticker"=>$file_id
        ]));
      }
      var_dump(bot("sendMessage",[
        "chat_id"=>$chat_id,
        "text"=>"_پیام شما با موفقیت به تمام کاربران ارسال شد._",
        "parse_mode"=>"markdown",
        "reply_markup"=>json_encode(["remove_keyboard"=>true])
      ])); file_put_contents("sudo.txt","empty");
      }elseif(isset($up->message->voice)){
        $file_id=$up->message->voice->file_id;
        foreach($member as $key=>$value){
        $id=$value+0;
        var_dump(bot("sendvoice",[
          "chat_id"=>$id,
          "voice"=>$file_id,
          "caption"=>$caption
        ]));
      }
      var_dump(bot("sendMessage",[
        "chat_id"=>$chat_id,
        "text"=>"_پیام شما با موفقیت به تمام کاربران ارسال شد._",
        "parse_mode"=>"markdown",
        "reply_markup"=>json_encode(["remove_keyboard"=>true])
      ]));
      file_put_contents("sudo.txt","empty");
      }
    }elseif($vaziyat=="profile"){
      if(isset($up->message->text)){
        var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_پیام پروفایل ذخیره شد._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["remove_keyboard"=>true])
        ]));
        file_put_contents("sudo.txt","empty");
        file_put_contents("profile.txt","$text");
      }else{
        var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_پیام فقط باید حاوی متن باشد._",
          "parse_mode"=>"markdown"
        ]));
      }
    }elseif($vaziyat=="dasturjadid"){
      $json=json_decode(file_get_contents("dasturat.json"),true);
      if(isset($up->message->text)){
        if(!isset($json[$text]) && $text!="empty" && $text!="/start" && $text!="پروفایل"){
          file_put_contents("dastur.txt","$text");
          file_put_contents("sudo.txt","pasokh");
          var_dump(bot("sendMessage",[
          "chat_id"=>$chat_id,
          "text"=>"_حال پاسخ پیام خود را ارسال کنید._",
          "parse_mode"=>"markdown"
        ]));
        }else{
          var_dump(bot("sendMessage",[
          "chat_id"=>$chat_id,
          "text"=>"_این دستور از قبل موجود است._",
          "parse_mode"=>"markdown"
        ]));
        }
      }else{
        var_dump(bot("sendMessage",[
          "chat_id"=>$chat_id,
          "text"=>"_دستور فقط باید متن باشد._",
          "parse_mode"=>"markdown"
        ]));
      }
    }elseif($vaziyat=="pasokh"){
      if(isset($up->message->text)){
   $json=json_decode(file_get_contents("dasturat.json"),true);
          $json[file_get_contents("dastur.txt")]["text"]="$text";
          $json=json_encode($json);
          file_put_contents("dasturat.json","$json");
         file_put_contents("sudo.txt","empty");
         $file=fopen("dasturat.txt","a");
         $dastur=file_get_contents("dastur.txt");
         fwrite($file,",$dastur");
         fclose($file);
            var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_دستور شما ذخیره شد._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["remove_keyboard"=>true])
        ]));
      }elseif(isset($up->message->photo)){
        $json=json_decode(file_get_contents("dasturat.json"),true);
        $up2=json_decode(file_get_contents("php://input"),true);
        $json[file_get_contents("dastur.txt")]["file_id"]=$up2["message"]["photo"][0]["file_id"];
        $json[file_get_contents("dastur.txt")]["caption"]="$caption";
        $json[file_get_contents("dastur.txt")]["type"]="photo";
        $json=json_encode($json);
        file_put_contents("dasturat.json","$json");
         file_put_contents("sudo.txt","empty");
         $file=fopen("dasturat.txt","a");
         fwrite($file,file_get_contents("dastur.txt")."\n");
         fclose($file);
            var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_دستور شما ذخیره شد._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["remove_keyboard"=>true])
        ]));
      }elseif(isset($up->message->video)){
        $json=json_decode(file_get_contents("dasturat.json"),true);
        $json[file_get_contents("dastur.txt")]["caption"]="$caption";
        $json[file_get_contents("dastur.txt")]["file_id"]=$up->message->video->file_id;
        $json[file_get_contents("dastur.txt")]["type"]="video";
        $json=json_encode($json);
        file_put_contents("dasturat.json","$json");
         file_put_contents("sudo.txt","empty");
         $file=fopen("dasturat.txt","a");
         fwrite($file,file_get_contents("dastur.txt")."\n");
         fclose($file);
            var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_دستور شما ذخیره شد._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["remove_keyboard"=>true])
        ]));
      }elseif(isset($up->message->video_note)){
        $json=json_decode(file_get_contents("dasturat.json"),true);
        $json[file_get_contents("dastur.txt")]["file_id"]=$up->message->video_note->file_id;
        $json[file_get_contents("dastur.txt")]["type"]="video_note";
        $json=json_encode($json);
        file_put_contents("dasturat.json","$json");
         file_put_contents("sudo.txt","empty");
         $file=fopen("dasturat.txt","a");
         fwrite($file,file_get_contents("dastur.txt")."\n");
         fclose($file);
            var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_دستور شما ذخیره شد._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["remove_keyboard"=>true])
        ]));
      }elseif(isset($up->message->sticker)){
        $json=json_decode(file_get_contents("dasturat.json"),true);
        $json[file_get_contents("dastur.txt")]["file_id"]=$up->message->sticker->file_id;
        $json[file_get_contents("dastur.txt")]["type"]="sticker";
        $json=json_encode($json);
        file_put_contents("dasturat.json","$json");
         file_put_contents("sudo.txt","empty");
         $file=fopen("dasturat.txt","a");
         fwrite($file,file_get_contents("dastur.txt")."\n");
         fclose($file);
            var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_دستور شما ذخیره شد._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["remove_keyboard"=>true])
        ]));
      }elseif(isset($up->message->voice)){
        $json=json_decode(file_get_contents("dasturat.json"),true);
        $json[file_get_contents("dastur.txt")]["caption"]="$caption";
        $json[file_get_contents("dastur.txt")]["file_id"]=$up->message->voice->file_id;
        $json[file_get_contents("dastur.txt")]["type"]="voice";
        $json=json_encode($json);
        file_put_contents("dasturat.json","$json");
         file_put_contents("sudo.txt","empty");
         $file=fopen("dasturat.txt","a");
         fwrite($file,file_get_contents("dastur.txt")."\n");
         fclose($file);
            var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_دستور شما ذخیره شد._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["remove_keyboard"=>true])
        ]));
      }elseif(isset($up->message->audio)){
        $json=json_decode(file_get_contents("dasturat.json"),true);
        $json[file_get_contents("dastur.txt")]["caption"]="$caption";
        $json[file_get_contents("dastur.txt")]["file_id"]=$up->message->audio->file_id;
        $json[file_get_contents("dastur.txt")]["type"]="audio";
        $json=json_encode($json);
        file_put_contents("dasturat.json","$json");
         file_put_contents("sudo.txt","empty");
         $file=fopen("dasturat.txt","a");
         fwrite($file,file_get_contents("dastur.txt")."\n");
         fclose($file);
            var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_دستور شما ذخیره شد._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["remove_keyboard"=>true])
        ]));
      }elseif(isset($up->message->document)){
        $json=json_decode(file_get_contents("dasturat.json"),true);
        $json[file_get_contents("dastur.txt")]["caption"]="$caption";
        $json[file_get_contents("dastur.txt")]["file_id"]=$up->message->document->file_id;
        $json[file_get_contents("dastur.txt")]["type"]="document";
        $json=json_encode($json);
        file_put_contents("dasturat.json","$json");
         file_put_contents("sudo.txt","empty");
         $file=fopen("dasturat.txt","a");
         fwrite($file,file_get_contents("dastur.txt")."\n");
         fclose($file);
            var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_دستور شما ذخیره شد._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["remove_keyboard"=>true])
        ]));
      }
    }elseif($vaziyat=="start"){
      if(isset($up->message->text)){
        var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_پیام دستور استارت تغییر کرد._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["remove_keyboard"=>true])
        ]));
        file_put_contents("sudo.txt","empty");
        file_put_contents("start.txt","$text");
      }else{
        var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_پیام فقط باید حاوی متن باشد._",
          "parse_mode"=>"markdown"
        ]));
      }
    }elseif($text=="/block" and isset($up->message->reply_to_message->forward_from->id) and $fwd_id!=$sudo){
      $file=fopen("block.txt","a");
      fwrite($file,"\n$fwd_id");
      fclose($file);
      var_dump(bot("sendmessage",[
          "chat_id"=>$fwd_id,
          "text"=>"_کاربر شما از ربات بلاک شدید._",
          "parse_mode"=>"markdown"
        ]));
        var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_کاربر $fwd_id بلاک شد._",
          "parse_mode"=>"markdown"
        ])); 
    }elseif(isset($up->message->reply_to_message) && !empty($fwd_id)){
      var_dump(bot("forwardmessage",[
          "chat_id"=>$fwd_id,
          "from_chat_id"=>$chat_id,
          "message_id"=>$msg_id
        ]));
        var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_پیام شما باموفقیت ارسال شد._",
          "parse_mode"=>"markdown"
        ]));
    }elseif($text=="/start"){
      var_dump(bot("sendmessage",[
          "chat_id"=>$chat_id,
          "text"=>"_چکاری میتونم انجام بدم ادمین؟_",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["inline_keyboard"=>[[["text"=>"آمار 👥","callback_data"=>"amar"],["text"=>"پروفایل 👤","callback_data"=>"profile"]],[["text"=>"فروارد همگانی 🗣","callback_data"=>"forward"],["text"=>"بلاک لیست 🚫","callback_data"=>"block"]],[["text"=>"♨️ پیام استارت ربات ♨️","callback_data"=>"start"]],[["text"=>"✏️فروارد بدون عنوان✏️","callback_data"=>"forward2"]],[["text"=>"دستور ➕","callback_data"=>"dasturjadid"],["text"=>"دستور ➖","callback_data"=>"hazfdastur"]]]])
        ]));
    }
  }else{
   if(!strstr(file_get_contents("block.txt"),"$from_id")){
    if(!isset($up->message->forward_from) && !isset($up->message->forward_from_chat)){
    $json=json_decode(file_get_contents("dasturat.json"),true);
      if($text=="/start"){
        $start=str_replace("userid","$from_id",file_get_contents("start.txt"));
        $start=str_replace("username","$username",$start);
        $start=str_replace("firstname","$first_name",$start);
        $start=str_replace("lastname","$last_name",$start);
        $list=array();
        $list[0]=array(array("text"=>"پروفایل"));
        $arrayjs=json_decode(file_get_contents("dasturat.json"),true);
        unset($arrayjs["empty"]);
        $n=0;
        foreach($arrayjs as $key=>$value){
          $n++;
          $list[$n]=array(array("text"=>"$key"));
        }
        var_dump(bot("sendMessage",[
          "chat_id"=>$chat_id,
          "text"=>"$start",
          "reply_markup"=>json_encode(["resize_keyboard"=>true,"keyboard"=>$list])
        ]));
        if(!strstr(file_get_contents("member.txt"),"$from_id")){
          $file=fopen("member.txt","a");
          fwrite($file,"\n$from_id");
          fclose($file);
        }
      }elseif($text=="پروفایل"){
        $profile=file_get_contents("profile.txt");
        var_dump(bot("sendMessage",[
          "chat_id"=>$chat_id,
          "text"=>"$profile"
        ]));
      }elseif(isset($json[$text]) && $text!="empty"){
        if(isset($json[$text]["text"])){
          var_dump(bot("sendMessage",[
            "chat_id"=>$chat_id,
            "text"=>$json[$text]["text"],
            "parse_mode"=>"html"
          ]));
        }elseif($json[$text]["type"]=="sticker"){
          var_dump(bot("sendSticker",[
            "chat_id"=>$chat_id,
            "sticker"=>$json[$text]["file_id"]
          ]));
        }elseif($json[$text]["type"]=="video"){
          var_dump(bot("sendVideo",[
            "chat_id"=>$chat_id,
            "video"=>$json[$text]["file_id"],
            "caption"=>$json[$text]["caption"]
          ]));
        }elseif($json[$text]["type"]=="video_note"){
          var_dump(bot("sendVideoNote",[
            "chat_id"=>$chat_id,
            "video_note"=>$json[$text]["file_id"]
          ]));
        }elseif($json[$text]["type"]=="photo"){
          var_dump(bot("sendPhoto",[
            "chat_id"=>$chat_id,
            "photo"=>$json[$text]["file_id"],
            "caption"=>$json[$text]["caption"]
          ]));
        }elseif($json[$text]["type"]=="audio"){
          var_dump(bot("sendAudio",[
            "chat_id"=>$chat_id,
            "audio"=>$json[$text]["file_id"],
            "caption"=>$json[$text]["caption"]
          ]));
        }elseif($json[$text]["type"]=="voice"){
          var_dump(bot("sendVoice",[
            "chat_id"=>$chat_id,
            "voice"=>$json[$text]["file_id"],
            "caption"=>$json[$text]["caption"]
          ]));
        }elseif($json[$text]["type"]=="document"){
          var_dump(bot("sendDocument",[
            "chat_id"=>$chat_id,
            "document"=>$json[$text]["file_id"],
            "caption"=>$json[$text]["caption"]
          ]));
        }
      }else{
        var_dump(bot("forwardMessage",[
          "chat_id"=>$sudo,
          "from_chat_id"=>$chat_id,
          "message_id"=>$msg_id
        ]));
        var_dump(bot("sendMessage",[
          "chat_id"=>$chat_id,
          "text"=>"_پیام شما با موفقیت ارسال شد._",
          "parse_mode"=>"markdown"
        ]));
      }
    }else{
      var_dump(bot("sendMessage",[
          "chat_id"=>$chat_id,
          "text"=>"_لطفا از جایی پیام فروارد نکنید._",
          "parse_mode"=>"markdown"
        ]));
    }}
  }
}elseif(isset($up->callback_query)){
$data=$up->callback_query->data;
$cl_msgid=$up->callback_query->message->message_id;
$cl_fromid=$up->callback_query->from->id;
$cl_chatid=$up->callback_query->message->chat->id;
  if($cl_fromid==$sudo){
    if($vaziyat=="empty"){
      if($data=="amar"){
        $count=count($member);
        var_dump(bot("editMessageText",[
          "chat_id"=>$cl_chatid,
          "text"=>"_آمار ربات با احتساب خودتان $count نفر است._",
          "message_id"=>$cl_msgid,
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["inline_keyboard"=>[[["text"=>"بازگشت 🔙","callback_data"=>"back"]]]])
        ]));
      }elseif($data=="hazfdastur"){
       $json=json_decode(file_get_contents("dasturat.json"),true); 
       if(count($json)!=1){
         unset($json["empty"]);
         foreach($json as $key=>$value){
           $list="$list\n$key";
         } file_put_contents("sudo.txt","hazfdastur");
          var_dump(bot("sendMessage",[
            "chat_id"=>$cl_chatid,
            "text"=>"دستور مورد نظر را برای حذف بفرستید.\nدستورات شما:\n".$list,
            "reply_markup"=>json_encode(["resize_keyboard"=>true,"keyboard"=>[[["text"=>"لغو"]]]])
          ]));
        }else{
          var_dump(bot("sendMessage",[
            "chat_id"=>$cl_chatid,
            "text"=>"_دستوری موجود نیست._",
            "parse_mode"=>"markdown"
          ]));
        }
      }elseif($data=="back"){
        var_dump(bot("editMessageText",[
          "chat_id"=>$cl_chatid,
          "text"=>"_چکاری میتونم انجام بدم ادمین؟_",
          "message_id"=>$cl_msgid,
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["inline_keyboard"=>[[["text"=>"آمار 👥","callback_data"=>"amar"],["text"=>"پروفایل 👤","callback_data"=>"profile"]],[["text"=>"فروارد همگانی 🗣","callback_data"=>"forward"],["text"=>"بلاک لیست 🚫","callback_data"=>"block"]],[["text"=>"♨️ پیام استارت ربات ♨️","callback_data"=>"start"]],[["text"=>"✏️فروارد بدون عنوان✏️","callback_data"=>"forward2"]],[["text"=>"دستور ➕","callback_data"=>"dasturjadid"],["text"=>"دستور ➖","callback_data"=>"hazfdastur"]]]])
        ]));
      }elseif($data=="profile"){
        var_dump(bot("editMessageText",[
          "chat_id"=>$cl_chatid,
          "text"=>file_get_contents("profile.txt"),
          "message_id"=>$cl_msgid,
          "reply_markup"=>json_encode(["inline_keyboard"=>[[["text"=>"بازگشت 🔙","callback_data"=>"back"],["text"=>"تغییر 🖊","callback_data"=>"changeprofile"]]]])
        ]));
      }elseif($data=="dasturjadid"){
        file_put_contents("sudo.txt","dasturjadid");
        var_dump(bot("sendMessage",[
          "chat_id"=>$cl_chatid,
          "text"=>"_لطفا دستور خود را ارسال کنید._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["resize_keyboard"=>true,"keyboard"=>[[["text"=>"لغو"]]]])
        ]));
      }elseif($data=="changeprofile"){
        file_put_contents("sudo.txt","profile");
        var_dump(bot("sendMessage",[
          "chat_id"=>$cl_chatid,
          "text"=>"_لطفا پیام خود را که فقط حاوی متن باشد ارسال کنید._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["resize_keyboard"=>true,"keyboard"=>[[["text"=>"لغو"]]]])
        ]));
      }elseif($data=="forward2"){
        file_put_contents("sudo.txt","forward2");
        var_dump(bot("sendMessage",[
          "chat_id"=>$cl_chatid,
          "text"=>"_لطفا پیام خود را ارسال کنید._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["resize_keyboard"=>true,"keyboard"=>[[["text"=>"لغو"]]]])]));
      }elseif($data=="forward"){
        file_put_contents("sudo.txt","forward");
        var_dump(bot("sendMessage",[
          "chat_id"=>$cl_chatid,
          "text"=>"_لطفا پیام خود را ارسال کنید._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["resize_keyboard"=>true,"keyboard"=>[[["text"=>"لغو"]]]])]));
      }elseif($data=="start"){
        $txt=file_get_contents("start.txt");
        var_dump(bot("editMessageText",[
          "chat_id"=>$cl_chatid,
          "text"=>"$txt",
          "message_id"=>$cl_msgid,
          "reply_markup"=>json_encode(["inline_keyboard"=>[[["text"=>"بازگشت 🔙","callback_data"=>"back"],["text"=>"تغییر 🖊","callback_data"=>"changestart"]]]])
        ]));
      }elseif($data=="changestart"){
        file_put_contents("sudo.txt","start");
        var_dump(bot("sendMessage",[
          "chat_id"=>$cl_chatid,
          "text"=>"_لطفا پیام خود را که فقط حاوی متن باشد ارسال کنید.کلمات زیر جایگزین خواهند شد.\nuserid با آیدی فرد\nfirstname با نام فرد\nlastname با نام خانوادگی فرد\nusername با یوزرنیم فرد._",
          "parse_mode"=>"markdown",
          "reply_markup"=>json_encode(["resize_keyboard"=>true,"keyboard"=>[[["text"=>"لغو"]]]])
        ]));
      }elseif($data=="block"){
        $array=explode("\n",str_replace("block\n","",file_get_contents("block.txt")));
        if($array[0]!="block"){
          $list=array();
          foreach($array as $key=>$value){
            $list[$key]=array(array("text"=>"$value","callback_data"=>"$value"));
          }
          var_dump(bot("sendMessage",[
            "chat_id"=>$cl_chatid,
            "text"=>"_>>>بلاک لیست<<<_",
            "parse_mode"=>"markdown",
            "reply_markup"=>json_encode(array("inline_keyboard"=>$list))
          ]));
        }else{
          var_dump(bot("sendMessage",[
          "chat_id"=>$cl_chatid,
          "text"=>"_بلاک لیست خالی است._",
          "parse_mode"=>"markdown"
          ]));
        }
      }else{
        file_put_contents("block.txt",str_replace("\n$data","",file_get_contents("block.txt")));
        var_dump(bot("sendMessage",[
          "chat_id"=>$data+0,
          "text"=>"_شما ازبلاک خارج شدید._",
          "parse_mode"=>"markdown"
        ]));
        $array=explode("\n",str_replace("block\n","",file_get_contents("block.txt")));
        if($array[0]!="block"){
          $list=array();
          foreach($array as $key=>$value){
            $list[$key]=array(array("text"=>"$value","callback_data"=>"$value"));
          }
          var_dump(bot("editMessageReplyMarkup",[
            "chat_id"=>$cl_chatid,
            "message_id"=>$cl_msgid, "reply_markup"=>json_encode(array("inline_keyboard"=>$list))
          ]));
        }else{
          var_dump(bot("editMessageText",[
            "chat_id"=>$cl_chatid,
            "message_id"=>$cl_msgid,
            "text"=>"_بلاک لیست خالی است._",
            "parse_mode"=>"markdown"
          ]));
        }
      }
    }else{
      var_dump(bot("answerCallbackQuery",[
        "callback_query_id"=>$up->callback_query->id,
        "text"=>"شما در حال انجام عملیات دیگری هستید.ابتدا آن را لغو کنید.",
        "show_alert"=>true
      ]));
    }
  }else{
    var_dump(bot("answerCallbackQuery",[
        "callback_query_id"=>$up->callback_query->id,
        "text"=>"شما ادمین ربات نیستید.",
        "show_alert"=>true
      ]));
  }
}
elseif($text == "/creator"){
if($bottype != "gold"){
SendMessage($chat_id,"ساخته شده با 💎
⚙️ @TxCreateBot_Bot",'html',$keyboard);
}
}
?>

