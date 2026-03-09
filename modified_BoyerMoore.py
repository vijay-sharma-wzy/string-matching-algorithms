
import sys


def txt_to_list(text_file):
    """
    Appends each character in text_file to a list and returns that list

    TIME COMPLEXITY: O(number_of_characters_in_text_file)
    SPACE COMPLEXITY: O(number_of_characters_in_text_file)
    """
    text = []
    with open(text_file, 'r') as t:
        for char in t.read():
            # Exclude newlines from the final list
            if char != '\n':
                text.append(char)
    return text


def reverse_list(ls):
    """
    Returns copy of ls but reversed

    TIME COMPLEXITY: O(len(ls))
    SPACE COMPLEXITY: O(len(ls))
    """
    reversed_list = []
    # Iterate through ls backwards
    for i in range(len(ls) - 1, -1, -1):
        reversed_list.append(ls[i])
    return reversed_list


def output_matches_to_file(pattern_matches, filename):
    """ Outputs pattern matches to file """
    pat_matches_len = len(pattern_matches)
    pat_matches_last_idx = pat_matches_len - 1
    with open(filename, 'w') as f:
        for i in range(pat_matches_len):
            # Output positions as if they are 1-indexed
            f.write(str(pattern_matches[i] + 1))
            if i < pat_matches_last_idx:
                f.write('\n')



def get_z_list(pattern):
    """
    Returns z_list of pattern
        (a list where for each i in 0...pattern_last_index: z_list[i] is the length of the longest substring beginning at index i, that is a prefix of pattern)

    TIME COMPLEXITY: O(len(pattern))
    SPACE COMPLEXITY: O(len(pattern))
    """
    # Initialise variables
    pat_length = len(pattern)
    z_list = [0 for i in range(len(pattern))]
    right = -1
    left = -1

    # Create Z values for Z[1] ... Z[pat_length - 1]
    for k in range(1, pat_length):
        # If 'right' is BEFORE the position (k) that we are computing the current Z variable (Z[k]):
        #   explicitly compare pattern[k...mismatch_position - 1] with pattern[0...mismatch_position - k] to find Z[k]
        if k > right:
            i = k
            j = 0
            while i < pat_length and pattern[i] == pattern[j]:
                i += 1
                j += 1

            z_list[k] = i - k
            # Update right and left variables if Z[k] > 0. Otherwise leave them as is
            if z_list[k] > 0:
                right = i - 1
                left = k
        # If 'right' is AFTER the position (k) that we are computing the current Z variable (Z[k]):
        #   use previously computed data to efficiently calculate Z[k]
        else:
            # This 'if statement block' executes if we already calculated a Z value that is identical to Z[k]
            if z_list[k - left] < right - k + 1:
                z_list[k] = z_list[k - left]
            # This 'else statement block' executes if we already calculated a Z value that shares a prefix with Z[k]
            #   meaning that we need to explicitly compare values after that identical prefix to get the full Z[k] value
            else:
                i = right + 1
                j = right - k + 1
                while i < pat_length and pattern[i] == pattern[j]:
                    i += 1
                    j += 1
                z_list[k] = i - k
                right = i - 1
                left = k

    return z_list


def get_zs_list(pattern):
    """
    Returns z_suffix_list of pattern
        (a list where for each i in 0...pattern_last_index: z_suffix_list[i] is the length of the longest substring ending at index i, that is a suffix of pattern)

    TIME COMPLEXITY: O(len(pattern))
    SPACE COMPLEXITY: O(len(pattern))
    """
    # Compute Z prefix list of reverse(pattern), then reverse that Z prefix list which turns it into a Z suffix list
    pattern_rev = reverse_list(pattern)
    z_suffix_list = get_z_list(pattern_rev)
    z_suffix_list = reverse_list(z_suffix_list)
    return z_suffix_list


def get_ascii_gs_list(pattern, z_suffix_list):
    """
    Returns ascii_good_suffix_list.
    - good_suffix_list SEMI-DEFINITION:  a list where for each i in 0...len(pattern), good_suffix_list[i] is the index
                                        of the rightmost substring that equals the suffix good_suffix_list[i...last_index]
    - ascii_good_suffix_list DEFINITION: 2D list where each row represents a printable ASCII character and stores a
                                            'good_suffix_list' with the condition that the substrings must be preceded
                                            by the respective ASCII character

    TIME COMPLEXITY: O(len(pattern))
    SPACE COMPLEXITY: O(len(pattern))
    """
    # ascii_list = list of all printable ASCII characters
    ascii_list = [chr(i) for i in range(32, 127 + 1)]
    pat_length = len(pattern)
    # good_suffix_list = 2D list where each row represents an ASCII character,
    # and store a 'good suffix list' with the condition that the substrings must be preceded by the respective ASCII character
    ascii_good_suffix_list = [[] for _ in range(128)]

    # Initialise the inner good suffix lists with None values
    for ascii_row in ascii_good_suffix_list:
        for i in range(0, pat_length + 1):
            ascii_row.append(None)

    # Populate inner good suffix lists, that are in ascii_good_suffix_list
    for char in ascii_list:
        for p in range(0, pat_length - 1):
            j = pat_length - z_suffix_list[p]
            # If p represents a good suffix that is preceded by character 'char':
            #   add it to ascii_good_suffix_list at the respective ASCII char row
            if p - z_suffix_list[p] >= 0 and pattern[p - z_suffix_list[p]] == char:
                ascii_good_suffix_list[ord(char)][j] = p

    return ascii_good_suffix_list


