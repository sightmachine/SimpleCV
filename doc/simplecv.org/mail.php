<?php
	//declare our assets 
	$name = stripcslashes($_POST['name']);
	$emailAddr = stripcslashes($_POST['email']);
	$comment = stripcslashes($_POST['message']);
	$subject = stripcslashes($_POST['subject']);	
	$contactMessage =  
		"Message:
		$comment 

		Name: $name
		E-mail: $emailAddr

		Sending IP:$_SERVER[REMOTE_ADDR]
		Sending Script: $_SERVER[HTTP_HOST]$_SERVER[PHP_SELF]";
		
		//send the email 
		mail('public.relations@ingenuitas.com', $subject, $contactMessage);
		echo('success'); //return success callback
?>
