
import sys

# For development
global DEBUG
DEBUG = False


class GlobalEnd:
    """ Class to create a GlobalEnd pointer for leaf nodes when constructing suffix tree """

    def __init__(self):
        self.data = None

    def set_data(self, new_data):
        self.data = new_data

    def get_data(self):
        return self.data


# Create a GlobalEnd pointer for leaf nodes when constructing suffix tree
GLOBAL_END = GlobalEnd()


class STNode:
    """ Class to create nodes for ModifiedSuffixTree object """

    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end
        # self.children has positions for all ASCII characters
        self.children = [None for i in range(0, 127 + 1)]
        self.is_leaf = True
        self.suffix_link = None
        self.parent = None
        # self.substring_start is the 'leaf label' (for indicating the start of a substring from root node to leaf)
        self.substring_start = None
        # self.text_reference stores which text file/object the STNode belongs to
        self.text_reference = None

    def get_start(self):
        return self.start

    def get_end(self):
        # If self is a leaf, return GLOBAL_END data. Otherwise return self.end that has been previously initialised
        if self.is_leaf:
            return GLOBAL_END.get_data()
        else:
            return self.end

    def get_children(self):
        return self.children

    def get_suffix_link(self):
        return self.suffix_link

    def get_substring_start(self):
        # Only return self.substring_start (leaf label) if self is a leaf
        if self.is_leaf:
            return self.substring_start
        else:
            return None

    def get_text_reference(self):
        # Only return self.text_reference (leaf label) if self is a leaf
        if self.is_leaf:
            return self.text_reference
        else:
            return None

    def set_text_reference(self, text_num):
        self.text_reference = text_num

    def set_start(self, new_start):
        self.start = new_start

    def set_end(self, new_end):
        self.end = new_end

    def set_substring_start(self, position):
        self.substring_start = position

    def add_suffix_link(self, node):
        self.suffix_link = node

    def __getitem__(self, first_char):
        """
        This method allows for easily getting children of self.

        E.G.
            say you have an STNode called node
            say node has a child that holds a substring (self.start, self.end) that begins with the letter 'a'
            then calling node['a'] will return that child
        """

        return self.children[ord(first_char)]

    def __setitem__(self, first_char, node):
        """
        This method allows for easily setting children of self.

        E.G.
            say you have an STNode called node
            then executing node['a'] = STNode(some_start, some_end) will create a child node
        """

        self.children[ord(first_char)] = node
        # Make the child's 'parent' attribute point to this node (self)
        node.parent = self
        # Since a child is added, self is no longer a leaf
        self.is_leaf = False

    def __str__(self, st_string=None, level=0):
        """
        When executing print(some_node),
        this method returns a string representation of self and all nodes below it (children of children of children... etc)
        """
        if st_string is None:
            return self.__repr__()

        tabs = "\t" * level
        first_char = "[R]"
        substring = ""

        # These booleans can be adjusted depending on what information you want to show in the string representation
        show_slink = True
        show_leaf_label = True
        show_text_reference = True

        # Initialise substrings
        slink_string = ""
        leaf_label = ""
        text_reference = ""

        # Organise substrings of what information to show per node
        if self.get_start() is not None:
            first_char = st_string[self.get_start()]
        if self.get_start() is not None and self.get_end() is not None:
            substring = ''.join(st_string[self.get_start():self.get_end()+1])
        if self.get_suffix_link() is not None and show_slink:
            slink_string = "-- SLINK --> " + str(hex(id(self.get_suffix_link())))
        if self.is_leaf and show_leaf_label:
            leaf_label = " LEAF LABEL=" + str(self.get_substring_start())
        if self.get_text_reference() is not None and show_text_reference:
            text_reference = " TEXT REF=" + str(self.get_text_reference())

        # String for a single node
        string = str(hex(id(self))) + "\t" + tabs + first_char + " : (" + str(self.get_start()) + ", " + str(self.get_end()) + ") " + substring + "\t\t" + leaf_label + "\t\t" + text_reference + "\t\t" + slink_string + "\n"

        # Recursively add node string representations to final string
        for child in self.get_children():
            if child is not None:
                string += child.__str__(st_string, level + 1)

        return string


