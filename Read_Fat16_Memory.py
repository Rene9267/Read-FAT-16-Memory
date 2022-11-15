
from struct import unpack
from tkinter import filedialog

filepath = filedialog.askopenfilename()

__FAT_size_index__ = 22
__FAT_copy_index__ = 16
__file_list_index__ = 0
__sector_size_index__ = 11
__root_directory_end__ = 17
__Directory_Entry_Size__ = 32
__reserved_sector_index__ = 14

File_Struct = {}


def BitMaskCalculator(value):
    match value:
        case (b'\x01',):
            return "READ_ONLY"
        case (b'\x02',):
            return "HIDDEN"
        case (b'\x04',):
            return "SYSTEM"
        case (b'\x08',):
            return "VOLUME_ID"
        case (b'\x10',):
            return "DIRECTORY"
        case (b'\x20',):
            return "ARCHIEVE"


def FileReader(__file_list_index__, Starting_point):
 # Read File
    __line_offset__ = 0
    while True:
        line = f[Starting_point +
                 __line_offset__:Starting_point+1+__line_offset__]
        first_Byte_line = ord(unpack('<c', line)[0])

        if first_Byte_line == 0:
            return __file_list_index__

        # Read Name
        Root_Directory_Starting_Offset = 8
        line = f[Starting_point+__line_offset__:Starting_point +
                 Root_Directory_Starting_Offset+__line_offset__]
        File_Struct["Name"+str(__file_list_index__)] = line

        # Read Type
        Root_Directory_Starting_Offset += 3
        line = f[Starting_point+__line_offset__ +
                 8:Starting_point+Root_Directory_Starting_Offset+__line_offset__]
        File_Struct["Type"+str(__file_list_index__)] = line

        # Read Attributes
        Root_Directory_Starting_Offset += 1
        line = f[Starting_point+__line_offset__ +
                 11:Starting_point+Root_Directory_Starting_Offset+__line_offset__]
        attribute_value = unpack('<c', line)
        File_Struct["Attribute" +
                    str(__file_list_index__)] = BitMaskCalculator(attribute_value)

        # Read Cluster Starting
        line = f[Starting_point+__line_offset__ +
                 26:Starting_point+__line_offset__+28]

        cluster_starting_line = unpack('<H', line)
        File_Struct["ClusterStart" +
                    str(__file_list_index__)] = cluster_starting_line[0]

        # File Dimension
        line = f[Starting_point+28 +
                 __line_offset__:Starting_point+32+__line_offset__]
        file_dimension_line = unpack('<2H', line)
        File_Struct["FileDimension" +
                    str(__file_list_index__)] = file_dimension_line[0]

        __line_offset__ += 32
        __file_list_index__ += 1


with open(filepath, 'rb') as G:
    f = G.read()

    # Reserved Sector calculation
    # 16 bits little endian at Index 14
    line = f[__reserved_sector_index__:__reserved_sector_index__+2]
    reserved_sector_line = unpack('<H', line)
    Reserved_Sector = reserved_sector_line[0]

    # Sector Size calculation
    # 16 bits little endian at Index 11
    line = f[__sector_size_index__:__sector_size_index__+2]
    sector_size_line = unpack('<H', line)
    Sector_Size = sector_size_line[0]

    # FAT Sector Starting
    Starting_FAT_Sector = Sector_Size * Reserved_Sector

    # FAT Size calculation
    # 16 bits little endian at Index 22
    line = f[__FAT_size_index__:__FAT_size_index__+2]
    FAT_size_line = unpack('<H', line)
    FAT_Size = FAT_size_line[0]

    # FAT Copies calculation
    # 8 bits little endian at index 16
    line = f[__FAT_copy_index__:__FAT_copy_index__+1]
    FAT_copy_line = unpack('<c', line)
    FAT_Copy = ord(FAT_copy_line[0])

    # Root Directory Starting
    Root_Directory_Starting = FAT_Size*FAT_Copy*Sector_Size+Starting_FAT_Sector

    # Root Directory Entries
    # 16 bits little endian at Index 22
    line = f[__root_directory_end__:__root_directory_end__+2]
    root_directory_entries_line = unpack('<H', line)
    Root_Directory_Entries = root_directory_entries_line[0]

    # Root Directory Size
    Root_Directory_Size = Root_Directory_Entries*__Directory_Entry_Size__
    Root_Directory_NSector = Root_Directory_Size/Sector_Size

    # Cluster Starting
    Cluster_Starting = Root_Directory_Starting + Root_Directory_Size

    __file_list_index__ = FileReader(
        __file_list_index__, Root_Directory_Starting)

    # Read Directory Files
    __file_list_index__ = FileReader(__file_list_index__, Cluster_Starting)

    __file_list_index__ = 0
    print("The Reserved Sector is "+str(Reserved_Sector) + "\n" + " ")
    print("The Sector Size is "+str(Sector_Size)+"\n" + " ")
    print("The FAT Sector start in "+str(Starting_FAT_Sector) +
          " / "+str(hex(Starting_FAT_Sector))+"\n" + " ")
    print("The FAT Size Size is "+str(FAT_Size)+"\n" + " ")
    print("The FAT Copy are "+str(FAT_Copy)+"\n" + " ")
    print("The Root Directory start in "+str(Root_Directory_Starting) +
          " / "+str(hex(Root_Directory_Starting))+"\n" + " ")
    print("The end of Root Directory entries is " +
          str(Root_Directory_Entries)+"\n" + " ")
    for x in File_Struct:

        if File_Struct.get("Name"+str(__file_list_index__)):
            print("\n" + " "+"The File Name is " +
                  str(File_Struct.get("Name"+str(__file_list_index__))))

        if File_Struct.get("Type"+str(__file_list_index__)):
            print("     The Extenstion is " +
                  str(File_Struct.get("Type"+str(__file_list_index__))))

        if File_Struct.get("Attribute" + str(__file_list_index__)):
            print("     The Attribue is " +
                  str(File_Struct.get("Attribute"+str(__file_list_index__))))

        if File_Struct.get("ClusterStart" + str(__file_list_index__)):
            print("     The Cluster of this file is the " +
                  str(File_Struct.get("ClusterStart"+str(__file_list_index__))))

        if File_Struct.get("FileDimension" + str(__file_list_index__)):
            print("     The File Dimension is the " +
                  str(File_Struct.get("FileDimension"+str(__file_list_index__))))

        __file_list_index__ += 1
