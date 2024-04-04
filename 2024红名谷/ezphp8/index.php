<?php
if (isset($_GET['ezphpPhp8'])) {
    highlight_file(__FILE__);
} else {
    die("No");
}

$a = new class {
    function __construct() {

    }

    function getflag() {
        system('cat /flag');
    }
};

$a = $_GET['ezphpPhp8'];
$f = new $a();
$f->getflag();
?>