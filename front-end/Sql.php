<?php

// get the HTTP method, path and body of the request
$method = $_SERVER['REQUEST_METHOD'];

// connect to the mysql database
$configs = include('SqlConfig.php');
$link = mysqli_connect($configs['host'], $configs['username'], $configs['password'], $configs['database']);
mysqli_set_charset($link, 'utf8');

// Only works for game for now.
$table = 'game';

// create SQL based on HTTP method
switch ($method) {
  case 'GET':
    $sql = "select * from `$table`;"; break;
  // These others aren't supported yet.
  case 'PUT':
    die("Request method is not supported."); break;
  case 'POST':
    die("Request method is not supported."); break;
  case 'DELETE':
    die("Request method is not supported."); break;
}

// excecute SQL statement
$result = mysqli_query($link, $sql);

// die if SQL statement failed
if (!$result) {
  http_response_code(404);
  die(mysqli_error());
}

// Print results
if ($method == 'GET') {
  if (!$key) echo '[';
  for ($i=0;$i<mysqli_num_rows($result);$i++) {
    echo ($i>0?',':'').json_encode(mysqli_fetch_object($result));
  }
  if (!$key) echo ']';
}

// close mysql connection
mysqli_close($link);
