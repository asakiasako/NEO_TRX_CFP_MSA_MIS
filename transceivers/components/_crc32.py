import sys
import math
import os
import struct

DEFAULT_CRC32_INIT_VALUE_OLD = 0x0   # i363
crc32_table_old =[ # i363 0x04c11db7L
		0x00000000, 0x04C11DB7, 0x09823B6E, 0x0D4326D9,
		0x130476DC, 0x17C56B6B, 0x1A864DB2, 0x1E475005,
		0x2608EDB8, 0x22C9F00F, 0x2F8AD6D6, 0x2B4BCB61,
		0x350C9B64, 0x31CD86D3, 0x3C8EA00A, 0x384FBDBD,
		0x4C11DB70, 0x48D0C6C7, 0x4593E01E, 0x4152FDA9,
		0x5F15ADAC, 0x5BD4B01B, 0x569796C2, 0x52568B75,
		0x6A1936C8, 0x6ED82B7F, 0x639B0DA6, 0x675A1011,
		0x791D4014, 0x7DDC5DA3, 0x709F7B7A, 0x745E66CD,
		0x9823B6E0, 0x9CE2AB57, 0x91A18D8E, 0x95609039,
		0x8B27C03C, 0x8FE6DD8B, 0x82A5FB52, 0x8664E6E5,
		0xBE2B5B58, 0xBAEA46EF, 0xB7A96036, 0xB3687D81,
		0xAD2F2D84, 0xA9EE3033, 0xA4AD16EA, 0xA06C0B5D,
		0xD4326D90, 0xD0F37027, 0xDDB056FE, 0xD9714B49,
		0xC7361B4C, 0xC3F706FB, 0xCEB42022, 0xCA753D95,
		0xF23A8028, 0xF6FB9D9F, 0xFBB8BB46, 0xFF79A6F1,
		0xE13EF6F4, 0xE5FFEB43, 0xE8BCCD9A, 0xEC7DD02D,
		0x34867077, 0x30476DC0, 0x3D044B19, 0x39C556AE,
		0x278206AB, 0x23431B1C, 0x2E003DC5, 0x2AC12072,
		0x128E9DCF, 0x164F8078, 0x1B0CA6A1, 0x1FCDBB16,
		0x018AEB13, 0x054BF6A4, 0x0808D07D, 0x0CC9CDCA,
		0x7897AB07, 0x7C56B6B0, 0x71159069, 0x75D48DDE,
		0x6B93DDDB, 0x6F52C06C, 0x6211E6B5, 0x66D0FB02,
		0x5E9F46BF, 0x5A5E5B08, 0x571D7DD1, 0x53DC6066,
		0x4D9B3063, 0x495A2DD4, 0x44190B0D, 0x40D816BA,
		0xACA5C697, 0xA864DB20, 0xA527FDF9, 0xA1E6E04E,
		0xBFA1B04B, 0xBB60ADFC, 0xB6238B25, 0xB2E29692,
		0x8AAD2B2F, 0x8E6C3698, 0x832F1041, 0x87EE0DF6,
		0x99A95DF3, 0x9D684044, 0x902B669D, 0x94EA7B2A,
		0xE0B41DE7, 0xE4750050, 0xE9362689, 0xEDF73B3E,
		0xF3B06B3B, 0xF771768C, 0xFA325055, 0xFEF34DE2,
		0xC6BCF05F, 0xC27DEDE8, 0xCF3ECB31, 0xCBFFD686,
		0xD5B88683, 0xD1799B34, 0xDC3ABDED, 0xD8FBA05A,
		0x690CE0EE, 0x6DCDFD59, 0x608EDB80, 0x644FC637,
		0x7A089632, 0x7EC98B85, 0x738AAD5C, 0x774BB0EB,
		0x4F040D56, 0x4BC510E1, 0x46863638, 0x42472B8F,
		0x5C007B8A, 0x58C1663D, 0x558240E4, 0x51435D53,
		0x251D3B9E, 0x21DC2629, 0x2C9F00F0, 0x285E1D47,
		0x36194D42, 0x32D850F5, 0x3F9B762C, 0x3B5A6B9B,
		0x0315D626, 0x07D4CB91, 0x0A97ED48, 0x0E56F0FF,
		0x1011A0FA, 0x14D0BD4D, 0x19939B94, 0x1D528623,
		0xF12F560E, 0xF5EE4BB9, 0xF8AD6D60, 0xFC6C70D7,
		0xE22B20D2, 0xE6EA3D65, 0xEBA91BBC, 0xEF68060B,
		0xD727BBB6, 0xD3E6A601, 0xDEA580D8, 0xDA649D6F,
		0xC423CD6A, 0xC0E2D0DD, 0xCDA1F604, 0xC960EBB3,
		0xBD3E8D7E, 0xB9FF90C9, 0xB4BCB610, 0xB07DABA7,
		0xAE3AFBA2, 0xAAFBE615, 0xA7B8C0CC, 0xA379DD7B,
		0x9B3660C6, 0x9FF77D71, 0x92B45BA8, 0x9675461F,
		0x8832161A, 0x8CF30BAD, 0x81B02D74, 0x857130C3,
		0x5D8A9099, 0x594B8D2E, 0x5408ABF7, 0x50C9B640,
		0x4E8EE645, 0x4A4FFBF2, 0x470CDD2B, 0x43CDC09C,
		0x7B827D21, 0x7F436096, 0x7200464F, 0x76C15BF8,
		0x68860BFD, 0x6C47164A, 0x61043093, 0x65C52D24,
		0x119B4BE9, 0x155A565E, 0x18197087, 0x1CD86D30,
		0x029F3D35, 0x065E2082, 0x0B1D065B, 0x0FDC1BEC,
		0x3793A651, 0x3352BBE6, 0x3E119D3F, 0x3AD08088,
		0x2497D08D, 0x2056CD3A, 0x2D15EBE3, 0x29D4F654,
		0xC5A92679, 0xC1683BCE, 0xCC2B1D17, 0xC8EA00A0,
		0xD6AD50A5, 0xD26C4D12, 0xDF2F6BCB, 0xDBEE767C,
		0xE3A1CBC1, 0xE760D676, 0xEA23F0AF, 0xEEE2ED18,
		0xF0A5BD1D, 0xF464A0AA, 0xF9278673, 0xFDE69BC4,
		0x89B8FD09, 0x8D79E0BE, 0x803AC667, 0x84FBDBD0,
		0x9ABC8BD5, 0x9E7D9662, 0x933EB0BB, 0x97FFAD0C,
		0xAFB010B1, 0xAB710D06, 0xA6322BDF, 0xA2F33668,
		0xBCB4666D, 0xB8757BDA, 0xB5365D03, 0xB1F740B4]

