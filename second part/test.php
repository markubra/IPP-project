<?php

/*
* Author: Marko Kubrachenko (xkubra00)
* Date: 04.22
* Project: test.php for IPP
*/

// Defaults
$tests_folder = './';
$recursive = FALSE;
$parser_script = "./parse.php";
$interpret_script = "./interpret.py";
$parse_only = FALSE;
$int_only = FALSE;
$jexampath = "/pub/courses/ipp/jexamxml/";
$noclean = FALSE;

// function to print help
function show_help()
{
    echo "HELP:" . PHP_EOL;
    echo "\t--help                vypíše na standardní výstup nápovědu skriptu" . PHP_EOL;
    echo "\t--directory=path      testy bude hledat v zadaném adresáři (chybí-li tento parametr, skript prochází aktuální adresář)" . PHP_EOL;
    echo "\t--recursive           testy bude hledat nejen v zadaném adresáři, ale i rekurzivně ve všech jeho podadresářích" . PHP_EOL;
    echo "\t--parse-script=file   soubor se skriptem v PHP 8.1 pro analýzu zdrojového kódu v IPPcode22 (chybí-li tento parametr, implicitní hodnotou je parse.php uložený v aktuálním adresáři)" . PHP_EOL;
    echo "\t--int-script=file     soubor se skriptem v Python 3.8 pro interpret XML reprezentace kódu v IPPcode22 (chybí-li tento parametr, implicitní hodnotou je interpret.py uložený v aktuálním adresáři)" . PHP_EOL;
    echo "\t--parse-only          bude testován pouze skript pro analýzu zdrojového kódu v IPPcode22 (tento parametr se nesmí kombinovat s parametry --int-only a --int-script)" . PHP_EOL;
    echo "\t--int-only            bude testován pouze skript pro interpret XML reprezentace kódu v IPPcode22 (tento parametr se nesmí kombinovat s parametry --parse-only, --parse-script a --jexampath)" . PHP_EOL;
    echo "\t--jexampath=path      cesta k adresáři obsahující soubor jexamxml.jar s JAR balíčkem s nástrojem A7Soft JExamXML a soubor s konfigurací jménem options" . PHP_EOL;
    echo "\t--noclean             během činnosti test.php nebudou mazány pomocné soubory s mezivýsledky" . PHP_EOL;

}

// function to check and parse arguments
function check_args()
{
    global $argv, $tests_folder, $parser_script, $interpret_script,
           $recursive, $parse_only, $int_only, $jexampath, $noclean;

    $found_parse_script = FALSE;
    $found_int_script = FALSE;
    $found_parse_only = FALSE;
    $found_int_only = FALSE;
    $found_jexampath = FALSE;

    foreach ($argv as $arg)
    {
        if (preg_match("/--help/", $arg))
        {
            // if anything else besides --help -> error
            // otherwise -> print help
            if (count($argv) > 2)
            {
                fwrite(STDERR, "Cannot combine --help with other arguments." . PHP_EOL);
                exit(10);
            }
            show_help();
            exit(0);
        }
        else if (preg_match("/--directory=(.+)/", $arg, $data))
        {
            $tests_folder = $data[1];
        }
        else if (preg_match("/--recursive/", $arg, $data))
        {
            $recursive = TRUE;
        }
        else if (preg_match("/--parse-script=(.+)/", $arg, $data))
        {
            $parser_script = $data[1];
            // check if parser script exists
            if (!file_exists($parser_script))
            {
                fwrite(STDERR, "Wrong path to parser script." . PHP_EOL);
                exit(41);
            }
            $found_parse_script = TRUE;
        }
        else if (preg_match("/--int-script=(.+)/", $arg, $data))
        {
            $interpret_script = $data[1];
            // check if interpret script exists
            if (!file_exists($interpret_script))
            {
                fwrite(STDERR, "Wrong path to interpret script." . PHP_EOL);
                exit(41);
            }
            $found_int_script = TRUE;
        }
        else if (preg_match("/--parse-only/", $arg))
        {
            $parse_only = TRUE;
            $found_parse_only = TRUE;
        }
        else if (preg_match("/--int-only/", $arg))
        {
            $int_only = TRUE;
            $found_int_only = TRUE;
        }
        else if (preg_match("/--jexampath=(.+)/", $arg, $data))
        {
            $jexampath = $data[1];
            $found_jexampath = TRUE;
            // check if jexamxml.jar and options can be found in the directory 
            if (!file_exists($jexampath . "/jexamxml.jar") || !file_exists($jexampath . "/options"))
            {
                fwrite(STDERR, "Wrong path to jexamxml." . PHP_EOL);
                exit(41);
            }
        }
        else if (preg_match("/--noclean/", $arg))
        {
            $noclean = TRUE;
        }
        else
        {
            if (!preg_match("/test.php/", $arg))
            {
                // wrong argument
                fwrite(STDERR, "Use --help." . PHP_EOL);
                exit(10);
            }
        }
    }

    if ($found_parse_only && ($found_int_script || $found_int_only))
    {
        fwrite(STDERR, "wrong combination of arguments -> see --help" . PHP_EOL);
        exit(10);
    }
    if ($found_int_only && ($found_parse_script || $found_parse_only || $found_jexampath))
    {
        fwrite(STDERR, "wrong combination of arguments -> see --help" . PHP_EOL);        
        exit(10);
    }
}

