import os

class FoamCase:

    def __init__(self, path):
        self.path = path
        self.name = os.path.split(path)[1]

    '''
    Find a file that matches the name passed to the function
    From: https://stackoverflow.com/questions/1724693/find-a-file-in-python#1724723
    '''
    def find(self, name):
        # TODO: Add wildcards
        for root, subFolders, files in os.walk(self.path):
            if name in files:
                return os.path.join(root, name)

    '''
    Find all files that match the name passed to the function
    From: https://stackoverflow.com/questions/1724693/find-a-file-in-python#1724723
    '''
    def findAll(self, name):
        # TODO: Add wildcards
        found_files = []
        for root, subFolders, files in os.walk(self.path):
            if name in files:
                found_files.append(os.path.join(root, name))

        return found_files

    '''
    Search for a property and return its value
    example: lookUp('turbulenceProperties', 'RASModel') should return kEpsilon, lienCubic etc..
    '''
    def lookUp(self, fileName, propertyName):
        with open(self.find(fileName)) as f:
            for line in f:
                if propertyName in line:
                    propertyValue = line.split()[1].strip(';')
                    return propertyValue

    '''
    Look up all force.dat files
    If there are multiple force.dat files, concatenate and sort
    '''
    def findForceData(self):

        forceTimes = self.findAll('force.dat')

        df = pd.DataFrame()

        for time in forceTimes:
            df = df.append(self.readForceData(time))

        df.sort_index()

        return df

    '''
    Read .dat file from a given path
    Returns pandas DataFrame
    '''
    def readForceData(self, forcePath):
        # Read force data from .dat file.
        # TODO: Rewrite this function to work without sed stuff

        assert os.path.exists(forcePath)

        tmpFile = '/tmp/force.dat'

        # Call stream line editor to remove brackets
        call(["sed", "s/[\(\)]//g ", forcePath], stdout=open(tmpFile, 'w'))

        # Clear header, extract columns
        with open(tmpFile) as f:
            for x in range(4):
                line = f.readline()

        cols = line.split()

        # Read into pandas
        dataFrame = pd.read_csv(filepath_or_buffer=tmpFile, sep='\s+', index_col=0, header=4, names=cols[1:])

        os.remove(tmpFile)

        # Select only total force columns divide by 1/2 to turn nondimensional
        # Edit: this is because c_F = F / (0.5 * rho * L**2)
        # In our simulations we assume rho = 1 and L = 1
        # This needs to be adjusted for dimensionalised simulations
        tmp_data = dataFrame[['total_x', 'total_y', 'total_z']]

        # Rename to comply with SNAME convention
        clean_data = tmp_data.rename(columns={'total_x':'Fx', 'total_y':'Fy', 'total_z':'Fz'})

        return clean_data
