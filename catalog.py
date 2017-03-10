import numpy as np

class Catalog(object):
    @staticmethod
    def fromFilename(filename, comments = '#', header_line = 1, skiprows = 0, 
                     usecols = None, debug = False, skip_index = True,
                     **kwargs):
        f = open(filename, 'r')
        def dbp(line):
            if debug:
                print line
        if header_line < 0:
            # this means the last of the commented lines + header_line
            lines = f.readlines()
            linenum = skiprows
            line = lines[linenum].strip()
            while (len(line) == 0 or line.startswith(comments)):
                linenum += 1
                line = lines[linenum].strip()
            header_line += linenum
            header = lines[header_line].strip()
        else:
            linenum = 1
            while linenum <= skiprows + header_line:
                header = f.readline().strip()
                linenum += 1
        f.close()

        # condition the header correctly to get a list of columns
        dbp("Found header: '{}'".format(header))
        header = header.strip(comments) # header can be a comment
        dbp("Header after stripping comment chars: '{}'".format(header))
        header = header.split(comments)[0] # drop comment from the end
        header = header.lower()
        dbp("Header after stripping: '{!s}'".format(header))
        columns = header.split()
        dbp("I found these column headers:")
        dbp(columns)

        # get the correct columns, and do some error checking
        if skip_index:
            if 'index' in columns:
                ind = columns.index('index')
                usecols = range(len(columns))
                usecols.pop(ind)
                dbp("I found an index column; removing it")
        columns = np.array(columns)
        if usecols is not None:
            columns = columns[usecols]
            dbp("Using only these columns:")
            dbp(columns)
        unique_cols = np.unique(columns)
        for c in columns:
            if c not in unique_cols:
                raise ValueError("I got more than one column named {}".format(c))

        kwargs['unpack'] = True # we always have data arranged in columns
        kwargs['skiprows'] = skiprows + header_line
        kwargs['usecols'] = usecols
        kwargs['comments'] = comments
        data = np.loadtxt(filename, **kwargs)

        if len(columns) != len(data):
            raise ValueError("I got {} column headers and {} columns!".format(len(columns), len(data)))
        data_dict = {}
        for i, data_col in enumerate(data):
            if columns[i] == 'ra':
                ra = data_col
                continue
            if columns[i] == 'dec':
                dec = data_col
                continue
            assert not data_dict.has_key(columns[i])
            data_dict[columns[i]] = data_col
        dbp("Creating a catalog with the following extra columns:")
        dbp(data_dict.keys())
        return Catalog(ra, dec, **data_dict)

    @staticmethod
    def _wrap(ra):
        # force an angle to be between 0 and 180
        if abs(ra) > 180:
            if ra > 0:
                return ra - 180
            else:
                return ra + 180
        return ra
    
    @staticmethod
    def _greatCircleDist(ra1, dec1, ra2, dec2):
        ra1 = np.deg2rad(ra1)
        dec1 = np.deg2rad(dec1)
        ra2 = np.deg2rad(ra2)
        dec2 = np.deg2rad(dec2)
        return np.rad2deg(np.arccos(np.sin(dec1) * np.sin(dec2) + np.cos(dec1) * np.cos(dec2) * np.cos(abs(ra1 - ra2))))

    def __init__(self, ra, dec, **kwargs):
        if np.shape(ra) != np.shape(dec):
            raise ValueError("ra and dec must have the same length")
        self._forceSetAttr('ra', ra)
        self._forceSetAttr('dec', dec)
        self._forceSetAttr('extra_keys', {})
        for key, value in kwargs.iteritems():
            self.__setattr__(key, value)
            
    def __setattr__(self, name, value):
        if not isinstance(value, (type(list()), type(np.array([])))):
            # handle non-array-likes by just putting them in 
            self.__dict__[name] = value
            self.extra_keys[name] = False
            return
        if np.shape(value) != np.shape(self.ra):
            raise ValueError("{} must have the same length as ra".format(key))
        self.extra_keys[name] = True
        self.__dict__[name] = value

    def _forceSetAttr(self, name, value):
        # allows values to be set without storing them in extra_keys
        # or any error checking.
        self.__dict__[name] = value

    def __delattr__(self, name):
        self.extra_keys.remove(name)
        self.__dict__.pop(name)
        
    def __getitem__(self, cut):
        new_dict = {}
        for key, isarray in self.extra_keys.iteritems():
            if isarray:
                new_dict[key] = self.__getattribute__(key)[cut]
            else:
                new_dict[key] = self.__getattribute__(key)
        return type(self)(self.ra[cut], self.dec[cut], **new_dict)

    def findNearest(self, ra, dec):
        '''
        Find the object nearest to (RA, dec).
        returns the index of the nearest object, and the distance
        '''
        mindist = 181
        i = 0
        for sra, sdec in zip(self.ra, self.dec):
            dist = self._greatCircleDist(ra, dec, sra, sdec)
            if dist < mindist:
                closest = i
                mindist = dist
            i += 1
        return closest, mindist

    def compare(self, other, threshold = None):
        matches = np.zeros(len(self.ra))
        distances = np.zeros(len(self.ra))
        for i, (ra, dec) in enumerate(zip(self.ra, self.dec)):
            closest, dist = other.findNearest(ra, dec)
            matches[i] = closest
            distances[i] = dist
        return matches, distances

    def toDS9(self, filename, include = None, index = True):
        if include is not None:
            # create a new version with only the fields we want, then run
            # its toDS9 method
            new = type(self)(ra, dec)
            for key in include:
                new.__setattr__(key, self.key)
            new.toDS9(filename, include = None)
            return
        f = open(filename, 'w')
        if index:
            f.write("\t".join(["index", "ra", "dec"]))
            f.write("\t")
        else:
            f.write("\t".join(["ra", "dec"]))
        f.write("\t".join(self.extra_keys.keys()))
        f.write("\n")
        for i, (ra, dec) in enumerate(zip(self.ra, self.dec)):
            if index:
                f.write("\t".join(["{index}", "{ra}", 
                                   "{dec}"]).format(index = i, 
                                                    ra = self.ra[i], 
                                                    dec = self.dec[i]))
            else:
                f.write("\t".join(["{ra}", "{dec}"]).format(ra = self.ra[i], 
                                                            dec = self.dec[i]))
            for key, isarray in self.extra_keys.iteritems():
                if isarray:
                    f.write("\t{}".format(self.__getattribute__(key)[i]))
                else:
                    f.write("\t{}".format(self.__getattribute__(key)))
            f.write("\n")