def get_mp_list(pattern, z_suffix_list):
    """
    Returns matched_prefix_list
        (matched_prefix_list[i] denotes the length of the largest suffix of pattern[i...last_index]
         that is identical to the prefix of pattern[0, last_index - k])

    TIME COMPLEXITY: O(len(pattern))
    SPACE COMPLEXITY: O(len(pattern))
    """
    pat_length = len(pattern)
    matched_prefix_list = [0 for _ in range(pat_length + 1)]

    last_stored_position = 0
    for p in range(0, pat_length - 1):
        if z_suffix_list[p] == p + 1:
            last_stored_position = z_suffix_list[p]
            matched_prefix_list[pat_length - 1 - p] = last_stored_position
        else:
            matched_prefix_list[pat_length - 1 - p] = last_stored_position

    return matched_prefix_list


def get_pattern_matches(pattern, text):
    """
    Returns positions in text where pattern occurs.
    This is done using the modified Boyer-Moore algorithm:
        (scan right-to-left until (potential) mismatch at position k, so text[k] is considered a 'bad character'.
         the pattern is shifted to the right to align a good suffix (that is preceded by the 'bad character').
         This is repeated until all matches are found.

    TIME COMPLEXITY: O(len(pattern) + len(text))
    SPACE COMPLEXITY: O(len(pattern) + len(text))
    """
    # Account for edge cases
    if pattern == [] or pattern == '':
        return []
    pat_length = len(pattern)
    pat_last_index = pat_length - 1
    text_last_index = len(text) - 1
    # match_positions = positions in text where pattern occurs
    match_positions = []

    z_suffix_list = get_zs_list(pattern)
    good_suffix_list = get_ascii_gs_list(pattern, z_suffix_list)
    matched_prefix_list = get_mp_list(pattern, z_suffix_list)

    text_shift = 0
    # Variables for Galil optimisation
    stop = None
    start = None
    while pat_last_index + text_shift <= text_last_index:
        # Scan right-to-left while skipping characters we already know match (Galil's optimisation)
        p = pat_last_index
        while p > 0 and pattern[p] == text[p + text_shift]:
            if p - 1 == stop:
                p = start - 1 if start > 0 else 0
            else:
                p -= 1

        # If we found a mismatch:
        #   shift pattern to the right to align a good suffix that is preceded by the 'bad character'
        if pattern[p] != text[p + text_shift]:
            bad_char = text[p + text_shift]
            gs_shift = good_suffix_list[ord(bad_char)][p + 1]
            if gs_shift is not None:
                text_shift = text_shift + pat_length - gs_shift - 1
                # stop and start represents range of characters we already know match, so we don't need to recompare later
                stop = gs_shift
                start = gs_shift - pat_length + p + 2
            else:
                text_shift = text_shift + pat_length - matched_prefix_list[p + 1]
                # stop and start represents range of characters we already know match, so we don't need to recompare later
                stop = matched_prefix_list[p + 1] - 1
                start = 0

        # Else if we found an occurrence of pattern in text:
        #   shift pattern to the right by pat_length - matched_prefix_list[1]
        else:
            match_positions.append(p + text_shift)
            text_shift = text_shift + pat_length - matched_prefix_list[1]
            # stop and start represents range of characters we already know match, so we don't need to re-compare later
            stop = matched_prefix_list[p + 1] - 1
            start = 0

    return match_positions


def my_test_cases():
    """ For development/testing """
    NUM_TESTS = 10
    TEST_CASES_DIRECTORY = 'q1_test_cases'
    for test_num in range(1, NUM_TESTS + 1):
        directory = TEST_CASES_DIRECTORY + '/test' + str(test_num)

        pattern_file = directory + '/pat.txt'
        text_file = directory + '/text.txt'
        pattern = txt_to_list(pattern_file)
        text = txt_to_list(text_file)

        answer_file = directory + '/answer.txt'
        with open(answer_file, 'r') as a:
            answer = a.read()
            answer = answer.split(',')
            if answer == ['']:
                answer = []
            else:
                answer = [int(num) for num in answer]

        pattern_matches = get_pattern_matches(pattern, text)
        print("========== TEST " + str(test_num) + " ==========")
        print("ATTEMPT:\t\t" + str(pattern_matches))
        print("REAL ANSWER:\t" + str(answer))
        print("CORRECTNESS?:\t" + str(pattern_matches == answer))


if __name__ == '__main__':
    #my_test_cases()

    if len(sys.argv) >= 3:
        # Retrieve text from console as lists
        text_list = txt_to_list(sys.argv[1])
        pattern_list = txt_to_list(sys.argv[2])

        # Get pattern matches and output to file
        pattern_matches = get_pattern_matches(pattern_list, text_list)
        output_matches_to_file(pattern_matches, filename='output_modified_BoyerMoore.txt')
    else:
        print('Invalid console arguments')