DEFAULT_CRC32_INIT_VALUE = 0xffffffff
crc32_table = [ #zte 0xEDB88320
	0x00000000,  0xedb88320 , 0x36c98560 , 0xdb710640 , 0x6d930ac0 , 0x802b89e0 , 0x5b5a8fa0 , 0xb6e20c80,
	0xdb261580 , 0x369e96a0 , 0xedef90e0 , 0x5713c0 , 0xb6b51f40 , 0x5b0d9c60 , 0x807c9a20 , 0x6dc41900,
	0x5bf4a820 , 0xb64c2b00 , 0x6d3d2d40 , 0x8085ae60 , 0x3667a2e0 , 0xdbdf21c0 , 0xae2780 , 0xed16a4a0,
	0x80d2bda0 , 0x6d6a3e80 , 0xb61b38c0 , 0x5ba3bbe0 , 0xed41b760 , 0xf93440 , 0xdb883200 , 0x3630b120,
	0xb7e95040 , 0x5a51d360 , 0x8120d520 , 0x6c985600 , 0xda7a5a80 , 0x37c2d9a0 , 0xecb3dfe0 , 0x10b5cc0,
	0x6ccf45c0 , 0x8177c6e0 , 0x5a06c0a0 , 0xb7be4380 , 0x15c4f00 , 0xece4cc20 , 0x3795ca60 , 0xda2d4940,
	0xec1df860 , 0x1a57b40 , 0xdad47d00 , 0x376cfe20 , 0x818ef2a0 , 0x6c367180 , 0xb74777c0 , 0x5afff4e0,
	0x373bede0 , 0xda836ec0 , 0x1f26880 , 0xec4aeba0 , 0x5aa8e720 , 0xb7106400 , 0x6c616240 , 0x81d9e160,
	0x826a23a0 , 0x6fd2a080 , 0xb4a3a6c0 , 0x591b25e0 , 0xeff92960 , 0x241aa40 , 0xd930ac00 , 0x34882f20,
	0x594c3620 , 0xb4f4b500 , 0x6f85b340 , 0x823d3060 , 0x34df3ce0 , 0xd967bfc0 , 0x216b980 , 0xefae3aa0,
	0xd99e8b80 , 0x342608a0 , 0xef570ee0 , 0x2ef8dc0 , 0xb40d8140 , 0x59b50260 , 0x82c40420 , 0x6f7c8700,
	0x2b89e00 , 0xef001d20 , 0x34711b60 , 0xd9c99840 , 0x6f2b94c0 , 0x829317e0 , 0x59e211a0 , 0xb45a9280,
	0x358373e0 , 0xd83bf0c0 , 0x34af680 , 0xeef275a0 , 0x58107920 , 0xb5a8fa00 , 0x6ed9fc40 , 0x83617f60,
	0xeea56660 , 0x31de540 , 0xd86ce300 , 0x35d46020 , 0x83366ca0 , 0x6e8eef80 , 0xb5ffe9c0 , 0x58476ae0,
	0x6e77dbc0 , 0x83cf58e0 , 0x58be5ea0 , 0xb506dd80 , 0x3e4d100 , 0xee5c5220 , 0x352d5460 , 0xd895d740,
	0xb551ce40 , 0x58e94d60 , 0x83984b20 , 0x6e20c800 , 0xd8c2c480 , 0x357a47a0 , 0xee0b41e0 , 0x3b3c2c0,
	0xe96cc460 , 0x4d44740 , 0xdfa54100 , 0x321dc220 , 0x84ffcea0 , 0x69474d80 , 0xb2364bc0 , 0x5f8ec8e0,
	0x324ad1e0 , 0xdff252c0 , 0x4835480 , 0xe93bd7a0 , 0x5fd9db20 , 0xb2615800 , 0x69105e40 , 0x84a8dd60,
	0xb2986c40 , 0x5f20ef60 , 0x8451e920 , 0x69e96a00 , 0xdf0b6680 , 0x32b3e5a0 , 0xe9c2e3e0 , 0x47a60c0,
	0x69be79c0 , 0x8406fae0 , 0x5f77fca0 , 0xb2cf7f80 , 0x42d7300 , 0xe995f020 , 0x32e4f660 , 0xdf5c7540,
	0x5e859420 , 0xb33d1700 , 0x684c1140 , 0x85f49260 , 0x33169ee0 , 0xdeae1dc0 , 0x5df1b80 , 0xe86798a0,
	0x85a381a0 , 0x681b0280 , 0xb36a04c0 , 0x5ed287e0 , 0xe8308b60 , 0x5880840 , 0xdef90e00 , 0x33418d20,
	0x5713c00 , 0xe8c9bf20 , 0x33b8b960 , 0xde003a40 , 0x68e236c0 , 0x855ab5e0 , 0x5e2bb3a0 , 0xb3933080,
	0xde572980 , 0x33efaaa0 , 0xe89eace0 , 0x5262fc0 , 0xb3c42340 , 0x5e7ca060 , 0x850da620 , 0x68b52500,
	0x6b06e7c0 , 0x86be64e0 , 0x5dcf62a0 , 0xb077e180 , 0x695ed00 , 0xeb2d6e20 , 0x305c6860 , 0xdde4eb40,
	0xb020f240 , 0x5d987160 , 0x86e97720 , 0x6b51f400 , 0xddb3f880 , 0x300b7ba0 , 0xeb7a7de0 , 0x6c2fec0,
	0x30f24fe0 , 0xdd4accc0 , 0x63bca80 , 0xeb8349a0 , 0x5d614520 , 0xb0d9c600 , 0x6ba8c040 , 0x86104360,
	0xebd45a60 , 0x66cd940 , 0xdd1ddf00 , 0x30a55c20 , 0x864750a0 , 0x6bffd380 , 0xb08ed5c0 , 0x5d3656e0,
	0xdcefb780 , 0x315734a0 , 0xea2632e0 , 0x79eb1c0 , 0xb17cbd40 , 0x5cc43e60 , 0x87b53820 , 0x6a0dbb00,
	0x7c9a200 , 0xea712120 , 0x31002760 , 0xdcb8a440 , 0x6a5aa8c0 , 0x87e22be0 , 0x5c932da0 , 0xb12bae80,
	0x871b1fa0 , 0x6aa39c80 , 0xb1d29ac0 , 0x5c6a19e0 , 0xea881560 , 0x7309640 , 0xdc419000 , 0x31f91320,
	0x5c3d0a20 , 0xb1858900 , 0x6af48f40 , 0x874c0c60 , 0x31ae00e0 , 0xdc1683c0 , 0x7678580 , 0xeadf06a0	
]

