"""
Tools for reading and writing csv files

Created by adam on 6/22/18
"""
__author__ = 'adam'

import csv
import os


def makeDataFileIterator(folderPath, exclude=[]):
    """
    Returns an iterator of all files in the source directory
    so that each file has its path appended to it.

    Args:
        folderPath: The path to get file names from
        exclude: file names which should not be included in the output list

    """
    exclude = exclude if any(exclude) else ['.DS_Store']
    for root, dirs, files in os.walk(folderPath):
        for name in files:
            if name not in exclude:
                yield os.path.join(root, name)



def write_csv( csvFile, rowToWrite ):
    """TODO: let this figure out whether needs i, j or i"""
    with open( csvFile, 'a' ) as csvfile:
        writer = csv.writer( csvfile )
        # for i in toWrite:
        if type( rowToWrite ) is not list:
            rowToWrite = [ rowToWrite ]
        writer.writerow( rowToWrite )


#             for i, j in toWrite:
#                 writer.writerow([i, j])

def write_dict_to_csv( csvFile, toWrite ):
    """"Writes a mapping dictionary to a csv file """
    with open( csvFile, 'w' ) as csvfile:
        writer = csv.writer( csvfile )
        for k in toWrite.keys():
            for v in toWrite[ k ]:
                writer.writerow( [ k, v ] )


def read_csv_mapping( csvFile, firstColIsKey=True ):
    """Returns a dictionary mapping values in the first column to values in the second. That way
     the second column list of tuples for each row of the stored item

    Args:
        firstColIsKey (oboolean): Whether the first column in the file is to be used as keys
    """
    with open( csvFile ) as csvFile:
        reader = csv.reader( csvFile, quotechar='|' )
        out = { }
        for row in reader:
            if firstColIsKey:
                out[ row[ 0 ] ] = row[ 1 ]
            else:
                out[ row[ 1 ] ] = row[ 0 ]
        return out


def read_csv( csvFile ):
    """Returns a list of tuples for each row of the stored item"""
    with open( csvFile ) as csvFile:
        reader = csv.reader( csvFile, quotechar='|' )
        out = [ ]
        for row in reader:
            out.append( tuple( row ) )
        return out


def read_list( csvFile ):
    """Returns a list which has been stored as a csv file"""
    with open( csvFile ) as csvFile:
        reader = csv.reader( csvFile, quotechar='|' )
        out = [ ]
        for row in reader:
            out += row
        return out


def read_list_generator( csvFile ):
    """Returns a generator for items in a list which has been stored in a csv file"""
    results = read_list( csvFile )
    for r in results:
        yield r

# Get all subfolder paths


if __name__ == '__main__':
    pass