class ModifiedSuffixTree:
    def __init__(self, texts, is_case_sensitive=True):
        """
        Ukkonens algorithm. Creates suffix tree in linear time.
        'texts' parameter is a list storing multiple texts
        """

        TERMINAL = '$'

        # self.string stores all texts separated by '$' symbols
        #   E.G. self.string = text1$text2$text3$...textN$
        # self.text_starting_points is a list storing the starting points of each text object within self.string
        self.string, self.text_starting_points = self.combine_texts_with_terminals(texts)

        # Set self.string to lowercase if we don't care about case sensitivity
        self.is_case_sensitive = is_case_sensitive
        if not self.is_case_sensitive:
            self.string = self.lowercase(self.string)

        # Creating implicitST_0
        self.root = STNode()
        first_char = self.string[0]
        self.root[first_char] = STNode(start=0, end=0)
        self.root[first_char].set_substring_start(0)
        curr_text_reference = 1
        self.root[first_char].set_text_reference(curr_text_reference)

        string_last_index = len(self.string) - 1

        # last_j_i will initially point to first character because the first GLOBAL_END.set_data(i + 1) statement
        # will automatically do the leaf extension for the first character
        last_j_i = 0

        # For i from 0 to 2nd last index of string:
        for i in range(0, string_last_index):
            # u will store the current node to add a suffix link from
            u = None
            # Debug
            print_debug("============================\nPHASE " + str(i) + " + 1 = " + str(i + 1) + ": " + ''.join(self.string[0:i+1]) + " + " + self.string[i+1] + "\n~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~")
            GLOBAL_END.set_data(i + 1)
            # If we've reached the start of a new text object, increment curr_text_reference
            if i > 0 and self.string[i - 1] == TERMINAL:
                curr_text_reference += 1

            # For j from last_j_i + 1 to i + 1:
            for j in range(last_j_i + 1, i + 2):
                # Debug
                print_debug("\tj = " + str(j))

                # last_node = the STNode that concludes the substring self.string[j...i]
                #   NOTE: if j == i + 1, then last_node is self.root if a node holding self.string[i + 1] is NOT hanging off root (otherwise, last_node is that node hanging off root)
                # ends_at_i = True if last_node ends at i
                # i_plus_1_char_match = True if an (i + 1)'th character is present in last_node AND matches self.string[i + 1]
                # i_plus_1_pos = position in last_node where the (i + 1)th character would be
                last_node, ends_at_i, i_plus_1_char_match, i_plus_1_pos = self.traverse(j, i)

                # If last_node ends at i'th character AND is a leaf: Apply RULE 1 (leaf extension)
                if ends_at_i and last_node.is_leaf:
                    self.leaf_extension(node=last_node, i=i)

                # Else if last_node ends at i and needs the (i + 1)th character to be added as a child OR j == i + 1 and needs the (i + 1)th character to be added as a child of root:
                # apply RULE 2 ALTERNATIVE (create leaf)
                elif (ends_at_i and not last_node.is_leaf and last_node[self.string[i + 1]] is None) or (j == i + 1 and last_node is self.root):
                    # u = internal node pointing to leaf (so we can suffix link it later)
                    u = self.create_leaf(node=last_node, j=j, i=i, u=u, curr_text_reference=curr_text_reference)

                # Else if last_node DOES NOT end at i and (i + 1)'th character in last_node is NOT string[i + 1]: Apply RULE 2 (create internal node)
                elif not ends_at_i and not i_plus_1_char_match:
                    # u = newly created internal node (so we can suffix link it later)
                    u = self.create_internal_node(node=last_node, j=j, i=i, i_plus_1_pos=i_plus_1_pos, u=u, curr_text_reference=curr_text_reference)

                # Else if string[j...i+1] is already in the suffix tree: Apply RULE 3 (no work needed)
                else:
                    if j == i + 1 and u is not None:
                        u.add_suffix_link(self.root)
                    elif not last_node.is_leaf and u is not None:
                        u.add_suffix_link(last_node)
                    # last_j_i = position BEFORE rule 3 was applied
                    last_j_i = j - 1
                    # Debug
                    if DEBUG:
                        print_debug(tab_across(self.__str__(), 2))
                    # Break out of inner loop. All future extensions in current phase does not require anymore work. Move onto next phase
                    break

                # last_j_i = last position where rule 1 or 2 occurred
                last_j_i = j
                # Debug
                if DEBUG:
                    print_debug(tab_across(self.__str__(), 2))

    def combine_texts_with_terminals(self, texts):
        """ Method to concatenate all text objects in 'texts' list, using "$" to separate each text object """

        TERMINAL = '$'
        combined_texts = []
        text_starting_points = [None for _ in texts]

        # Create combined_texts (text1$text2$text3$...textN)
        for i in range(len(texts)):
            if texts[i] is not None:
                combined_texts += texts[i]
                combined_texts.append(TERMINAL)

        # Create text_starting_points (list of starting position of each text object in combined_texts)
        for i in range(len(texts)):
            if i == 0 or i == 1:
                text_starting_points[i] = 0
            else:
                text_starting_points[i] = text_starting_points[i - 1] + len(texts[i - 1]) + 1

        return combined_texts, text_starting_points

    def lowercase(self, text):
        """ Lowercase all characters in text """

        # ascii_lowercase = all ASCII characters in order, all in lowercase form
        ascii_lowercase = [chr(i) for i in range(0, 64 + 1)]
        ascii_lowercase += ['a', 'b', 'c', 'd', 'e', 'f', 'g',
                            'h', 'i', 'j', 'k', 'l', 'm', 'n',
                            'o', 'p', 'q', 'r', 's', 't', 'u',
                            'v', 'w', 'x', 'y', 'z']
        ascii_lowercase += [chr(i) for i in range(91, 127 + 1)]

        # Lowercase all characters in text and return
        return [ascii_lowercase[ord(char)] for char in text]

    def get_root(self):
        return self.root

    def leaf_extension(self, node, i):
        """ RULE 1: Extends leaf node by the (i + 1)th character """

        node.set_start(i - (node.get_end() - node.get_start()))
        node.set_end(i + 1)

    def create_leaf(self, node, j, i, u, curr_text_reference):
        """ RULE 2 ALTERNATIVE: Creates new leaf holding self.string[i + 1], and attaches it to node as a child """

        # Suffix link u to node (node will be an internal node due to the leaf child we will attach later)
        if u is not None:
            u.add_suffix_link(node)

        # Create leaf for (i + 1)th character
        new_leaf = STNode(start=i+1, end=i+1)
        new_leaf.set_substring_start(j)
        new_leaf.set_text_reference(curr_text_reference)

        # Attach new_leaf to node
        new_char = self.string[i + 1]
        node[new_char] = new_leaf

        # Return internal node to suffix link it to another node later
        return node

    def create_internal_node(self, node, j, i, i_plus_1_pos, u, curr_text_reference):
        """ RULE 2: Create internal node between node and node.parent, and make this internal node hold the (i + 1)th character """

        # Create new internal node (with substring starting at node.start and ending before the (i + 1)th character)
        new_internal_node = STNode(start=node.get_start(), end=i_plus_1_pos - 1)
        node.parent[self.string[node.get_start()]] = new_internal_node

        # Connect new internal node to existing node
        node.set_start(i_plus_1_pos)
        new_internal_node[self.string[i_plus_1_pos]] = node

        # Add (i + 1)th leaf to new internal node AND create appropriate suffix link
        self.create_leaf(node=new_internal_node, j=j, i=i, u=u, curr_text_reference=curr_text_reference)

        # Return new internal node to suffix link it to another node later
        return new_internal_node

    def traverse(self, j, i):
        """
        Traverse suffix tree to find the node, where the substring self.string[j...i] ends.

        We return 4 objects...
            - last_node: the STNode that concludes the substring self.string[j...i]
                * NOTE: if j == i + 1, then last_node is self.root if a node holding self.string[i + 1] is NOT hanging off root (otherwise, last_node is that node hanging off root)
            - ends_at_i: Boolean object, True if last_node ends EXACTLY at i (not i + 1, or i + 2, or i + 3, etc...)
            - i_plus_1_char_match: Boolean object, True if an (i + 1)'th character is present in last_node AND matches self.string[i + 1]
            - i_plus_1_pos: position in last_node where the (i + 1)th character would be
        """

        # If j == i + 1, then we want to make sure the (i + 1)th character is hanging off root
        if j == i + 1:
            # If the (i + 1)th character is NOT hanging off root
            if self.root[self.string[i + 1]] is None:
                last_node = self.root
                i_plus_1_char_match = None
                i_plus_1_pos = None
            # Else if the (i + 1)th character IS hanging off root
            else:
                # last_node = (i + 1)th node (that is hanging off root)
                last_node = self.root[self.string[i + 1]]
                i_plus_1_char_match = True
                i_plus_1_pos = last_node.get_start()

            ends_at_i = False
            return last_node, ends_at_i, i_plus_1_char_match, i_plus_1_pos

        # If we've reached this point in the code, then we know j < i + 1
        substr_length = i - j + 1
        tree_substr_length = 0
        current_node = self.root

        # Keep traversing down the tree until we find the node ending the substring self.string[j...i]
        while tree_substr_length < substr_length:
            next_char = self.string[j + tree_substr_length]
            current_node = current_node[next_char]
            tree_substr_length += current_node.get_end() - current_node.get_start() + 1

        last_node = current_node
        ends_at_i = substr_length == tree_substr_length
        i_plus_1_pos = None
        i_plus_1_char_match = None

        if not ends_at_i:
            i_plus_1_pos = current_node.get_end() - (tree_substr_length - substr_length) + 1
            i_plus_1_char_match = self.string[i_plus_1_pos] == self.string[i + 1]

        return last_node, ends_at_i, i_plus_1_char_match, i_plus_1_pos

    def get_multiple_occ(self, patterns):
        """
        Given a list of patterns, return the following...
            pattern_nums: List of pattern numbers (can include duplicates) for each pattern occurrence
            text_nums: List of text numbers (can include duplicates) for each pattern occurrence
            position_nums: List of positions where patterns occur
        """

        pattern_nums = []
        text_nums = []
        position_nums = []

        # For each pattern
        for p in range(1, len(patterns)):
            # Check if we're pattern matching with or without case sensitivity
            if self.is_case_sensitive:
                # positions = list of positions where patterns[p] occurs
                # text_references = list of numbers referring to which text object patterns[p] occurs in
                positions, text_references = self.get_occurrences(patterns[p])
            else:
                # positions = list of positions where patterns[p] occurs
                # text_references = list of numbers referring to which text object patterns[p] occurs in
                positions, text_references = self.get_occurrences(self.lowercase(patterns[p]))
            # For each text object
            for i in range(len(text_references)):
                pattern_nums.append(p)
                text_nums.append(text_references[i])
                position_nums.append(positions[i])

        return pattern_nums, text_nums, position_nums

    def get_multiple_occ_str(self, patterns):
        """ Simply just gets the pattern numbers, text numbers and positions from self.get_multiple_occ(patterns) and returns a readable string """

        string = ''
        pattern_nums, text_nums, position_nums = self.get_multiple_occ(patterns)
        pattern_nums_length = len(pattern_nums)

        for i in range(pattern_nums_length):
            string += str(pattern_nums[i]) + ' ' + str(text_nums[i]) + ' ' + str(position_nums[i] + 1)
            if i <= pattern_nums_length - 2:
                string += '\n'

        return string

    def get_occurrences(self, pattern):
        """ Get positions of pattern occurrences for each text object """

        # Get node that concludes the substring: pattern
        pat_node = self._get_pattern_node(pattern)
        if pat_node is False:
            return [], []

        # positions = list of positions where pattern occurs in the texts
        # text_references = list of numbers referring to which text object a pattern was found in
        positions = []
        text_references = []
        self._get_leaf_labels(pat_node, positions, text_references)

        return positions, text_references

    def _get_pattern_node(self, pattern):
        """ Returns node that concludes the substring: pattern. If pattern does not exist in suffix tree: return False """

        pat_length = len(pattern)
        pat_last_index = pat_length - 1
        match_node = False
        node = self.root[pattern[0]]

        # If the first letter in pattern IS hanging off root...
        if node is not None:
            node_index = node.get_start()
        # Else if the first letter in pattern IS NOT hanging off root: return False
        else:
            return match_node

        # For each letter in pattern
        for i in range(pat_length):
            # If any character in pattern does not match: return False
            if self.string[node_index] != pattern[i]:
                return match_node
            # Else if a match was found: return node concluding the substring: pattern
            elif self.string[node_index] == pattern[i] and i == pat_last_index:
                return node

            # Move onto next position in the suffix tree path
            if node_index < node.get_end():
                node_index += 1
            else:
                node = node[pattern[i + 1]]
                # If the next character in patter appears in the suffix tree, move onto next iteration
                if node is not None:
                    node_index = node.get_start()
                # Else if any character in pattern does not match: return False
                else:
                    return match_node

    def _get_leaf_labels(self, node, positions, text_references):
        """
        Populates positions and text_references lists...
            positions = list of positions where pattern occurs in the texts
            text_references = list of numbers referring to which text object a pattern was found in
        """

        # Recursively do a depth first search, searching for all leaves connecting to node
        children = [child for child in node.get_children() if child is not None]
        for child in children:
            self._get_leaf_labels(child, positions, text_references)

        # If node is a leaf
        if node.is_leaf:
            # Add appropriate data to positions and text_references
            txt_ref = node.get_text_reference()
            text_references.append(txt_ref)
            positions.append(node.get_substring_start() - self.text_starting_points[txt_ref])

    def __str__(self):
        """ Return string representation of the suffix tree when print(...) is called """

        return self.root.__str__(self.string)