// function to return the tests depending on recursive argument
function is_recursive($recursive, $tests_folder)
{
    try
    {
        if($recursive)
        {
            return new RecursiveIteratorIterator(new RecursiveDirectoryIterator($tests_folder), RecursiveIteratorIterator::SELF_FIRST);
        }
        else
        {
            return new DirectoryIterator($tests_folder);
        }
    }
    catch (Exception $e)
    {
        fwrite(STDERR, "File does not exist." . PHP_EOL);
        exit(41);
    }
}

// print the beginning of html
function print_start()
{
    global $tests_folder, $parser_script, $interpret_script, $parse_only, $int_only, $recursive, $noclean;
    if ($parse_only)
    {
        $script = $parser_script;
    }
    else if ($int_only)
    {
        $script = $interpret_script;
    }
    else
    {
        $script = $parser_script . ", " . $interpret_script;
    }

    echo '<!DOCTYPE html>
    <html>
    <head>
        <title>Test IPPcode22</title>
        <style>
            .styled-table {
                border-collapse: collapse;
                margin: 0px auto;
                font-size: 0.9em;
                font-family: sans-serif;
                min-width: 800px;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            }
            .styled-table thead tr {
                background-color: #07393C;
                color: #ffffff;
                text-align: left;
            }
            .styled-table th,
            .styled-table td {
                padding: 12px 15px;
            }
            .styled-table tbody tr {
                border-bottom: 1px solid #dddddd;
            }
            .styled-table tbody tr:nth-of-type(even) {
                background-color: #f3f3f3;
            }
            .styled-table tbody tr:last-of-type {
                border-bottom: 2px solid #07393C;
            }
            h1 {
                margin: 20px auto;
                color: #07393C;
                text-align: center;
                font-family: sans-serif;
            }
            h3 {
                margin: 20px auto;
                color: #07393C;
                text-align: center;
                font-family: sans-serif;
            }
        </style>    
    </head>
    <body>
        <h3>Directory: ' . $tests_folder . '</h3>
        <h3>Testing: ' . ($parse_only ? 'parse only' : ($int_only ? 'interpret only' : 'both')) . '</h3>
        <h3>Script: ' . $script . '</h3>
        <h3>Recursive: ' . ($recursive ? 'yes' : 'no') . '</h3>
        <h3>No clean: ' . ($noclean ? 'yes' : 'no') . '</h3>
        <table class="styled-table">' . "\n";
}

// print the header of the table in html
function print_header()
{
    
    echo "\t\t\t" . '<thead>
                <tr>
                    <th>#</th>
                    <th>Test</th>
                    <th>Result</th>
                </tr>
            </thead>
            <tbody>' . "\n";
}

// print the test in html
function print_test($number, $test, $result)
{
    echo "\t\t\t\t" . '<tr>
                    <td>' . $number . '</td>
                    <td><b>Folder:</b> ' . pathinfo($test, PATHINFO_DIRNAME) . '<br>
                        <b>Test:</b> ' . pathinfo($test, PATHINFO_FILENAME) . '</td>
                    <td>' . $result . '</td>
                </tr>' . "\n";
}

// print the last part of html file
function print_end($tests_succeeded, $test_counter, $percentage)
{
    echo "\t\t\t" . '</tbody>
    </table>
    <h1>In total succeeded: ' . $tests_succeeded . '/' . $test_counter . ' ~ ' . $percentage . '%</h2>
</body>' . "\n";
}

