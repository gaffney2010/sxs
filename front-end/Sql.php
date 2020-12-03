<?php

// get the HTTP method, path and body of the request
$method = $_SERVER['REQUEST_METHOD'];

// connect to the mysql database
$configs = include('SqlConfig.php');
$mysqli = new mysqli($configs['host'], $configs['username'], $configs['password'], $configs['database']);

function safeGet($mysqli, $param) {
  if (isset($_GET[$param])) {
    return $mysqli->real_escape_string($_GET[$param]);
  }
  return "";
}

// Only works for game for now.
$columns = safeGet($mysqli, 'columns');
$table = safeGet($mysqli, 'table');
$where_clause = safeGet($mysqli, 'where');
$order_clause = safeGet($mysqli, 'order');
$limit = safeGet($mysqli, 'limit');

if (empty($columns) || empty($table)) {
  die("columns and table must be passed.");
}
if (empty($where_clause)) {
  $where_clause = "true";
}
if (empty($order_clause)) {
  $order_clause = "1";
}
if (empty($limit)) {
  $limit = "9999";
}

// create SQL based on HTTP method
switch ($method) {
  case 'GET':
    $result = $mysqli->query("select distinct $columns from $table where $where_clause order by $order_clause limit $limit;") or die($mysqli->error);
    break;
  // These others aren't supported yet.
  case 'PUT':
    die("Request method is not supported."); break;
  case 'POST':
    die("Request method is not supported."); break;
  case 'DELETE':
    die("Request method is not supported."); break;
}

// Print results
if ($method == 'GET') {
  $myArray = array();
  while($row = $result->fetch_array(MYSQLI_ASSOC)) {
          $myArray[] = $row;
  }
  echo json_encode($myArray);
}
