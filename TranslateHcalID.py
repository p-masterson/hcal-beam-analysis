

class DetectorID(object):   #ADDED OBJECT
    subdetectorid_mask = 0x3F
    subdetectorid_shift = 26
    subdetectorid_payload_mask = 0x3FFFFFFF
    def __init__(self, SDtype, subpayload):
        self.ID = ((SDtype & DetectorID.subdetectorid_mask) <<
                   DetectorID.subdetectorid_shift) |\
                   (subpayload & DetectorID.subdetectorid_payload_mask)


class HcalAbstractID(DetectorID):
    SD_HCAL = 6
    EID_HCAL = 19
    hcal_payload_mask = 0x007FFFFF
    bar_type_shift = 23
    bar_type_mask = 0x7
    bar_type_global = 0
    bar_type_digi = 1

    def __init__(self, bar_type, payload):
        super(HcalAbstractID, self).__init__(HcalAbstractID.SD_HCAL, 0)
        # cls.defaultID(HcalID.SD_HCAL, 0)
        self.ID |= (bar_type & HcalAbstractID.bar_type_mask) << \
            HcalAbstractID.bar_type_shift
        self.ID |= (payload & HcalAbstractID.hcal_payload_mask)


def layer_valid(layer):
    if (layer > 19 or layer < 0):
        print("Error: Layer number greater than 19 or less than 0 which is not valid for the prototype")
        return False
    if (layer == 0):
        print("Error: Layer numbers start from 1 not 0")
        return False
    return True
def section_valid(section):
    if (section != 0):
        print("Error: HcalID for prototype with Section number != 0 (Back Hcal)")
def bar_valid(layer,bar):
    if (layer > 9 and bar > 8):
        print("Error: Bar in front region with more than 8 bars")
    if (bar > 12 or bar < 0):
        print("Error: Bar number is greater than 12 or less than 0")
def end_valid(end):
    if (end < 0 or end > 1):
        print("End is not 0 or 1")
        return False
    return True

def pieces_valid(section, layer, bar, end=0):
    return section_valid(section) and layer_valid(layer) and bar_valid(bar) and end_valid(end)

class HcalID(HcalAbstractID):
    section_mask = 0x7
    section_shift = 18
    layer_mask = 0xFF
    layer_shift = 10
    bar_mask = 0xFF
    bar_shift = 0

    def __str__(self):
        return "HcalID({},{},{})".format(self.section(),
                                         self.layer(),
                                         self.bar())

    def __repr__(self):
        return self.__str__()

    def __init__(self):
        super(HcalID, self).__init__(HcalAbstractID.bar_type_global, 0)

    def from_vars(self, section, layer, bar):
        pieces_valid(section, layer, bar)
        self.ID |= (section & HcalID.section_mask) << HcalID.section_shift
        self.ID |= (layer & HcalID.layer_mask) << HcalID.layer_shift
        self.ID |= (bar & HcalID.bar_mask) << HcalID.bar_shift
        return self

    def pieces(self):
        return self.section(), self.layer(), self.bar()

    def from_ID(self, ID):
        self.ID = ID
        return self

    def section(self):
        return (self.ID >> HcalID.section_shift) & HcalID.section_mask

    def layer(self):
        return (self.ID >> HcalID.layer_shift) & HcalID.layer_mask

    def bar(self):
        return (self.ID >> HcalID.bar_shift) & HcalID.bar_mask


class HcalDigiID(HcalAbstractID):
    end_mask = 0x1
    end_shift = 19
    section_mask = 0x7
    section_shift = 16
    layer_mask = 0xFF
    layer_shift = 8
    bar_mask = 0xFF
    bar_shift = 0

    def __init__(self):
        super(HcalDigiID, self).__init__(HcalAbstractID.bar_type_digi, 0)

    def from_vars(self, section, layer, bar, end):
        pieces_valid(section, layer, bar, end)
        self.ID |= (section & HcalDigiID.section_mask) << \
            HcalDigiID.section_shift
        self.ID |= (layer & HcalDigiID.layer_mask) << HcalDigiID.layer_shift
        self.ID |= (bar & HcalDigiID.bar_mask) << HcalDigiID.bar_shift
        self.ID |= (end & HcalDigiID.end_mask) << HcalDigiID.end_shift
        return self

    def section(self):
        return (self.ID >> HcalDigiID.section_shift) & HcalDigiID.section_mask

    def layer(self):
        return (self.ID >> HcalDigiID.layer_shift) & HcalDigiID.layer_mask

    def bar(self):
        return (self.ID >> HcalDigiID.bar_shift) & HcalDigiID.bar_mask

    def end(self):
        return (self.ID >> HcalDigiID.end_shift) & HcalDigiID.end_mask

    def pieces(self):
        return self.section(), self.layer(), self.bar(), self.end()

    def from_ID(self, ID):
        self.ID = ID
        return self

    def is_negative_end(self):
        return self.end() == 1

    def __str__(self):
        return "HcalDigiID({},{},{},{})".format(self.section(),
                                                self.layer(),
                                                self.bar(),
                                                self.end())

    def __repr__(self):
        return self.__str__()


def bar_to_pos(layer, bar):
    shifted_bar = -6 + bar if layer > 9 else -4 + bar
    # print(shifted_bar)
    return shifted_bar

# HcalID(0,14,0)
# HcalID(0,12,1)
# HcalID(0,16,2)
# HcalID(0,13,3)
# HcalID(0,14,4)
# HcalID(0,11,5)
# HcalID(0,11,6)
# HcalID(0,13,7)
# HcalID(0,10,5)
# HcalID(0,12,5)
# HcalID(0,12,6)
# HcalID(0,14,3)
# HcalID(0,13,4)
# HcalID(0,11,4)
# HcalID(0,11,7)
# HcalID(0,10,6)
# HcalID(0,11,11)
# HcalID(0,15,11)
# HcalID(0,16,4)
# HcalID(0,8,4)
# HcalID(0,9,7)
# HcalID(0,14,2)
# HcalID(0,14,5)
# HcalID(0,14,7)
