<?php

/*
* Author: Marko Kubrachenko (xkubra00)
* Date: 01.22
* Project: Parser for IPP
*/

ini_set('display_errors', 'stderr');

// different arrays of instructions depending on how many arguments the instruction has (total 35)
$instructions0 = array("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK");
$instructions1 = array("DEFVAR", "CALL", "PUSHS", "POPS", "WRITE", "LABEL", "JUMP", "EXIT", "DPRINT");
$instructions2 = array("MOVE", "INT2CHAR", "READ", "STRLEN", "TYPE", "NOT");
$instructions3 = array("ADD", "SUB", "MUL", "IDIV", "GT", "LT", "EQ", "AND", "OR",
                       "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR", "JUMPIFEQ", "JUMPIFNEQ");

$empty_line = FALSE;
$var = "/^(LF|GF|TF)@[a-zA-Z_\-$&%*!?]+[a-zA-Z0-9_\-$&%*!?]*$/";
$symb = "/^(((LF|GF|TF)@[a-zA-Z_\-$&%*!?]+[a-zA-Z0-9_\-$&%*!?]*)|(nil@nil)|(bool@(true|false))|(int@[+-]?[0-9]+)|(string@([^\\\\\\s]|(\\\\\d{3,}))*))$/";
$label = "/^[a-zA-Z_\-$&%*!?]+[a-zA-Z0-9_\-$&%*!?]*$/";
$type = "/^(int|string|bool)$/";

// counters for stats 
$order = 0; // --loc
$cnt_comments = 0; // --comments
$cnt_labels = 0; // --labels
$unique_labels = array();
$cnt_jumps = 0;

// sends a certain error to stderr with the message
function send_error($error, $message)
{
    // if buffer is not empty
    if (ob_get_contents())
    {
        // clean buffer and finish
        ob_end_clean();
    }

    fwrite(STDERR, $message . PHP_EOL);
    exit($error);
}

// checks header of the input file
function check_header($line)
{
    if (strtoupper(trim($line)) != ".IPPCODE22")
    {
        send_error(21, "Chybná nebo chybějící hlavička (.IPPcode22)." . PHP_EOL);
    }
}

// deletes comments from input file
function delete_comments($line)
{
    global $empty_line;
    global $cnt_comments;

    // if comment was detected
    if (strpos($line, "#") !== FALSE)
    {
        // increase counter for stats
        $cnt_comments++;

        if (substr(trim($line), 0, 1) == "#")
        {
            $empty_line = TRUE;
        }

        // cut off comments
        $line = substr($line, 0, strpos($line, "#"));
    }

    //cut off white chars
    $line = trim($line);
    return $line;
}

// splits the instruction to an array
function split_the_line($line)
{
    // split the line to an array of parts
    return (preg_split("/\s+/", $line));
}

// counts parts of the instruction
function count_parts($instruction, $num)
{
    if (count($instruction) !== $num)
    {
        send_error(23, "Pocet argumentu u zadane instrukce je spatny.");
    }
}

function print_symb($argument, $num)
{
    $tmp = explode("@", $argument, 2);
    if ($tmp[0] == "string")
    {
        echo "\t\t<arg".$num." type=\"string\">".$tmp[1]."</arg".$num.">" . PHP_EOL;
    }
    else if ($tmp[0] == "bool")
    {
        echo "\t\t<arg".$num." type=\"bool\">".$tmp[1]."</arg".$num.">" . PHP_EOL;
    }
    else if ($tmp[0] == "int")
    {
        echo "\t\t<arg".$num." type=\"int\">".$tmp[1]."</arg".$num.">" . PHP_EOL;
    }
    else if ($tmp[0] == "nil")
    {
        echo "\t\t<arg".$num." type=\"nil\">".$tmp[1]."</arg".$num.">" . PHP_EOL;
    }
    else
    {
        echo "\t\t<arg".$num." type=\"var\">".$argument."</arg".$num.">" . PHP_EOL;
    }
}

