# This script parses .ASS and .SRT subtitle files
# It determines the length in seconds for all non-empty lines
# As well as character count with and without spaces
# Made by Jamato-sUn to more precicely evaluate translation costs
# for videos with a lot of pauses between speech

import re  # regex
import io  # encoding
import sys  # argument
import os  # file existence


# accepts milliseconds
def print_time(mt):  # stupid, but better than datetime
    seconds = round(mt / 1000)  # seconds rounded
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    print("TOTAL LINES LENGTH:  %02d:%02d:%02d" % (hours, minutes, seconds))


def process_ass(full_text):
    total_length = 0  # milliseconds
    character_count = 0  # with spaces
    character_no_space = 0
    actual_timecodes = full_text

    lines = actual_timecodes.split('\n')
    lines = lines[:-1]  # for some reason split generates an extra empty line

    del lines[0]  # [Events]
    del lines[0]  # Format

    # expression_text = r"^([^,]*,)(?P<t1>[^,]*),(?P<t2>[^,]*),([^,]*,){6}(?P<Text>.+)$"
    # .ass lines have 9 commas before text, six of them follow the timecodes
    # Decent editors refuse to add commas to styles' names

    text_lines_amount = 0
    # i = 0 # for debugging
    for line in lines:
        # i+=1;
        # print(str(i)+" "+str(line)); # for debugging
        m = line.split(',', 10)
        # if this not a valid or empty line
        if len(m) < 10 or m[9] == "":
            continue

        result1 = [m[9], m[1], m[2]]
        # print(result1)
        text_lines_amount += 1
        # print(">>>"+result1[0]+"<<<") # for debugging
        character_count += len(result1[0])
        character_no_space += len(result1[0].replace(" ", ""))
        # sending centiseconds here, hence the extra "0"
        total_length += timecode_difference(result1[1] + "0", result1[2] + "0")

    return total_length, character_count, character_no_space, text_lines_amount


def process_srt(full_text):
    print("This is not an ASS file! It could be anything! Ugh. Well, here we go...")
    total_length = 0  # milliseconds
    character_count = 0  # with spaces
    character_no_space = 0
    chunks = full_text.split('\n\n')  # there may be multiple lines of text within chunk
    amount_of_chunks = len(chunks) - 1
    text_lines_amount = amount_of_chunks
    for chunk in chunks:
        if len(chunk) >= 2:  # number of srt line and at least symbol
            text_lines = chunk.split('\n')
            timecodes = text_lines[1]
            i = 2
            subtitle_text = ""
            while i < len(text_lines):
                subtitle_text += text_lines[i]
                i += 1
            # print(subtitle_text+ "\n")
            result = timecodes.split(" --> ")
            if len(result) == 2:
                total_length += timecode_difference(result[0], result[1])

            character_count += len(subtitle_text)
            character_no_space += len(subtitle_text.replace(" ", ""))

    return total_length, character_count, character_no_space, text_lines_amount


# Parses two strings which should have timecodes in them
# Returns difference in milliseconds
def timecode_difference(t_start, t_end):
    expression_timecode = r"(?P<hours>\d+):(?P<minutes>\d\d):(?P<seconds>\d\d)[:.,](?P<centiseconds>\d+)"
    result = [re.findall(expression_timecode, t_start)[0], re.findall(expression_timecode, t_end)[0]]
    # print(result) # for debugging
    time1 = list(map(int, result[0]))  # line beginning
    time2 = list(map(int, result[1]))  # line end
    # get milliseconds
    time_ms_1 = time1[0] * 3600000 + time1[1] * 60000 + time1[2] * 1000 + time1[3]
    time_ms_2 = time2[0] * 3600000 + time2[1] * 60000 + time2[2] * 1000 + time2[3]
    difference = time_ms_2 - time_ms_1
    return difference


def length_counter(full_filename):
    if not os.path.exists(full_filename):
        print("File not found")
        return

    print(full_filename)
    file = io.open(full_filename, encoding='utf-8')  # solution for error with byte 0х98
    full_text = file.read()
    file.close()
    # print(full_text)
    # No more filework from now on
    beginning = full_text.find("[Events]")  # this is actually kind of stupid, maybe I should add some checks

    # SRT cannot contain empty lines, it breaks.
    if beginning == -1:  # SRT processing attempt
        total_length, character_count, character_nospace, text_lines_amount = process_srt(full_text)
    else:  # ASS PROCESSING
        total_length, character_count, character_nospace, text_lines_amount = process_ass(full_text[beginning:])

    print_time(total_length)
    print("Characters: " + str(character_count) + "   Without spaces: " + str(character_nospace))
    print("LINES: " + str(text_lines_amount))


def main():
    print("START")
    length_counter(sys.argv[1])


main()