// main function
function main()
{
    global $tests_folder, $parser_script, $interpret_script,
    $recursive, $parse_only, $int_only, $jexampath, $noclean;

    check_args();
    $tests = is_recursive($recursive, $tests_folder);

    print_start();
    print_header();

    // counters for tests
    $test_counter = 0;
    $tests_succeeded = 0;

    foreach ($tests as $test)
    {
        // find the test with .src
        if (pathinfo($test, PATHINFO_EXTENSION) == "src")
        {
            $test_counter++;
            // get the test name without extension
            $test_name = pathinfo($test, PATHINFO_DIRNAME) . "/" . pathinfo($test, PATHINFO_FILENAME);
            // create .in file if misses
            if (!file_exists($test_name . ".in"))
            {
                $file = fopen($test_name . ".in", 'w+');
                fwrite($file, "");
                fclose($file);
            }
            // create .out file if misses
            if (!file_exists($test_name . ".out"))
            {
                $file = fopen($test_name . ".out", 'w+');
                fwrite($file, "");
                fclose($file);
            }
            // create .rc file if misses
            if (!file_exists($test_name . ".rc"))
            { 
                $file = fopen($test_name . ".rc", 'w+');
                fwrite($file, "0");
                fclose($file);
            }

            // get the correct return code from .rc file
            $correct_rc = file($test_name . ".rc")[0];
    
            // if parse only
            if ($parse_only)
            {
                exec("php8.1 $parser_script < \"$test_name\".src > \"$test_name\".tmp_out", $none, $parser_rc);
                exec("java -jar \"$jexampath\"/jexamxml.jar \"$test_name\".out \"$test_name\".tmp_out delta.xml /D \"$jexampath\"options", $none, $jexamxml_rc);
                    
                if ($correct_rc == $parser_rc)
                {
                    if ($jexamxml_rc == 0)
                    {
                        $succeeded = TRUE;
                        $tests_succeeded++;
                    }
                    else
                    {
                        if (!file_get_contents($test_name . ".tmp_out") && !file_get_contents($test_name . ".out"))
                        {
                            $succeeded = TRUE;
                            $tests_succeeded++;
                        }
                        else
                        {
                            $succeeded = FALSE;
                        }
                    }
                }
                else
                {
                    $succeeded = FALSE;
                }
                // print the test and the result
                print_test($test_counter, $test_name, $succeeded ? '<p style="color:green;font-weight:bold">Success</p>' : '<p style="color:red;font-weight:bold">Fail</p>');
            }
            // if interpret only
            else if ($int_only)
            {
                exec("python3.8 $interpret_script --source=\"$test_name\".src < \"$test_name\".in > \"$test_name\".tmp_out", $none, $interpret_rc);
				exec("diff \"$test_name\".out \"$test_name\".tmp_out", $none, $diff_rc);

                if (($correct_rc == $interpret_rc) && ($diff_rc == 0))
                {
                    $succeeded = TRUE;
                    $tests_succeeded++;
                }
                else
                {
                    $succeeded = FALSE;
                }
                // print the test and the result
                print_test($test_counter, $test_name, $succeeded ? '<p style="color:green;font-weight:bold">Success</p>' : '<p style="color:red;font-weight:bold">Fail</p>');
            }
            else
            {
                exec("php8.1 $parser_script < \"$test_name\".src > \"$test_name\".tmp_xml", $none, $parser_rc);
                exec("python3.8 $interpret_script --source=\"$test_name\".tmp_xml < \"$test_name\".in > \"$test_name\".tmp_out", $none, $interpret_rc);
                exec("diff \"$test_name\".out \"$test_name\".tmp_out", $none, $diff_rc);
                if (($parser_rc == 0) && ($interpret_rc == $correct_rc) && ($diff_rc == 0))
                {
                    $succeeded = TRUE;
                    $tests_succeeded++;
                }
                else
                {
                    $succeeded = FALSE;
                }
                // print the test and the result
                print_test($test_counter, $test_name, $succeeded ? '<p style="color:green;font-weight:bold">Success</p>' : '<p style="color:red;font-weight:bold">Fail</p>');
            }
            // clean temporary files if noclean is false
            if (!$noclean)
            {
                // clean tmps
                if (file_exists($test_name . ".tmp_out"))
                {
                    unlink($test_name . ".tmp_out");
                }
                if (file_exists($test_name . ".tmp_xml"))
                {
                    unlink($test_name . ".tmp_xml");
                }
                if (file_exists($test_name . ".out.log"))
                {
                    unlink($test_name . ".out.log");
                }
                if (file_exists("./delta.xml"))
                {
                    unlink("./delta.xml");
                }
            }
        }
    }
    // calculate the percentage of succeeded tests
    if ($test_counter != 0)
    {
        $percentage = round(($tests_succeeded * 100) / $test_counter);
    }
    else
    {
        $percentage = 0;
    }

    print_end($tests_succeeded, $test_counter, $percentage);

}

// start
main();

?>
