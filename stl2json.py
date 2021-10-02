#!/usr/bin/env python3

import sys

whitespace = { ' ': 1, '\n': 1, '\r': 1, '\t': 1 }
UTF8 = "utf-8"

# grumble grumble
true = True
false = False
none = None

# eat white space
def eatWhitespace (content, offset):
    #print ("eatWhitespace: ", offset)
    while ((offset < len (content)) and (whitespace.get (content[offset], 0) > 0)):
        offset += 1
    #print ("- eatWhitespace:", offset)
    return offset

# return the next space delineated text token
def readToken (content, offset = 0):
    start = offset = eatWhitespace (content, offset)
    #print ("readToken: ", offset)
    while ((offset < len (content)) and (whitespace.get (content[offset], 0) == 0)):
        offset += 1
    #print ("-readToken:", offset)
    return (offset, content[start:offset])

# return a floating point number or none
def readFloat (content, offset):
    lastOffset = offset
    (offset, token) = readToken (content, offset)
    if (len (token) > 0):
        return (offset, float (token))
    return (offset, none)

# return true if an expected token was read
def expect (content, offset, expected):
    lastOffset = offset
    (offset, token) = readToken (content, offset)
    if (token == expected):
        print ("matched: ", token)
        return (offset, true)
    print ("failed to match token ({}) at {}".format (expected, offset))
    return (lastOffset, false)

# read a token from the compound, expect it in the content, the need for this
# indicates an amateur design of the file format
def expectCompound (content, offset, compound):
    lastOffset = offset
    (compoundOffset, token) = readToken (compound, 0)
    while (len (token) > 0):
        (offset, match) = expect (content, offset, token)
        if (not match):
            return (lastOffset, false)
        (compoundOffset, token) = readToken (compound, compoundOffset)
    return (offset, true)

# read three floating point numbers as part of a vector
def readVector (content, offset, expected):
    (offset, match) = expect (content, offset, expected)
    if (match):
        (offset, a) = readFloat (content, offset)
        (offset, b) = readFloat (content, offset)
        (offset, c) = readFloat (content, offset)
        return (offset, (a, b, c))
    return (offset, none)

# read a facet
def readFacet (content, offset):
    (offset, match) = expect (content, offset, "facet")
    if (match):
        # read a normal vector
        (offset, normal) = readVector (content, offset, "normal")
        (offset, match) = expectCompound (content, offset, "outer loop")
        if (match):
            vertices = []
            # read vertices until there are no more
            (offset, vertex) = readVector (content, offset, "vertex")
            while (vertex != none):
                vertices.append (vertex)
                (offset, vertex) = readVector (content, offset, "vertex")
            (offset, match) = expect (content, offset, "endloop")
            (offset, match) = expect (content, offset, "endfacet")
            return (offset, (normal, vertices))
    return (offset, none)

# read a solid, which consists of a bunch of facets
def readSolid (content, offset):
    (offset, match) = expect (content, offset, "solid")
    if (match):
        facets = []
        (offset, facet) = readFacet (content, offset)
        while (facet != none):
            facets.append (facet)
            (offset, facet) = readFacet (content, offset)
            print (".")
        (offset, match) = expect (content, offset, "endsolid")
    return (offset, none)

n = len(sys.argv)
if (n > 1):
    filename = sys.argv[1]
    print ("filename: {0}".format (filename))
    with open(filename, mode='rb') as file:
        content = file.read()

    # get the first few bytes to look for the word "solid"
    (offset, match) = expect (content[0:10].decode (UTF8), 0, "solid")
    if (match):
        print ("text format")

        # decode the whole string to make this easier
        content = content.decode (UTF8);

        # read the next token
        solids = []
        (offset, solid) = readSolid (content, 0)
        while (solid != none):
            solids.append (solid)
            (offset, solid) = readSolid (content, offset);

    else:
        print ("binary format")

print ("Done.")
