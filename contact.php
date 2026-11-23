<?php
// Contact form handler for scandinaviannomads.com
$to = 'connect@scandinaviannomads.com';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: /contact/'); exit; }
if (!empty($_POST['website'])) { header('Location: /thanks/'); exit; } // honeypot

$name    = trim(substr($_POST['name'] ?? '', 0, 100));
$email   = trim(substr($_POST['email'] ?? '', 0, 200));
$topic   = trim(substr($_POST['topic'] ?? 'General question', 0, 60));
$message = trim(substr($_POST['message'] ?? '', 0, 5000));

if ($name === '' || $message === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    header('Location: /oops/'); exit;
}
$clean = fn($s) => str_replace(["\r", "\n"], ' ', $s);

$subject = 'Scandinavian Nomads: ' . $clean($topic) . ' from ' . $clean($name);
$body = "Name: $name\nEmail: $email\nTopic: $topic\n\n$message\n";
$headers = "From: Scandinavian Nomads <noreply@scandinaviannomads.com>\r\n"
         . "Reply-To: " . $clean($email) . "\r\n"
         . "Content-Type: text/plain; charset=UTF-8\r\n";

$ok = @mail($to, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, $headers);
header('Location: ' . ($ok ? '/thanks/' : '/oops/'));