// checks the opcode and operands of the instruction
function check_instruction_and_print($instruction)
{
    global $var, $symb, $label, $type;
    global $order;
    global $cnt_labels, $unique_labels;
    global $cnt_jumps;
    global $instructions0;
    global $instructions1;
    global $instructions2;
    global $instructions3;
    
    // opcode to upper case
    $instruction[0] = strtoupper($instruction[0]);

    // check opcode and number of operands
    if (in_array($instruction[0], $instructions0))
    {
        count_parts($instruction, 1);
    }
    else if (in_array($instruction[0], $instructions1))
    {
        count_parts($instruction, 2);
    }
    else if (in_array($instruction[0], $instructions2))
    {
        count_parts($instruction, 3);
    }
    else if (in_array($instruction[0], $instructions3))
    {
        count_parts($instruction, 4);
    }
    else
    {
        send_error(22, "Neznámý nebo chybný operační kód." . PHP_EOL);
    }

    // print the opcode part of xml
    echo "\t<instruction order=\"".$order."\" opcode=\"".$instruction[0]."\">" . PHP_EOL;

    // check first operand
    switch($instruction[0])
    {
        // first operand is "var"
        case 'MOVE':
        case 'DEFVAR':
        case 'POPS':
        case 'ADD':
        case 'SUB':
        case 'MUL':
        case 'IDIV':
        case 'LT':
        case 'GT':
        case 'EQ':
        case 'AND':
        case 'OR':
        case 'NOT':
        case 'INT2CHAR':
        case 'STRI2INT':
        case 'READ':
        case 'CONCAT':
        case 'STRLEN':
        case 'GETCHAR':
        case 'SETCHAR':
        case 'TYPE':
            if (preg_match($var, $instruction[1]))
            {
                $instruction[1] = htmlspecialchars($instruction[1], ENT_QUOTES | ENT_XML1);

                echo "\t\t<arg1 type=\"var\">".$instruction[1]."</arg1>" . PHP_EOL;
            }
            else
            {
                send_error(23, "Spatne argumenty u instrukce.");
            }
            break;
            
        // first operand is "symb"
        case 'PUSHS':
        case 'WRITE':
        case 'EXIT':
        case 'DPRINT':
            if (preg_match($symb, $instruction[1]))
            {
                $instruction[1] = htmlspecialchars($instruction[1], ENT_QUOTES | ENT_XML1);

                print_symb($instruction[1], 1);
            }
            else
            {
                send_error(23, "Spatne argumenty u instrukce.");
            }
            break;

        // first operand is "label"
        case 'CALL':
        case 'LABEL':
        case 'JUMP':
        case 'JUMPIFEQ':
        case 'JUMPIFNEQ':
            if (preg_match($label, $instruction[1]))
            {
                $instruction[1] = htmlspecialchars($instruction[1], ENT_QUOTES | ENT_XML1);

                echo "\t\t<arg1 type=\"label\">".$instruction[1]."</arg1>" . PHP_EOL;
            }
            else            
            {
                send_error(23, "Spatne argumenty u instrukce.");
            }

            // increase counter for stat --jumps
            $cnt_jumps++;
            break;

        // instructions without operands
        default:
            break;
    }

    // check second operand
    switch($instruction[0])
    {
        // second operand is symb
        case 'MOVE':
        case 'ADD':
        case 'SUB':
        case 'MUL':
        case 'IDIV':
        case 'LT':
        case 'GT':
        case 'EQ':
        case 'AND':
        case 'OR':
        case 'NOT':
        case 'INT2CHAR':
        case 'STRI2INT':
        case 'CONCAT':
        case 'GETCHAR':
        case 'SETCHAR':
        case 'STRLEN':
        case 'TYPE':
        case 'JUMPIFEQ':
        case 'JUMPIFNEQ':
            if (preg_match($symb, $instruction[2]))
            {
                $instruction[2] = htmlspecialchars($instruction[2], ENT_QUOTES | ENT_XML1);

                print_symb($instruction[2], 2);
            }
            else
            {
                send_error(23, "Spatne argumenty u instrukce.");
            }
            break;

        // second operand is type
        case 'READ':
            if (preg_match($type, $instruction[2]))
            {
                echo "\t\t<arg2 type=\"type\">".$instruction[2]."</arg2>" . PHP_EOL;
            }
            else
            {
                send_error(23, "Spatne argumenty u instrukce.");
            }
            break;
            
        // instructions with less then 2 operands
        default:
            break;
    }

    //
    switch ($instruction[0])
    {
        // third operand is symb
        case 'ADD':
        case 'SUB':
        case 'MUL':
        case 'IDIV':
        case 'LT':
        case 'GT':
        case 'EQ':
        case 'AND':
        case 'OR':
        case 'STRI2INT':
        case 'CONCAT':
        case 'GETCHAR':
        case 'SETCHAR':
        case 'JUMPIFEQ':
        case 'JUMPIFNEQ':
            if (preg_match($symb, $instruction[3]))
            {
                $instruction[3] = htmlspecialchars($instruction[3], ENT_QUOTES | ENT_XML1);

                print_symb($instruction[3], 3);
            }
            else
            {
                send_error(23, "Spatne argumenty u instrukce.");
            }
            break;
        
        // case for stats param --labels
        // located here so it causes no problems
        case 'LABEL':
            // check if current label was not defined before
            if (!in_array($instruction[1], $unique_labels))
            {
                // add unique label to array
                $unique_labels[$cnt_labels] = $instruction[1];
                $cnt_labels++;
            }
            break;

        // instructions with less then 3 operands
        default:
            break;
    }

    // print end of instruction
    echo "\t</instruction>" . PHP_EOL;
}