def CRC32_old(crc_accum, crcDataBuf, crcCount):
    j = 0
    i = 0
    buf = crcDataBuf
    count = crcCount
    crc_accum = (~crc_accum) & 0xffffffff
    while j < crcCount:
        i = (((crc_accum & 0xFFFFFFFF)>> 24) ^ (crcDataBuf[j]) & 0xFF)
        crc_accum = ((crc_accum << 8) & 0xFFFFFFFF) ^ crc32_table_old[i]
        crc_accum &= 0xFFFFFFFF
        j += 1
    return (~crc_accum) & 0xffffffff

def CRC32(crc_accum, crcDataBuf, crcCount):
    j = 0
    i = 0
    buf = crcDataBuf
    count = crcCount
    crc_accum = (~crc_accum) & 0xffffffff
    while j < crcCount:
        i = (((crc_accum & 0xFFFFFFFF)>> 24) ^ (crcDataBuf[j]) & 0xFF)
        crc_accum = ((crc_accum << 8) & 0xFFFFFFFF) ^ crc32_table[i]
        crc_accum &= 0xFFFFFFFF
        j += 1
    return (~crc_accum) & 0xffffffff

def CRC32_file(filename):
    with open(filename, 'rb') as f:
        buf = f.read()
        return CRC32(DEFAULT_CRC32_INIT_VALUE, buf, len(buf))
    
def insertCrc32Ahead(str):
    # insert crc32 ahead by little byte order
    crc32 = CRC32(DEFAULT_CRC32_INIT_VALUE, str, len(str))        
    str.insert(0, (crc32) >> 24 & 0xff)
    str.insert(0, (crc32) >> 16 & 0xff)
    str.insert(0, (crc32) >> 8 & 0xff)        
    str.insert(0, (crc32) & 0xff)        
    print('crc32={:x}'.format(crc32))
    return str
        
def appendCrc32(str):
    # append crc32 ahead by little byte order
	crc32 = CRC32(DEFAULT_CRC32_INIT_VALUE, str, len(str))   
	str.extend(struct.pack('<I', crc32))        
	return str
