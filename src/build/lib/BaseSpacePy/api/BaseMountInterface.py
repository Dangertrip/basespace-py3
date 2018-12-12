"""
class to wrap a directory mounted using BaseMount and provide convenience functions to get at the metadata stored there

The currently supported metadata extraction uses the files created by metaBSFS, but is limited to first class entities like projects and samples
it will fail (and throw an exception) when pointing at other directories. For some of these it's not really clear what the behaviour *should* be
eg. ~/BaseSpace/current_user/Projects/Sloths\ Test/Samples/
which is the owning directory for the "Sloths Test" samples. Should this be a directory of type "project" and id of the "Hyperion Test" project?
"""

import os
import json

REQUIRED_ENTRIES = set([ ".json", ".id", ".type" ])
PERMITTED_TYPES = set([ "sample", "project", "appsession" ])


class BaseMountInterfaceException(Exception):
    pass


class BaseMountInterface(object):
    def __init__(self, path):
        if path.endswith(os.sep):
            path = path[:-1]
        self.path = path
        self.id = None
        self.type = None
        self.name = os.path.basename(path)
        if not self.__validate_basemount__():
            raise BaseMountInterfaceException("Path: %s does not seem to be a BaseMount path" % self.path)
        self.__resolve_details__()

    def __validate_basemount__(self):
        """
        Checks whether the chosen directory is a BSFS directory
        """
        if os.path.isdir(self.path):
            for required in REQUIRED_ENTRIES:
                required_path = os.path.join(self.path, required)
                if not os.path.exists(required_path):
                    return False
        return True

    def __resolve_details__(self):
        """
        pull the useful details out of the . files generated by metaBSFS
        """
        if os.path.isdir(self.path):
            type_file = os.path.join(self.path, ".type")
            # the [:-1] is to strip of the trailing 's' that appears in types
            self.type = open(type_file).read().strip()[:-1]
        else:
            # this must mean the reference was to a file.
            # make sure it looks right!
            if "Files" not in self.path:
                raise BaseMountInterfaceException("Referring to a file not in the Files hierarchy!")
            self.type = "file"
        if self.type == "file":
            metadata_path = self.path.replace("Files", "Files.metadata")
            id_file = os.path.join(metadata_path, ".id")
        else:
            id_file = os.path.join(self.path, ".id")
        self.id = open(id_file).read().strip()

    def __str__(self):
        return "%s : (%s) : (%s)" % (self.path, self.id, self.type)

    def get_meta_data(self):
        try:
            with open(os.path.join(self.path, ".json")) as fh:
                md_str = fh.read()
                return json.loads(md_str)
        except IOError as e:
            raise BaseMountInterfaceException("could not read metadata file")
        except ValueError as e:
            raise BaseMountInterfaceException("could not parse json file")

"""
some test code; run:

python BaseMountInterface.py /path/mounted/by/basemount
to see some summary information
"""
if __name__ == "__main__":
    import sys
    path = sys.argv[1]
    mbi = BaseMountInterface(path)
    print(mbi)