function main()
{
    // variables declaration
    global $line;
    global $instruction;
    global $empty_line;
    global $order;

    // check for empty input
    if(($line = fgets(STDIN)) == FALSE)
    {
        send_error(21, "Empty input file.");
    }

    // find first not empty line
    while(empty($line) || ($line == PHP_EOL) || strpos(trim($line), "#") === 0)
    {
        $line = fgets(STDIN);
    }

    // delete possible comment
    $line = delete_comments($line);

    // check the header
    check_header($line);

    // prints the beginning of xml
    echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" . PHP_EOL;
    echo "<program language=\"IPPcode22\">" . PHP_EOL;

    // read line by line until end of file
    while (($line = fgets(STDIN)) != FALSE)
    {
        while(empty($line) || ($line == PHP_EOL))
        {
            $line = fgets(STDIN);
        }

        // delete possible comments 
        $line = delete_comments($line);

        if (!$empty_line)
        {
            // split the instruction
            $instruction = split_the_line($line);
            // increase a counter for xml representation
            $order++;
            // check the instruction
            check_instruction_and_print($instruction);
            // split the line to an array with parts of the instruction
        }
        else
        {
            // skip the line
            $empty_line = FALSE;
        }
    }
    // print last part of xml
    echo "</program>" . PHP_EOL;
}


// start of the program
if ((array_search("parse.php", $argv) == 0) && !(in_array("--help", $argv)))
{
    ob_start();
    main();

    if ($argc > 1)
    {
        if (str_starts_with($argv[1], "--stats="))
        {
            // get the name of the file for stat
            $file = fopen(explode("=", $argv[1], 2)[1], "w") or die("Unable to open file!");
            // print the stats
            foreach (array_slice($argv, 2) as $stat)
            {
                if ($stat == "--loc")
                {
                    fwrite($file, $order . PHP_EOL);
                }
                else if ($stat == "--comments")
                {
                    fwrite($file, $cnt_comments . PHP_EOL);
                }
                else if ($stat == "--labels")
                {
                    fwrite($file, $cnt_labels . PHP_EOL);
                }
                else if ($stat == "--jumps")
                {
                    fwrite($file, $cnt_jumps . PHP_EOL);
                }
                else
                {
                    // unknown stat param
                    fclose($file);
                    send_error(10, "Bad params.");
                }
            }
            fclose($file);
        }
        else
        {
            // unknown param (not help not stats)
            send_error(10, "Bad params.");
        }
    }

    // print the buffer (xml)
    ob_end_flush();
    exit(0);
}
else if (($argc == 2) && (in_array("--help", $argv)))
{
    // print manual
    echo "Usage: parser.php [options] < inputFile" . PHP_EOL;
    echo "[options]:" . PHP_EOL;
    echo "\t--help - manual" . PHP_EOL;
    echo "\t--stats=file - specify name of file for stats output" . PHP_EOL;
    echo "with --stats=file only:" . PHP_EOL;
    echo "\t--loc - number of instructions in IPPcode22 programm" . PHP_EOL;
    echo "\t--comments - number of comments in IPPcode22 programm" . PHP_EOL;
    echo "\t--jumps - number of jump-instructions in IPPcode22 program" . PHP_EOL;
    exit(0);
}
else
{
    // shouldn't be riched
    send_error(10, "Bad params.");
}

?>