def print_debug(data):
    if DEBUG:
        print(data)


def tab_across(string, num_tabs):
    """ Indents all lines within string num_tabs times """

    new_string = [('\t' * num_tabs) + substring for substring in list(string.split('\n'))]
    new_string = '\n'.join(new_string)
    return new_string


def get_file_data(run_spec_file):
    """ Reads run specification file and returns texts and patterns as lists """

    with open(run_spec_file, 'r') as rsf:
        # lines = list of each line in run_spec_file
        lines = [line.strip() for line in rsf.readlines()]

        num_txt_files = int(lines[0])
        num_pat_files = int(lines[num_txt_files + 1])

        # Initialise texts and patterns using None values
        texts = [None for _ in range(num_txt_files + 1)]
        patterns = [None for _ in range(num_pat_files + 1)]

        # For each text file in run_spec_file
        for i in range(1, num_txt_files + 1):
            # Open text file i
            with open(lines[i].split()[1], 'r') as text_file:
                # Append text data to texts
                text_num = int(lines[i].split()[0])
                texts[text_num] = list(text_file.read())

        # For each pattern file in run_spec_file
        for i in range(num_txt_files + 2, num_txt_files + num_pat_files + 2):
            # Open pattern file i
            with open(lines[i].split()[1], 'r') as pat_file:
                # Append pattern data to patterns
                pat_num = int(lines[i].split()[0])
                patterns[pat_num] = list(pat_file.read())

    return texts, patterns


def write_output_file(filename, output):
    with open(filename, 'w') as f:
        f.write(output)
    print('WROTE TO FILE: \n' + output)


if __name__ == '__main__':
    # texts and patterns == lists of texts and patterns from run specification file
    texts, patterns = get_file_data(sys.argv[1])
    st = ModifiedSuffixTree(texts, is_case_sensitive=False)
    write_output_file('output_gst.txt', st.get_multiple_occ_str(patterns))


