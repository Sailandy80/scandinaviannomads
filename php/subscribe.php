<?php
// Newsletter signup for scandinaviannomads.com
// Stores subscribers outside the public web folder and emails a notification.
$notify = 'connect@scandinaviannomads.com';
$store  = dirname(__DIR__) . '/sn-data';   // one level above public_html, not reachable from the web

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: /'); exit; }
if (!empty($_POST['website'])) { header('Location: /subscribed/'); exit; } // honeypot

$email = strtolower(trim(substr($_POST['email'] ?? '', 0, 200)));
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) { header('Location: /oops/'); exit; }

$saved = false;
if (!is_dir($store)) { @mkdir($store, 0700, true); }
if (is_dir($store)) {
    $file = $store . '/subscribers.csv';
    $existing = is_file($file) ? file_get_contents($file) : '';
    if (strpos($existing, ',' . $email . "\n") === false) {
        $saved = @file_put_contents($file, gmdate('c') . ',' . $email . "\n", FILE_APPEND | LOCK_EX) !== false;
    } else {
        $saved = true;
    }
}

@mail($notify, 'New newsletter subscriber', "New subscriber: $email\n",
      "From: Scandinavian Nomads <noreply@scandinaviannomads.com>\r\nContent-Type: text/plain; charset=UTF-8\r\n");

header('Location: ' . ($saved ? '/subscribed/' : '/oops/'));
